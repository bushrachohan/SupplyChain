"""
core/forecasting.py
SKU-level demand forecasting for SupplyChain Sentinel AI.
Uses LightGBM with time-based features. Follows ML engineering rules:
- Time-based train/val/test split (no shuffling)
- No data leakage
- Mandatory baseline comparison (naive forecast)
- Reports MAPE and RMSE on test split only
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Any, Optional
import lightgbm as lgb

from ml.evaluation import (
    time_based_split,
    check_no_date_leakage,
    regression_metrics,
    naive_forecast_baseline,
    compare_to_baseline,
)


# ---------------------------------------------------------------------------
# 1. Feature Engineering
# ---------------------------------------------------------------------------

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build time-based features from historical demand data.
    Input df must have columns: sku_id, date, quantity_demanded, location_id.
    All features use only past information — no future leakage.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["sku_id", "date"]).reset_index(drop=True)

    # Calendar features
    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)

    # Lag features (per SKU) — strictly past values only
    for lag in [1, 7, 14]:
        df[f"lag_{lag}"] = (
            df.groupby("sku_id")["quantity_demanded"]
            .shift(lag)
        )

    # Rolling mean features (per SKU) — shift(1) ensures no leakage
    for window in [7, 14]:
        df[f"rolling_mean_{window}"] = (
            df.groupby("sku_id")["quantity_demanded"]
            .shift(1)
            .rolling(window)
            .mean()
            .reset_index(level=0, drop=True)
        )

    # Location encoding
    df["location_encoded"] = df["location_id"].astype("category").cat.codes

    # Drop rows where lags produced NaN (first N rows per SKU)
    df = df.dropna().reset_index(drop=True)

    return df


# ---------------------------------------------------------------------------
# 2. Train / Evaluate
# ---------------------------------------------------------------------------

FEATURE_COLS = [
    "day_of_week", "day_of_month", "month", "week_of_year",
    "lag_1", "lag_7", "lag_14",
    "rolling_mean_7", "rolling_mean_14",
    "location_encoded",
]
TARGET_COL = "quantity_demanded"


def train_forecast_model(
    df: pd.DataFrame,
) -> Tuple[lgb.LGBMRegressor, Dict[str, float], Dict[str, float]]:
    """
    Train a LightGBM demand forecasting model on historical demand data.
    Applies time-based split, leakage check, trains on train+val,
    evaluates on test, and compares against naive baseline.

    Args:
        df: Raw historical demand DataFrame with columns:
            sku_id, date, quantity_demanded, location_id

    Returns:
        (model, test_metrics, baseline_metrics)
        - model: trained LGBMRegressor
        - test_metrics: {'mape': float, 'rmse': float} on test split
        - baseline_metrics: same keys for naive baseline
    """
    featured_df = build_features(df)

    # Time-based split
    train_df, val_df, test_df = time_based_split(featured_df, date_col="date")

    # Remove boundary date overlaps caused by multiple SKUs sharing the same date
    train_dates = set(train_df["date"])
    val_dates = set(val_df["date"])
    val_df = val_df[~val_df["date"].isin(train_dates)]
    test_df = test_df[~test_df["date"].isin(val_dates | train_dates)]

    # Leakage check
    check_no_date_leakage(train_df, val_df, test_df, date_col="date")
    
    # Combine train + val for final training (test remains untouched)
    train_full = pd.concat([train_df, val_df], ignore_index=True)

    X_train = train_full[FEATURE_COLS]
    y_train = train_full[TARGET_COL].values
    X_test = test_df[FEATURE_COLS]
    y_test = test_df[TARGET_COL].values

    # Train LightGBM
    model = lgb.LGBMRegressor(
        n_estimators=200,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
        verbose=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    test_metrics = regression_metrics(y_test, y_pred)

    # Naive baseline: predict previous day's demand
    y_baseline = naive_forecast_baseline(y_test)
    baseline_metrics = regression_metrics(y_test, y_baseline)

    return model, test_metrics, baseline_metrics


# ---------------------------------------------------------------------------
# 3. Predict
# ---------------------------------------------------------------------------

def predict_demand(
    model: lgb.LGBMRegressor,
    df: pd.DataFrame,
    sku_id: str,
) -> pd.DataFrame:
    """
    Generate demand predictions for a specific SKU using a trained model.

    Args:
        model: Trained LGBMRegressor from train_forecast_model().
        df:    Full historical demand DataFrame (needed for feature engineering).
        sku_id: The SKU to generate predictions for.

    Returns:
        DataFrame with columns: date, sku_id, predicted_demand
        (rows correspond to the test split for that SKU)
    """
    featured_df = build_features(df)
    sku_df = featured_df[featured_df["sku_id"] == sku_id].copy()

    if sku_df.empty:
        raise ValueError(f"No data found for sku_id='{sku_id}'")

    _, _, test_df = time_based_split(sku_df, date_col="date")

    if test_df.empty:
        raise ValueError(f"Test split is empty for sku_id='{sku_id}'")

    X_test = test_df[FEATURE_COLS]
    preds = model.predict(X_test)

    result = test_df[["date", "sku_id"]].copy()
    result["predicted_demand"] = np.round(preds, 2)
    return result.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 4. Forecast vs Actual Comparison
# ---------------------------------------------------------------------------

def get_forecast_vs_actual(
    model: lgb.LGBMRegressor,
    df: pd.DataFrame,
    sku_id: str,
) -> Dict[str, Any]:
    """
    Produce aligned historical actuals and forecast predictions for a SKU.
    Reuses existing predict_demand output and df historical demand.

    Args:
        model: Trained LGBMRegressor from train_forecast_model().
        df: Full historical demand DataFrame.
        sku_id: The SKU to generate comparison for.

    Returns:
        dict containing:
            - is_aligned: bool
            - sku_id: str
            - aligned_df: pd.DataFrame with Date, Actual Demand, Forecast Demand, Variance
            - full_history_df: pd.DataFrame with Date, Actual Demand, Forecast Demand
            - horizon_periods: int
            - actual_avg: Optional[float]
            - forecast_avg: Optional[float]
            - mae: Optional[float]
            - mape: Optional[float]
            - rmse: Optional[float]
    """
    if df is None or df.empty or "sku_id" not in df.columns:
        return {"is_aligned": False, "sku_id": sku_id, "error": "Demand data unavailable"}

    sku_rows = df[df["sku_id"] == sku_id].copy()
    if sku_rows.empty or "date" not in sku_rows.columns:
        return {"is_aligned": False, "sku_id": sku_id, "error": f"No demand records for SKU {sku_id}"}

    target_col = "quantity_demanded" if "quantity_demanded" in sku_rows.columns else ("quantity" if "quantity" in sku_rows.columns else None)
    if not target_col:
        return {"is_aligned": False, "sku_id": sku_id, "error": "Quantity column missing"}

    try:
        preds = predict_demand(model, df, sku_id)
    except Exception as e:
        return {"is_aligned": False, "sku_id": sku_id, "error": str(e)}

    if preds is None or preds.empty or "date" not in preds.columns or "predicted_demand" not in preds.columns:
        return {"is_aligned": False, "sku_id": sku_id, "error": "Predictions unavailable"}

    # Normalize dates to string YYYY-MM-DD for consistent alignment
    sku_rows["date_str"] = pd.to_datetime(sku_rows["date"]).dt.strftime("%Y-%m-%d")
    preds["date_str"] = pd.to_datetime(preds["date"]).dt.strftime("%Y-%m-%d")

    # Aggregate actuals by date in case multiple records exist
    sku_actuals = (
        sku_rows.groupby("date_str", as_index=False)[target_col]
        .sum()
        .rename(columns={target_col: "Actual Demand"})
    )
    sku_preds = (
        preds.groupby("date_str", as_index=False)["predicted_demand"]
        .mean()
        .rename(columns={"predicted_demand": "Forecast Demand"})
    )

    aligned = pd.merge(sku_actuals, sku_preds, on="date_str", how="inner").sort_values("date_str").reset_index(drop=True)
    if aligned.empty:
        return {"is_aligned": False, "sku_id": sku_id, "error": "No aligned dates found"}

    aligned["Actual Demand"] = pd.to_numeric(aligned["Actual Demand"], errors="coerce")
    aligned["Forecast Demand"] = pd.to_numeric(aligned["Forecast Demand"], errors="coerce")
    aligned = aligned.dropna(subset=["Actual Demand", "Forecast Demand"]).reset_index(drop=True)

    if aligned.empty:
        return {"is_aligned": False, "sku_id": sku_id, "error": "No valid numeric observations aligned"}

    y_actual = aligned["Actual Demand"].values
    y_pred = aligned["Forecast Demand"].values

    mae = float(np.mean(np.abs(y_actual - y_pred)))
    try:
        reg_metrics = regression_metrics(y_actual, y_pred)
        mape = float(reg_metrics.get("mape", 0.0))
        rmse = float(reg_metrics.get("rmse", 0.0))
    except Exception:
        mape = None
        rmse = None

    display_df = pd.DataFrame({
        "Date": aligned["date_str"],
        "Actual Demand": np.round(y_actual, 1),
        "Forecast Demand": np.round(y_pred, 1),
        "Variance (Actual - Forecast)": np.round(y_actual - y_pred, 1),
    })

    full_history = (
        pd.merge(sku_actuals, sku_preds, on="date_str", how="left")
        .rename(columns={"date_str": "Date"})
        .sort_values("Date")
        .reset_index(drop=True)
    )

    return {
        "is_aligned": True,
        "sku_id": sku_id,
        "aligned_df": display_df,
        "full_history_df": full_history,
        "horizon_periods": len(display_df),
        "actual_avg": float(np.mean(y_actual)),
        "forecast_avg": float(np.mean(y_pred)),
        "mae": mae,
        "mape": mape,
        "rmse": rmse,
    }


# ---------------------------------------------------------------------------
# 5. Feature Importance
# ---------------------------------------------------------------------------

def get_feature_importance(model: lgb.LGBMRegressor) -> Dict[str, float]:
    """
    Return feature importance scores from the trained LightGBM model.
    Higher score = more influential in predictions.
    """
    importance = model.feature_importances_
    return dict(sorted(
        zip(FEATURE_COLS, importance.tolist()),
        key=lambda x: x[1],
        reverse=True,
    ))


# ---------------------------------------------------------------------------
# 5. Standalone test (run directly to verify)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from data_ingestion.csv_source import CSVDataSource

    source = CSVDataSource(data_dir="data")
    df = source.load_historical_demand()

    print(f"Loaded {len(df)} rows of demand data.")
    print(f"SKUs: {df['sku_id'].unique()}")

    model, test_metrics, baseline_metrics = train_forecast_model(df)

    print("\n=== Forecasting Results (Test Split) ===")
    print(f"Model   — MAPE: {test_metrics['mape']:.4f}, RMSE: {test_metrics['rmse']:.4f}")
    print(f"Baseline— MAPE: {baseline_metrics['mape']:.4f}, RMSE: {baseline_metrics['rmse']:.4f}")
    deltas = compare_to_baseline(
        {k: -v for k, v in test_metrics.items()},
        {k: -v for k, v in baseline_metrics.items()},
    )
    print(f"Delta (negative = model is better): {deltas}")

    print("\n=== Feature Importance ===")
    for feat, score in get_feature_importance(model).items():
        print(f"  {feat}: {score}")

    print("\n=== Sample Predictions (SKU_101) ===")
    preds = predict_demand(model, df, "SKU_101")
    print(preds.head(10))