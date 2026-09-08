"""
data_ingestion/validation.py
Canonical schema definition, column normalization, data quality validation,
and dataset profiling for SupplyChain Sentinel AI.
Enables real-world and Kaggle datasets (CSV, Excel, DB, API) to be normalized
into canonical structures without altering core ML pipelines.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# 1. Canonical Schema Specifications
# ---------------------------------------------------------------------------

CANONICAL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "demand": {
        "required_columns": ["sku_id", "date", "quantity_demanded"],
        "optional_columns": ["location_id"],
        "dtypes": {
            "sku_id": "string",
            "date": "datetime64[ns]",
            "quantity_demanded": "float64",
            "location_id": "string",
        },
        "defaults": {
            "location_id": "DEFAULT_LOCATION",
        },
    },
    "inventory": {
        "required_columns": ["sku_id", "current_stock", "reorder_point"],
        "optional_columns": ["safety_stock", "unit_cost", "lead_time_days", "location_id"],
        "dtypes": {
            "sku_id": "string",
            "current_stock": "float64",
            "reorder_point": "float64",
            "safety_stock": "float64",
            "unit_cost": "float64",
            "lead_time_days": "float64",
            "location_id": "string",
        },
        "defaults": {
            "safety_stock": 0.0,
            "unit_cost": 10.0,
            "lead_time_days": 7.0,
            "location_id": "DEFAULT_LOCATION",
        },
    },
    "deliveries": {
        "required_columns": ["delivery_id", "scheduled_date"],
        "optional_columns": [
            "carrier_id", "origin", "destination", "distance_km",
            "actual_date", "is_late", "weather_condition", "traffic_delay_hrs"
        ],
        "dtypes": {
            "delivery_id": "string",
            "carrier_id": "string",
            "origin": "string",
            "destination": "string",
            "distance_km": "float64",
            "scheduled_date": "datetime64[ns]",
            "actual_date": "datetime64[ns]",
            "is_late": "int64",
            "weather_condition": "string",
            "traffic_delay_hrs": "float64",
        },
        "defaults": {
            "carrier_id": "DEFAULT_CARRIER",
            "origin": "ORIGIN_HUB",
            "destination": "DEST_HUB",
            "distance_km": 100.0,
            "is_late": 0,
            "weather_condition": "Clear",
            "traffic_delay_hrs": 0.0,
        },
    },
    "vehicles": {
        "required_columns": ["vehicle_id", "capacity"],
        "optional_columns": ["depot_id"],
        "dtypes": {
            "vehicle_id": "string",
            "capacity": "float64",
            "depot_id": "string",
        },
        "defaults": {
            "depot_id": "CENTRAL_DEPOT",
        },
    },
}

# ---------------------------------------------------------------------------
# 2. Real-World & Kaggle Column Aliases Mapping
# ---------------------------------------------------------------------------

COLUMN_ALIASES: Dict[str, List[str]] = {
    "sku_id": [
        "sku", "sku_id", "product_code", "product_id", "item_code",
        "item_id", "item_number", "stockcode", "part_number", "product"
    ],
    "date": [
        "date", "order_date", "invoicedate", "invoice_date", "timestamp",
        "transaction_date", "dispatch_date", "created_at", "ship_date"
    ],
    "quantity_demanded": [
        "quantity_demanded", "quantity", "order_quantity", "order_qty",
        "qty", "sales", "units_sold", "demand", "volume", "amount"
    ],
    "location_id": [
        "location_id", "location", "warehouse", "store_id", "branch",
        "plant", "dc", "dc_id", "facility", "region"
    ],
    "current_stock": [
        "current_stock", "stock", "stock_level", "inventory", "on_hand",
        "qty_on_hand", "available_stock", "inventory_level"
    ],
    "reorder_point": [
        "reorder_point", "rop", "reorder_level", "min_stock", "reorder_qty"
    ],
    "safety_stock": [
        "safety_stock", "safety_buffer", "buffer_stock", "min_safety_stock"
    ],
    "unit_cost": [
        "unit_cost", "cost", "unit_price", "price", "standard_cost", "cost_price"
    ],
    "lead_time_days": [
        "lead_time_days", "lead_time", "leadtime", "supplier_lead_time"
    ],
    "delivery_id": [
        "delivery_id", "shipment_id", "order_id", "consignment_id", "tracking_number"
    ],
    "carrier_id": [
        "carrier_id", "carrier", "transporter", "logistics_partner", "courier"
    ],
    "distance_km": [
        "distance_km", "distance", "km", "transit_distance", "mileage"
    ],
    "scheduled_date": [
        "scheduled_date", "expected_delivery_date", "promised_date", "scheduled_time"
    ],
    "actual_date": [
        "actual_date", "delivered_date", "arrival_date", "actual_time"
    ],
    "is_late": [
        "is_late", "late", "delayed", "delay_flag", "delivery_status"
    ],
    "traffic_delay_hrs": [
        "traffic_delay_hrs", "traffic_delay", "delay_hours", "delay_hrs"
    ],
    "weather_condition": [
        "weather_condition", "weather", "weather_type", "climate"
    ],
    "vehicle_id": [
        "vehicle_id", "truck_id", "van_id", "transport_unit"
    ],
    "capacity": [
        "capacity", "vehicle_capacity", "max_weight", "max_capacity", "payload"
    ],
}


# ---------------------------------------------------------------------------
# 3. Structured Validation Result Dataclass
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """Detailed validation and data-understanding report for an ingested dataset."""
    schema_type: str
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    column_mapping: Dict[str, str] = field(default_factory=dict)
    profiling: Dict[str, Any] = field(default_factory=dict)
    normalized_df: Optional[pd.DataFrame] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_type": self.schema_type,
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "column_mapping": self.column_mapping,
            "profiling": self.profiling,
            "row_count": len(self.normalized_df) if self.normalized_df is not None else 0,
        }


# ---------------------------------------------------------------------------
# 4. Normalization and Column Mapping
# ---------------------------------------------------------------------------

def suggest_and_normalize_columns(
    df: pd.DataFrame, schema_type: str, explicit_mapping: Optional[Dict[str, str]] = None
) -> Tuple[pd.DataFrame, Dict[str, str], List[str]]:
    """
    Maps and normalizes DataFrame columns to canonical schema names.
    Supports explicit user mapping, exact name match, alias lookup, and substring matching.
    """
    if schema_type not in CANONICAL_SCHEMAS:
        raise ValueError(f"Unknown schema type '{schema_type}'. Expected one of {list(CANONICAL_SCHEMAS.keys())}")

    schema = CANONICAL_SCHEMAS[schema_type]
    all_target_cols = schema["required_columns"] + schema.get("optional_columns", [])
    
    df_clean = df.copy()
    existing_cols = list(df_clean.columns)
    existing_cols_lower = {str(c).strip().lower(): c for c in existing_cols}

    applied_mapping: Dict[str, str] = {}
    notes: List[str] = []

    # 1. Apply explicit mapping if supplied
    if explicit_mapping:
        for canonical_col, raw_col in explicit_mapping.items():
            if raw_col in df_clean.columns:
                applied_mapping[canonical_col] = raw_col

    # 2. For unmapped canonical columns, match via aliases
    for canonical_col in all_target_cols:
        if canonical_col in applied_mapping:
            continue
        
        # Check aliases
        aliases = COLUMN_ALIASES.get(canonical_col, [canonical_col])
        found_col = None
        for alias in aliases:
            cleaned_alias = alias.strip().lower()
            if cleaned_alias in existing_cols_lower:
                found_col = existing_cols_lower[cleaned_alias]
                break
        
        # Fallback: substring matching
        if found_col is None:
            for raw_col, orig_col in existing_cols_lower.items():
                if canonical_col.replace("_", "") in raw_col.replace("_", ""):
                    found_col = orig_col
                    break

        if found_col:
            applied_mapping[canonical_col] = found_col

    # 3. Create normalized DataFrame
    rename_dict = {orig: target for target, orig in applied_mapping.items()}
    df_normalized = df_clean.rename(columns=rename_dict)

    # 4. Fill defaults for missing optional columns
    defaults = schema.get("defaults", {})
    for col, default_val in defaults.items():
        if col not in df_normalized.columns:
            df_normalized[col] = default_val
            notes.append(f"Optional column '{col}' missing; defaulted to {default_val}.")

    return df_normalized, applied_mapping, notes


# ---------------------------------------------------------------------------
# 5. Comprehensive Data Validation
# ---------------------------------------------------------------------------

def validate_dataset(
    df: pd.DataFrame,
    schema_type: str,
    explicit_mapping: Optional[Dict[str, str]] = None
) -> ValidationResult:
    """
    Validates a dataset against canonical schema rules.
    Identifies fatal blocking errors vs actionable non-blocking warnings.
    """
    if schema_type not in CANONICAL_SCHEMAS:
        raise ValueError(f"Unknown schema type '{schema_type}'. Expected one of {list(CANONICAL_SCHEMAS.keys())}")

    errors: List[str] = []
    warnings: List[str] = []

    # 1. Check empty dataframe
    if df is None or df.empty or len(df.dropna(how="all")) == 0:
        return ValidationResult(
            schema_type=schema_type,
            is_valid=False,
            errors=[f"Dataset for '{schema_type}' is completely empty (0 rows)."],
            profiling={"total_rows": 0, "total_columns": 0}
        )

    # 2. Normalize columns
    try:
        norm_df, col_mapping, mapping_notes = suggest_and_normalize_columns(df, schema_type, explicit_mapping)
        warnings.extend(mapping_notes)
    except Exception as e:
        return ValidationResult(
            schema_type=schema_type,
            is_valid=False,
            errors=[f"Failed to map columns: {str(e)}"]
        )

    schema = CANONICAL_SCHEMAS[schema_type]
    req_cols = schema["required_columns"]

    # 3. Check required columns
    missing_required = [c for c in req_cols if c not in norm_df.columns]
    if missing_required:
        errors.append(f"Fatal: Missing required columns for '{schema_type}': {missing_required}. Please map these columns.")
        return ValidationResult(
            schema_type=schema_type,
            is_valid=False,
            errors=errors,
            warnings=warnings,
            column_mapping=col_mapping,
            normalized_df=norm_df
        )

    # 4. Type conversions and date/numeric validation
    for col in req_cols + schema.get("optional_columns", []):
        if col not in norm_df.columns:
            continue

        target_dtype = schema["dtypes"].get(col)
        
        # DateTime handling
        if target_dtype and "datetime" in target_dtype:
            try:
                norm_df[col] = pd.to_datetime(norm_df[col], errors="coerce")
                null_dates = norm_df[col].isnull().sum()
                if null_dates > 0:
                    warnings.append(f"Column '{col}' has {null_dates} invalid or unparseable date values.")
            except Exception as e:
                errors.append(f"Column '{col}' could not be converted to datetime: {str(e)}")

        # Numeric handling
        elif target_dtype in ["float64", "int64"]:
            try:
                norm_df[col] = pd.to_numeric(norm_df[col], errors="coerce")
                null_num = norm_df[col].isnull().sum()
                if null_num > 0:
                    warnings.append(f"Column '{col}' contains {null_num} non-numeric values coerced to NaN.")
                
                # Check for negative values where forbidden
                if col in ["quantity_demanded", "current_stock", "reorder_point", "safety_stock", "lead_time_days"]:
                    negative_count = (norm_df[col] < 0).sum()
                    if negative_count > 0:
                        warnings.append(f"Column '{col}' has {negative_count} negative values.")
            except Exception as e:
                errors.append(f"Column '{col}' could not be converted to numeric: {str(e)}")

        # String identifier handling
        elif target_dtype == "string":
            norm_df[col] = norm_df[col].astype(str)

    # 5. Check duplicate rows
    dupes = norm_df.duplicated().sum()
    if dupes > 0:
        warnings.append(f"Detected {dupes} duplicate rows in dataset.")

    # 6. Profile the dataset
    profiling = profile_dataset(norm_df, schema_type)

    # Check for small dataset / data sparsity warnings
    if profiling.get("is_small_dataset"):
        warnings.append(
            f"Small dataset warning: SKUs have an average of {profiling.get('avg_records_per_sku', 0):.1f} records. "
            "ML models require at least 15 points per SKU; baseline forecasting will be used for smaller SKUs."
        )

    is_valid = len(errors) == 0

    return ValidationResult(
        schema_type=schema_type,
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        column_mapping=col_mapping,
        profiling=profiling,
        normalized_df=norm_df if is_valid else None
    )


# ---------------------------------------------------------------------------
# 6. Dataset Understanding Profiler
# ---------------------------------------------------------------------------

def profile_dataset(df: pd.DataFrame, schema_type: str) -> Dict[str, Any]:
    """
    Analyzes dataset dimensions, unique entities, date spans, and operational readiness.
    Provides metrics that display in the UI without relying on hardcoded values.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    
    summary: Dict[str, Any] = {
        "schema_type": schema_type,
        "total_rows": total_rows,
        "total_columns": total_cols,
        "columns": list(df.columns),
        "missing_values_count": int(df.isnull().sum().sum()),
        "missing_percentage": float((df.isnull().sum().sum() / (total_rows * total_cols)) * 100) if total_rows and total_cols else 0.0,
    }

    # Demand profile
    if "sku_id" in df.columns:
        unique_skus = df["sku_id"].dropna().unique().tolist()
        summary["unique_skus_count"] = len(unique_skus)
        summary["sample_skus"] = unique_skus[:5]
        if total_rows and len(unique_skus):
            avg_per_sku = total_rows / len(unique_skus)
            summary["avg_records_per_sku"] = avg_per_sku
            summary["is_small_dataset"] = avg_per_sku < 15.0
        else:
            summary["is_small_dataset"] = True

    if "date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["date"]):
        valid_dates = df["date"].dropna()
        if not valid_dates.empty:
            summary["min_date"] = valid_dates.min().strftime("%Y-%m-%d")
            summary["max_date"] = valid_dates.max().strftime("%Y-%m-%d")
            summary["date_range_days"] = (valid_dates.max() - valid_dates.min()).days

    if "location_id" in df.columns:
        summary["unique_locations_count"] = int(df["location_id"].nunique())

    if "delivery_id" in df.columns:
        summary["total_deliveries"] = int(df["delivery_id"].nunique())
        if "is_late" in df.columns:
            summary["late_deliveries_count"] = int((df["is_late"] == 1).sum())
            summary["on_time_rate_pct"] = float((1.0 - ((df["is_late"] == 1).sum() / max(1, total_rows))) * 100.0)

    return summary
