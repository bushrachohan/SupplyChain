# Procurement & Purchase Approval Policy

**Document ID:** POL-PRO-003  
**Version:** 1.0  
**Effective Date:** 2026-06-01  
**Target Scope:** Procurement Teams & AI Decision Agent Governance  

---

## 1. Human-in-the-Loop Approval Thresholds

1. **Mandatory Human Gate:**
   - **NO purchase order or shipment rerouting action may be automatically executed.**
   - All AI Decision Agent recommendations must be logged with a status of `PENDING` and require explicit human approval via the dashboard.

2. **Approval Hierarchy by Value:**
   - Purchase orders $< \$10,000$: Requires Supply Chain Manager approval.
   - Purchase orders $\ge \$10,000$: Requires Supply Chain Director approval.

---

## 2. Supplier Lead Time & Risk Management

- **Single-Source Risk Policy:** No more than **60%** of total SKU volume may be sourced from a single supplier if lead times exceed **14 days**.
- Emergency orders must default to preferred suppliers with certified lead times under **5 days**.
