 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
index f09d13b2c8bc3fed2e6f2353f0e3f69e1e23735e..e7c9b3e04bee1ec46041decde53e05dff575898c 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,76 @@
-# sintrix-wholesale-estimator-
- app that will be used mainly by people trying to whole sale, this app with use ai to inform of local estimates of specific property and its value, give a precise cost break down then give information to user for what they should offer home owner and cover their wholesaler cost
+# Sintrix Wholesale Estimator
+
+Sintrix Wholesale Estimator is a lightweight Python application that provides AI-assisted
+valuation guidance for residential wholesale deals. It combines localized market heuristics
+with property-level inputs to deliver a cost breakdown, maximum allowable offer (MAO), and a
+recommended offer that preserves your wholesale spread.
+
+## Features
+
+- Pre-loaded market profiles for several high-volume metro areas
+- ARV, as-is value, and comparable sale range estimates using demand-adjusted pricing
+- Detailed cost breakdown covering repairs, closing costs, holding costs, and assignment fees
+- Configurable assignment fee override to tailor spreads to your business model
+- CLI output in either human-readable or JSON formats for easy sharing or integration
+
+## Quick start
+
+1. Ensure you have Python 3.10+ installed.
+2. Clone the repository and install dependencies (only the standard library is required).
+3. Run the CLI to generate an estimate:
+
+```bash
+python -m sintrix_wholesale_estimator "Austin, TX" 1850 3 2 \
+  --condition light_rehab \
+  --property-type single_family
+```
+
+Example output:
+
+```
+SINTRIX WHOLESALE ESTIMATE
+---------------------------
+After-repair value (ARV):      $560,952.00
+As-is value:                   $459,981.60
+Repair budget:                 $63,360.00
+Closing costs:                 $17,950.46
+Holding costs:                 $21,096.12
+Assignment fee:                $36,462.88
+Maximum allowable offer (MAO): $265,001.94
+Recommended offer:             $265,001.94
+Projected profit:              $157,081.60
+
+Comparable sale range:         $423,183.07 - $589,999.60
+Confidence score:              77%
+```
+
+To integrate with other tooling, return JSON instead:
+
+```bash
+python -m sintrix_wholesale_estimator "Austin, TX" 1850 3 2 --as-json
+```
+
+## Running tests
+
+Install `pytest` (e.g., `pip install pytest`) and execute:
+
+```bash
+pytest
+```
+
+## Extending market data
+
+Add new markets by editing `sintrix_wholesale_estimator/data/market_data.json`. Each market
+profile contains:
+
+- `price_per_sqft_turnkey`: Baseline price per square foot for turnkey homes
+- `condition_adjustment`: Discount factors per condition to model as-is values
+- `property_type_adjustment`: Multipliers per property type
+- `renovation_cost_per_sqft`: Typical renovation budgets per condition level
+- `closing_cost_rate`, `holding_cost_rate`: Cost assumptions applied to ARV/as-is value
+- `wholesale_fee_rate`: Target spread for assignment fees
+- `holding_months`: Average holding period for projects in that market
+- `demand_index`: Market heat multiplier influencing ARV
+
+Fine-tune the estimator by calibrating these values to your acquisition team's comps and
+contract-to-close timelines.
 
EOF
)