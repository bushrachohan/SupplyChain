# Inventory Control & Safety Stock Policy

**Document ID:** POL-INV-001  
**Version:** 1.0  
**Effective Date:** 2026-06-01  
**Target Scope:** Global Warehouses & Regional Distribution Centers  

---

## 1. Safety Stock Buffer Requirements

1. **Tier-1 Critical SKUs (High Value / High Velocity):**
   - Must maintain a minimum of **14 days (2 weeks)** of safety stock buffer based on trailing 4-week mean daily demand.
   - If stock falls below 14 days, an immediate **INVENTORY_RISK_FLAG** (CRITICAL) must be raised.

2. **Tier-2 Standard SKUs:**
   - Must maintain a minimum of **7 days (1 week)** of safety stock buffer.
   - Stock below 7 days triggers a **REORDER_WARNING** (MEDIUM).

3. **Tier-3 Low Velocity SKUs:**
   - Safety stock buffer requirement is **3 days**.

---

## 2. Reorder Point (ROP) Calculation Policy

- Reorder Point formula:
  $$\text{ROP} = (\text{Lead Time in Days} \times \text{Average Daily Demand}) + \text{Safety Stock}$$
- Purchase orders must be automatically recommended whenever `current_stock <= ROP`.

---

## 3. Stockout Prevention & Allocation Constraints

- **Zero-Stock Penalty:** Any projected stockout within 7 days requires emergency stock re-allocation from the nearest regional warehouse before expediting external purchase orders.
- **Max Stock Cap:** Inventory levels must not exceed **60 days of demand** to prevent warehouse congestion and holding costs.
