# Supply Chain CPQ — Scope, KPIs, and UAT Charter

This document freezes the scope, entity inventory, KPI list, and UAT scenarios for the Supply Chain CPQ platform implemented under the existing three-plane fabric. It is the source of truth for Sprints S1–S8.

For the conceptual framing see [Telco CPQ reference](def.md). For the existing supply-chain ontology see [Supply Chain Ontology Overview](../app-catalogue/supply-chain/ontology/index.md).

---

## 1. Platform Scope

Two coordinated modules sharing one CPQ engine on the existing Data, Control, and Reasoning planes:

| Module | Direction | Primary persona | Counter-party |
|--------|-----------|------------------|---------------|
| **Trade CPQ** | Sell-side | Sales rep / Commercial desk | Modern Trade, General Trade, HORECA, E-commerce |
| **Sourcing CPQ** | Buy-side | Category buyer / Sourcing manager | Raw material, Packaging, Co-pack, Logistics vendors |

Both modules expose **Configure → Price → Quote** semantics symmetric to Telco CPQ:

- Configure: assemble valid offerings (sell) or RFx baskets (buy) under declarative rules.
- Price: compute net per scenario from price books, promotions, should-cost models, contracts.
- Quote: produce a commercial document (proposal PDF, contract draft), route approvals, convert to order/PO.

## 2. Entity Inventory (Frozen for S1)

### 2.1 Sell-side — Domain 13 (Commercial Configure/Quote)

New virtual entities — all overlay the existing [supply-chain-schema.yaml](https://github.com/) `Material_Master`, `Account`, `Campaign`, `Cost_Accounting`, `AR_Customer`, `Plant_Master` masters.

1. `Product_Offering`
2. `Offering_Component`
3. `Price_Book`
4. `Price_Book_Entry`
5. `Quote_Header`
6. `Quote_Line`
7. `Quote_Promotion`
8. `Serviceability_Footprint`
9. `Configuration_Rule`

### 2.2 Buy-side — Domain 14 (Sourcing RFx/Award)

Overlay `Vendor_Master`, `Source_List`, `Material_Master`, `Plant_Master`, `Commodity_Price`, `Contract_Document`.

1. `RFx_Event`
2. `RFx_Line`
3. `RFx_Invitation`
4. `Vendor_Quote`
5. `Vendor_Quote_Line`
6. `Should_Cost_Model`
7. `Sourcing_Scenario`
8. `Sourcing_Award`

Total new tables: 17 virtual entities (zero new master entities — all join to existing masters via `Material_ID`, `Account_ID`, `Vendor_ID`, `Plant_ID`).

## 3. KPIs (Frozen for S5/S7 dashboards and S8 UAT)

### 3.1 Trade CPQ KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Quote cycle time (draft → approved) | < 1 business day | `Quote_Header.Created_At` → `Approval_Completed_At` |
| Auto-approval rate | > 70 % | `Quote_Header.Approval_Chain_JSON` |
| Win rate (Won_Converted / Submitted) | +5 to +8 pp uplift | `Quote_Header.Status` |
| Discount leakage (below tier floor) | < 1 % | `Quote_Line.Discount_Pct` vs `Price_Book_Entry.Floor_Price` |
| Margin floor breach rate | < 5 % | `Quote_Line.Margin_Pct_Line` vs `pricing-discount-policy` |
| Proposal generation latency | < 60 s p95 | `generate_proposal_doc` tool trace |

### 3.2 Sourcing CPQ KPIs

| KPI | Target | Source |
|-----|--------|--------|
| RFx cycle time (launch → award) | < 10 business days | `RFx_Event.Open_Date` → `Sourcing_Award.Issued_At` |
| Savings vs should-cost | > 5 % | `Sourcing_Scenario.Modeled_Savings` |
| Single-source ABC-A risk | < 2 % | `Source_List` joined on `Material_Plant.ABC_Classification` |
| Time to contract | < 3 business days after award | `Sourcing_Award.Approved_At` → `Contract_Document.Effective_Date` |
| Vendor concentration ceiling | ≤ 60 % per vendor per category | `Sourcing_Scenario.Concentration_Pct` |

### 3.3 Platform KPIs (cross-cutting)

| KPI | Target |
|-----|--------|
| All CPQ entities resolvable via Virtual Data Layer | 100 % |
| Reasoning traces visible with token cost | 100 % of agent runs |
| Approval policy coverage | 100 % of submitted quotes/awards |

## 4. Connector Scope (v1)

- **Sell-side**: Trade Promotion Management (TPM) simulator (new) hosts `Product_Offering`, `Price_Book*`, `Quote_*`, `Serviceability_Footprint`, `Configuration_Rule`, `Quote_Promotion`. Live Salesforce CPQ FDW is out of scope for v1; the simulator-toggle pattern allows swap-in later.
- **Buy-side**: Sourcing simulator (SAP Ariba-style, new) hosts `RFx_*`, `Vendor_Quote*`, `Should_Cost_Model`, `Sourcing_Scenario`, `Sourcing_Award`. Live Ariba/SAP SRM FDW is out of scope for v1.
- **Reused**: existing SAP, Salesforce, Oracle ERP, Google Drive, Social Listening simulators provide all masters and reference data.

## 5. UAT Scenarios (Frozen for S8)

### 5.1 Trade CPQ — Happy path

> "Build a quote for Reliance Modern Trade Q3 promo: 10,000 cases of Cola 330ml + 5,000 cases of Energy 500ml; discount 14 %; ship from Plant_IN_MUM to 3 DCs."

Expected outcome: draft `Quote_Header`, 2 lines, promo applied, waterfall shows margin 17 %, auto-approved, proposal PDF generated, quote convertible to order.

### 5.2 Trade CPQ — Margin floor breach

> "Same quote at 28 % discount."

Expected: margin 12 %, below floor → routed to CFO; agent annotates risk; rep can accept and submit; status = `In_Review`.

### 5.3 Trade CPQ — Configuration violation

> "Bundle 24-pack cans with HORECA channel."

Expected: `Configuration_Rule` violation (HORECA single-serve only); agent suggests substitution to 330 ml single-serve.

### 5.4 Sourcing CPQ — Happy path

> "Run an RFQ for 100 MT PET resin, 3 plants, 14-day close."

Expected: `RFx_Event` + 3 `RFx_Line`, invite top 5 vendors from `Source_List`, should-cost model published, three scenarios produced after bid submission, recommended scenario within policy.

### 5.5 Sourcing CPQ — Single-source guard

> "Award all volume to one vendor."

Expected: `sourcing-award-policy` violation (ABC-A material, single-source); agent forces split or escalates to VP Procurement.

### 5.6 Sourcing CPQ — Disruption-triggered emergency RFQ

> Critical `Market_Signal` on PET resin port congestion.

Expected: existing [disruption-response.yaml](../../app-catalogue/supply-chain/ontology/workflows.md) chains into `emergency_alt_source.yaml`; emergency `RFx_Event` auto-drafted; alternative vendors highlighted.

## 6. Assumptions and Risks

- LLM proposal/contract generation requires 3 templates per side; assume legal/commercial supplies by S5/S7.
- Approval routing reuses the existing approval task infrastructure used by O2C. If not present a thin store is added in S3.
- Should-cost model uses historical `Commodity_Price` only in v1; supplier cost benchmarking from external indices is a v2 enhancement.
- Live Salesforce CPQ and SAP Ariba connectors are deferred to a post-v1 sprint; the simulator-toggle pattern at the data plane allows hot swap.

## 7. Out of Scope (v1)

- Multi-currency conversion (single currency per quote/RFx).
- Multi-language proposal generation.
- Reverse auction live bidding UI (entity exists; only static bid matrix in v1).
- Tax engine integration (placeholder field only).
- e-signature workflow (placeholder; document is finalized in PDF).

---

[Back to CPQ index](def.md)
