import os
import pandas as pd
from datetime import datetime
from db.connection import SessionLocal
from db.models import SKU, HistoricalDemand, InventorySnapshot, Vehicle, Delivery

def load_data():
    session = SessionLocal()
    data_dir = "data"

    print("Loading SKUs and Inventory Snapshots...")
    inventory_df = pd.read_csv(os.path.join(data_dir, "inventory_snapshot.csv"))
    
    # First, let's create SKUs based on the inventory_snapshot
    for i, row in inventory_df.iterrows():
        sku = session.query(SKU).filter(SKU.sku_id == row['sku_id']).first()
        if not sku:
            # Create a mock name and tier
            sku = SKU(
                sku_id=row['sku_id'],
                name=f"Product {row['sku_id'].split('_')[1]}",
                tier=1 if row['unit_cost'] > 100 else 2,
                unit_cost=float(row['unit_cost']),
                lead_time_days=int(row['lead_time_days']),
                safety_stock_weeks=float(row['safety_stock']) / 50.0  # mock week calculation
            )
            session.add(sku)
            session.commit()
            
        # Add inventory snapshot
        snapshot = InventorySnapshot(
            sku_id=row['sku_id'],
            snapshot_date=datetime(2026, 9, 1), # Fixed date for snapshot
            current_stock=float(row['current_stock']),
            on_order=0.0,
            warehouse_location=row['location_id']
        )
        session.add(snapshot)
    
    session.commit()
    print("SKUs and Inventory Snapshots loaded.")

    print("Loading Historical Demand...")
    demand_df = pd.read_csv(os.path.join(data_dir, "historical_demand.csv"))
    demand_records = []
    for _, row in demand_df.iterrows():
        demand_records.append(HistoricalDemand(
            sku_id=row['sku_id'],
            date=datetime.strptime(row['date'], "%Y-%m-%d"),
            quantity=float(row['quantity_demanded']),
            region=row['location_id']
        ))
    session.bulk_save_objects(demand_records)
    session.commit()
    print(f"Loaded {len(demand_records)} historical demand records.")

    print("Loading Deliveries...")
    deliveries_df = pd.read_csv(os.path.join(data_dir, "deliveries.csv"))
    delivery_records = []
    
    # Assign some random SKUs to deliveries
    skus_list = [sku.sku_id for sku in session.query(SKU).all()]
    
    for i, row in deliveries_df.iterrows():
        # Handle actual_date empty strings if any
        actual_date_str = str(row['actual_date'])
        
        delivery_records.append(Delivery(
            delivery_id=row['delivery_id'],
            sku_id=skus_list[i % len(skus_list)] if skus_list else None,
            carrier=row['carrier_id'],
            origin=row['origin'],
            destination=row['destination'],
            distance_km=float(row['distance_km']),
            scheduled_date=datetime.strptime(row['scheduled_date'], "%Y-%m-%d"),
            actual_date=datetime.strptime(actual_date_str, "%Y-%m-%d") if pd.notna(row['actual_date']) else None,
            delivered=True if pd.notna(row['actual_date']) else False,
            late=bool(row['is_late'])
        ))
    session.bulk_save_objects(delivery_records)
    session.commit()
    print(f"Loaded {len(delivery_records)} deliveries.")
    
    # Mock some Vehicles for later routing optimization
    print("Loading Vehicles...")
    vehicles = [
        Vehicle(vehicle_id="VEH_001", capacity=1000.0, depot_location="WH_CENTRAL"),
        Vehicle(vehicle_id="VEH_002", capacity=1500.0, depot_location="WH_NORTH"),
        Vehicle(vehicle_id="VEH_003", capacity=800.0, depot_location="WH_CENTRAL"),
    ]
    for v in vehicles:
        if not session.query(Vehicle).filter(Vehicle.vehicle_id == v.vehicle_id).first():
            session.add(v)
    session.commit()
    print("Vehicles loaded.")

    session.close()
    print("Data loading complete.")

if __name__ == "__main__":
    load_data()
