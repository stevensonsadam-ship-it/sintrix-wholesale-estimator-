 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/sintrix_wholesale_estimator/data.py b/sintrix_wholesale_estimator/data.py
new file mode 100644
index 0000000000000000000000000000000000000000..4582d03f3a6467348ae119acfcae4c5d546e1312
--- /dev/null
+++ b/sintrix_wholesale_estimator/data.py
@@ -0,0 +1,47 @@
+"""Utilities for loading market data used by the estimator."""
+from __future__ import annotations
+
+import json
+from dataclasses import dataclass
+from importlib import resources
+from typing import Dict, Mapping
+
+
+@dataclass(frozen=True)
+class MarketProfile:
+    """Data model representing localized assumptions for an area."""
+
+    name: str
+    price_per_sqft_turnkey: float
+    condition_adjustment: Mapping[str, float]
+    property_type_adjustment: Mapping[str, float]
+    renovation_cost_per_sqft: Mapping[str, float]
+    closing_cost_rate: float
+    holding_cost_rate: float
+    wholesale_fee_rate: float
+    holding_months: float
+    demand_index: float
+
+
+def load_market_profiles() -> Dict[str, MarketProfile]:
+    """Load market profile data bundled with the package."""
+
+    path = resources.files(__package__) / "data" / "market_data.json"
+    raw = json.loads(path.read_text())
+
+    profiles: Dict[str, MarketProfile] = {}
+    for name, payload in raw.items():
+        profiles[name] = MarketProfile(
+            name=name,
+            price_per_sqft_turnkey=payload["price_per_sqft_turnkey"],
+            condition_adjustment=payload["condition_adjustment"],
+            property_type_adjustment=payload["property_type_adjustment"],
+            renovation_cost_per_sqft=payload["renovation_cost_per_sqft"],
+            closing_cost_rate=payload["closing_cost_rate"],
+            holding_cost_rate=payload["holding_cost_rate"],
+            wholesale_fee_rate=payload["wholesale_fee_rate"],
+            holding_months=payload["holding_months"],
+            demand_index=payload["demand_index"],
+        )
+
+    return profiles
 
EOF
)