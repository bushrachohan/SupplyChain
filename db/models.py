from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from db.connection import Base


class SKU(Base):
    __tablename__ = "skus"

    sku_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    tier = Column(Integer, nullable=False)          # 1 = highest priority
    unit_cost = Column(Float, nullable=False)
    lead_time_days = Column(Integer, nullable=False)
    safety_stock_weeks = Column(Float, nullable=False)

    demand_history = relationship("HistoricalDemand", back_populates="sku")
    inventory_snapshots = relationship("InventorySnapshot", back_populates="sku")
    forecast_results = relationship("ForecastResult", back_populates="sku")
    inventory_risks = relationship("InventoryRisk", back_populates="sku")


class HistoricalDemand(Base):
    __tablename__ = "historical_demand"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False)
    date = Column(DateTime, nullable=False)
    quantity = Column(Float, nullable=False)
    region = Column(String, nullable=True)

    sku = relationship("SKU", back_populates="demand_history")


class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False)
    snapshot_date = Column(DateTime, nullable=False)
    current_stock = Column(Float, nullable=False)
    on_order = Column(Float, default=0.0)
    warehouse_location = Column(String, nullable=True)

    sku = relationship("SKU", back_populates="inventory_snapshots")


class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False)
    forecast_date = Column(DateTime, nullable=False)
    horizon_weeks = Column(Integer, nullable=False)
    predicted_demand = Column(Float, nullable=False)
    model_used = Column(String, nullable=False)
    mape = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sku = relationship("SKU", back_populates="forecast_results")


class InventoryRisk(Base):
    __tablename__ = "inventory_risk"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    days_of_stock_remaining = Column(Float, nullable=False)
    risk_flag = Column(String, nullable=False)      # "stockout", "overstock", "ok"
    top_driver = Column(String, nullable=True)      # main feature driving the flag

    sku = relationship("SKU", back_populates="inventory_risks")


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(String, primary_key=True)
    capacity = Column(Float, nullable=False)
    depot_location = Column(String, nullable=False)


class Delivery(Base):
    __tablename__ = "deliveries"

    delivery_id = Column(String, primary_key=True)
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=True)
    carrier = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    actual_date = Column(DateTime, nullable=True)
    delivered = Column(Boolean, default=False)
    late = Column(Boolean, nullable=True)


class DeliveryRiskPrediction(Base):
    __tablename__ = "delivery_risk_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    delivery_id = Column(String, ForeignKey("deliveries.delivery_id"), nullable=False)
    predicted_at = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float, nullable=False)      # 0.0 – 1.0
    risk_label = Column(String, nullable=False)     # "high" / "low"
    top_features = Column(JSON, nullable=True)      # SHAP feature importance dict


class Route(Base):
    __tablename__ = "routes"

    route_id = Column(String, primary_key=True)
    vehicle_id = Column(String, ForeignKey("vehicles.vehicle_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_distance_km = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=True)

    stops = relationship("RouteStop", back_populates="route")


class RouteStop(Base):
    __tablename__ = "route_stops"

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(String, ForeignKey("routes.route_id"), nullable=False)
    delivery_id = Column(String, ForeignKey("deliveries.delivery_id"), nullable=False)
    stop_sequence = Column(Integer, nullable=False)

    route = relationship("Route", back_populates="stops")


class Policy(Base):
    __tablename__ = "policies"

    policy_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=True)        # "inventory", "procurement", "logistics"
    embedding = Column(JSON, nullable=True)         # stored as list of floats
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    situation = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    llm_narration = Column(Text, nullable=True)
    status = Column(String, default="pending")      # "pending" / "approved" / "rejected"


class ImpactSimulation(Base):
    __tablename__ = "impact_simulations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_id = Column(String, ForeignKey("recommendations.recommendation_id"))
    metric = Column(String, nullable=False)
    before_value = Column(Float, nullable=False)
    after_value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)


class DecisionTrace(Base):
    __tablename__ = "decision_traces"

    trace_id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    inputs = Column(JSON, nullable=False)
    predictions = Column(JSON, nullable=True)
    policies_retrieved = Column(JSON, nullable=True)
    tools_used = Column(JSON, nullable=True)
    options_considered = Column(JSON, nullable=True)
    recommendation = Column(JSON, nullable=True)
    human_approval = Column(JSON, nullable=True)    # {status, approver, timestamp, notes}
    outcome = Column(JSON, nullable=True)


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String, ForeignKey("decision_traces.trace_id"), nullable=False)
    status = Column(String, nullable=False)         # "pending" / "approved" / "rejected"
    approver = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    