"""
Script to generate synthetic seed data for development and testing.
Creates CSV files in the data/ directory:
- historical_demand.csv
- inventory_snapshot.csv
- deliveries.csv
"""

import os
import pandas as pd
import numpy as np


def generate_seed_data(output_dir: str = "data", seed: int = 42):
    np.random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)

    # 1. Historical Demand (12 weeks for 5 SKUs)
    dates = pd.date_range(start="2026-06-01", periods=90, freq="D")
    skus = ["SKU_101", "SKU_102", "SKU_103", "SKU_104", "SKU_105"]
    locations = ["LOC_NORTH", "LOC_SOUTH"]

    demand_records = []
    for sku in skus:
        base_demand = np.random.randint(20, 100)
        trend = np.random.choice([0.1, -0.05, 0.2, 0.0])
        for i, date in enumerate(dates):
            # add seasonality and noise
            seasonality = np.sin(i / 7.0 * 2 * np.pi) * 10
            qty = max(0, int(base_demand + trend * i + seasonality + np.random.normal(0, 5)))
            demand_records.append({
                "sku_id": sku,
                "date": date.strftime("%Y-%m-%d"),
                "quantity_demanded": qty,
                "location_id": np.random.choice(locations)
            })

    demand_df = pd.DataFrame(demand_records)
    demand_df.to_csv(os.path.join(output_dir, "historical_demand.csv"), index=False)
    print(f"Generated {len(demand_df)} demand records in {output_dir}/historical_demand.csv")

    # 2. Inventory Snapshot
    inventory_records = [
        {"sku_id": "SKU_101", "current_stock": 150, "reorder_point": 200, "safety_stock": 100, "unit_cost": 45.0, "lead_time_days": 7, "location_id": "LOC_NORTH"},
        {"sku_id": "SKU_102", "current_stock": 50, "reorder_point": 120, "safety_stock": 60, "unit_cost": 120.0, "lead_time_days": 10, "location_id": "LOC_NORTH"},
        {"sku_id": "SKU_103", "current_stock": 400, "reorder_point": 300, "safety_stock": 150, "unit_cost": 15.0, "lead_time_days": 5, "location_id": "LOC_SOUTH"},
        {"sku_id": "SKU_104", "current_stock": 20, "reorder_point": 80, "safety_stock": 40, "unit_cost": 250.0, "lead_time_days": 14, "location_id": "LOC_SOUTH"},
        {"sku_id": "SKU_105", "current_stock": 600, "reorder_point": 400, "safety_stock": 200, "unit_cost": 8.5, "lead_time_days": 3, "location_id": "LOC_NORTH"},
    ]
    inventory_df = pd.DataFrame(inventory_records)
    inventory_df.to_csv(os.path.join(output_dir, "inventory_snapshot.csv"), index=False)
    print(f"Generated {len(inventory_df)} inventory records in {output_dir}/inventory_snapshot.csv")

    # 3. Deliveries History & Active Deliveries
    delivery_records = []
    carriers = ["CARRIER_A", "CARRIER_B", "CARRIER_C"]
    origins = ["WH_CENTRAL", "WH_NORTH"]
    destinations = ["RETAIL_1", "RETAIL_2", "RETAIL_3", "HUB_WEST"]

    for i in range(1, 51):
        sched_date = pd.Timestamp("2026-08-01") + pd.Timedelta(days=i)
        delay = np.random.choice([0, 0, 0, 1, 2, 4], p=[0.6, 0.15, 0.1, 0.08, 0.05, 0.02])
        is_late = int(delay > 0)
        actual_date = sched_date + pd.Timedelta(days=delay)
        dist = np.random.randint(50, 600)
        weather = np.random.choice(["CLEAR", "RAIN", "STORM"], p=[0.7, 0.2, 0.1])
        traffic_delay = round(float(np.random.exponential(1.0) if weather != "CLEAR" else np.random.exponential(0.2)), 1)

        delivery_records.append({
            "delivery_id": f"DEL_{i:03d}",
            "carrier_id": np.random.choice(carriers),
            "origin": np.random.choice(origins),
            "destination": np.random.choice(destinations),
            "distance_km": dist,
            "scheduled_date": sched_date.strftime("%Y-%m-%d"),
            "actual_date": actual_date.strftime("%Y-%m-%d"),
            "is_late": is_late,
            "weather_condition": weather,
            "traffic_delay_hrs": traffic_delay
        })

    deliveries_df = pd.DataFrame(delivery_records)
    deliveries_df.to_csv(os.path.join(output_dir, "deliveries.csv"), index=False)
    print(f"Generated {len(deliveries_df)} delivery records in {output_dir}/deliveries.csv")


if __name__ == "__main__":
    generate_seed_data()
