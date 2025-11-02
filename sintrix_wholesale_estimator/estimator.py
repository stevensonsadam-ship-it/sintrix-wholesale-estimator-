 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/sintrix_wholesale_estimator/estimator.py b/sintrix_wholesale_estimator/estimator.py
new file mode 100644
index 0000000000000000000000000000000000000000..5584d34e9edd69ce6b199e6cbf6ba35c580d3c5f
--- /dev/null
+++ b/sintrix_wholesale_estimator/estimator.py
@@ -0,0 +1,181 @@
+"""Core wholesale estimation logic."""
+from __future__ import annotations
+
+from dataclasses import dataclass
+from typing import Dict, Mapping, Tuple
+
+from .data import MarketProfile, load_market_profiles
+
+CONDITION_LEVELS = ("turnkey", "rent_ready", "light_rehab", "heavy_rehab", "tear_down")
+PROPERTY_TYPES = ("single_family", "multi_family", "condo", "townhome")
+
+
+class MarketNotFoundError(ValueError):
+    """Raised when a requested market is not defined."""
+
+
+@dataclass
+class PropertyRequest:
+    """Input payload describing the subject property."""
+
+    location: str
+    square_feet: float
+    beds: float
+    baths: float
+    condition: str = "light_rehab"
+    property_type: str = "single_family"
+    year_built: int | None = None
+    lot_square_feet: float | None = None
+    target_assignment_fee: float | None = None
+
+
+@dataclass
+class PropertyEstimate:
+    """Output of the wholesale estimator."""
+
+    arv: float
+    as_is_value: float
+    repair_cost: float
+    closing_cost: float
+    holding_cost: float
+    assignment_fee: float
+    maximum_allowable_offer: float
+    recommended_offer: float
+    projected_profit: float
+    comparable_range: Tuple[float, float]
+    confidence: float
+
+
+class WholesaleEstimator:
+    """Provides wholesale offer guidance based on localized assumptions."""
+
+    def __init__(self, market_profiles: Mapping[str, MarketProfile] | None = None) -> None:
+        self._market_profiles: Mapping[str, MarketProfile] = (
+            market_profiles if market_profiles is not None else load_market_profiles()
+        )
+
+    @property
+    def available_markets(self) -> Tuple[str, ...]:
+        return tuple(sorted(self._market_profiles.keys()))
+
+    def estimate(self, request: PropertyRequest) -> PropertyEstimate:
+        market = self._resolve_market(request.location)
+        self._validate_inputs(request)
+
+        condition = request.condition
+        property_type = request.property_type
+
+        base_price = (
+            market.price_per_sqft_turnkey
+            * market.demand_index
+            * market.property_type_adjustment.get(property_type, 1.0)
+        )
+        arv = base_price * request.square_feet
+
+        condition_factor = market.condition_adjustment.get(condition)
+        if condition_factor is None:
+            raise ValueError(f"Unsupported condition '{condition}'.")
+
+        as_is_value = arv * condition_factor
+
+        repair_cost = self._estimate_repair_cost(request, market)
+        closing_cost = market.closing_cost_rate * arv
+        holding_cost = market.holding_cost_rate * as_is_value * market.holding_months
+
+        assignment_fee = self._assignment_fee(request, market, arv)
+
+        allowable_discount = 0.72 if condition in {"light_rehab", "heavy_rehab", "tear_down"} else 0.78
+        maximum_allowable_offer = max(
+            0.0,
+            (arv * allowable_discount)
+            - repair_cost
+            - closing_cost
+            - holding_cost
+            - assignment_fee,
+        )
+
+        recommended_offer = min(maximum_allowable_offer, as_is_value * 0.98)
+
+        total_investment = (
+            recommended_offer + repair_cost + closing_cost + holding_cost + assignment_fee
+        )
+        projected_profit = max(0.0, arv - total_investment)
+
+        comp_low = as_is_value * 0.92
+        comp_high = arv * 1.05
+        confidence = self._confidence_score(market, request)
+
+        return PropertyEstimate(
+            arv=round(arv, 2),
+            as_is_value=round(as_is_value, 2),
+            repair_cost=round(repair_cost, 2),
+            closing_cost=round(closing_cost, 2),
+            holding_cost=round(holding_cost, 2),
+            assignment_fee=round(assignment_fee, 2),
+            maximum_allowable_offer=round(maximum_allowable_offer, 2),
+            recommended_offer=round(recommended_offer, 2),
+            projected_profit=round(projected_profit, 2),
+            comparable_range=(round(comp_low, 2), round(comp_high, 2)),
+            confidence=round(confidence, 3),
+        )
+
+    def _resolve_market(self, location: str) -> MarketProfile:
+        try:
+            return self._market_profiles[location]
+        except KeyError as exc:  # pragma: no cover - simple guard
+            available = ", ".join(self.available_markets)
+            raise MarketNotFoundError(
+                f"No market profile for '{location}'. Available markets: {available}"
+            ) from exc
+
+    @staticmethod
+    def _validate_inputs(request: PropertyRequest) -> None:
+        if request.square_feet <= 0:
+            raise ValueError("Square footage must be positive.")
+        if request.beds <= 0:
+            raise ValueError("Bedroom count must be positive.")
+        if request.baths <= 0:
+            raise ValueError("Bathroom count must be positive.")
+        if request.condition not in CONDITION_LEVELS:
+            raise ValueError(f"Condition must be one of: {', '.join(CONDITION_LEVELS)}")
+        if request.property_type not in PROPERTY_TYPES:
+            raise ValueError(f"Property type must be one of: {', '.join(PROPERTY_TYPES)}")
+
+    @staticmethod
+    def _estimate_repair_cost(request: PropertyRequest, market: MarketProfile) -> float:
+        per_sqft = market.renovation_cost_per_sqft.get(request.condition, 0.0)
+        modifier = 1.0
+        if request.year_built and request.year_built < 1975:
+            modifier += 0.08
+        if request.year_built and request.year_built < 1950:
+            modifier += 0.05
+        if request.lot_square_feet and request.lot_square_feet > request.square_feet * 2:
+            modifier += 0.03
+        return per_sqft * request.square_feet * modifier
+
+    @staticmethod
+    def _assignment_fee(request: PropertyRequest, market: MarketProfile, arv: float) -> float:
+        if request.target_assignment_fee is not None:
+            return request.target_assignment_fee
+        return max(4500.0, arv * market.wholesale_fee_rate)
+
+    @staticmethod
+    def _confidence_score(market: MarketProfile, request: PropertyRequest) -> float:
+        score = 0.55
+        score += min(0.1, (market.demand_index - 0.95))
+        score += min(0.05, market.wholesale_fee_rate)
+        if request.square_feet <= 900:
+            score += 0.02
+        elif request.square_feet <= 1800:
+            score += 0.05
+        else:
+            score += 0.03
+        if request.condition in {"turnkey", "rent_ready"}:
+            score += 0.08
+        elif request.condition == "light_rehab":
+            score += 0.05
+        if request.property_type == "single_family":
+            score += 0.04
+        elif request.property_type == "multi_family":
+            score += 0.02
+        return max(0.3, min(score, 0.92))
 
EOF
)