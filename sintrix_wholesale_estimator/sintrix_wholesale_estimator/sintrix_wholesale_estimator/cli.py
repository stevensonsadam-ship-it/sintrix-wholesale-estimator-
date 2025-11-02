 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/sintrix_wholesale_estimator/cli.py b/sintrix_wholesale_estimator/cli.py
new file mode 100644
index 0000000000000000000000000000000000000000..d2c7cc161696400cac44fd6f283d84ad0b317662
--- /dev/null
+++ b/sintrix_wholesale_estimator/cli.py
@@ -0,0 +1,113 @@
+"""Command line entry point for the Sintrix Wholesale Estimator."""
+from __future__ import annotations
+
+import argparse
+import json
+from dataclasses import asdict
+
+from .estimator import PropertyEstimate, PropertyRequest, WholesaleEstimator
+
+
+def build_parser() -> argparse.ArgumentParser:
+    parser = argparse.ArgumentParser(
+        description=(
+            "AI-assisted wholesale estimator that evaluates a property, "
+            "produces a repair and cost breakdown, and suggests an offer."
+        )
+    )
+
+    parser.add_argument("location", help="Market name, e.g. 'Austin, TX'.")
+    parser.add_argument("square_feet", type=float, help="Heated square footage of the property.")
+    parser.add_argument("beds", type=float, help="Bedroom count.")
+    parser.add_argument("baths", type=float, help="Bathroom count.")
+
+    parser.add_argument(
+        "--condition",
+        choices=[
+            "turnkey",
+            "rent_ready",
+            "light_rehab",
+            "heavy_rehab",
+            "tear_down",
+        ],
+        default="light_rehab",
+        help="Current condition of the property.",
+    )
+    parser.add_argument(
+        "--property-type",
+        choices=["single_family", "multi_family", "condo", "townhome"],
+        default="single_family",
+        help="Type of property.",
+    )
+    parser.add_argument("--year-built", type=int, help="Year the property was built.")
+    parser.add_argument(
+        "--lot-square-feet",
+        type=float,
+        help="Lot size in square feet to inform exterior scope adjustments.",
+    )
+    parser.add_argument(
+        "--target-assignment-fee",
+        type=float,
+        help="Override the recommended assignment fee with a custom value.",
+    )
+    parser.add_argument(
+        "--as-json",
+        action="store_true",
+        help="Return the estimate as formatted JSON rather than human readable text.",
+    )
+    return parser
+
+
+def run(argv: list[str] | None = None) -> PropertyEstimate:
+    parser = build_parser()
+    args = parser.parse_args(argv)
+
+    estimator = WholesaleEstimator()
+    request = PropertyRequest(
+        location=args.location,
+        square_feet=args.square_feet,
+        beds=args.beds,
+        baths=args.baths,
+        condition=args.condition,
+        property_type=args.property_type,
+        year_built=args.year_built,
+        lot_square_feet=args.lot_square_feet,
+        target_assignment_fee=args.target_assignment_fee,
+    )
+    estimate = estimator.estimate(request)
+
+    if args.as_json:
+        print(_to_json(estimate))
+    else:
+        print(_format_estimate(estimate))
+
+    return estimate
+
+
+def _to_json(estimate: PropertyEstimate) -> str:
+    return json.dumps(asdict(estimate), indent=2)
+
+
+def _format_estimate(estimate: PropertyEstimate) -> str:
+    report = [
+        "SINTRIX WHOLESALE ESTIMATE",
+        "---------------------------",
+        f"After-repair value (ARV):      ${estimate.arv:,.2f}",
+        f"As-is value:                   ${estimate.as_is_value:,.2f}",
+        f"Repair budget:                 ${estimate.repair_cost:,.2f}",
+        f"Closing costs:                 ${estimate.closing_cost:,.2f}",
+        f"Holding costs:                 ${estimate.holding_cost:,.2f}",
+        f"Assignment fee:                ${estimate.assignment_fee:,.2f}",
+        f"Maximum allowable offer (MAO): ${estimate.maximum_allowable_offer:,.2f}",
+        f"Recommended offer:             ${estimate.recommended_offer:,.2f}",
+        f"Projected profit:              ${estimate.projected_profit:,.2f}",
+        "",
+        f"Comparable sale range:         ${estimate.comparable_range[0]:,.2f}"
+        f" - ${estimate.comparable_range[1]:,.2f}",
+        f"Confidence score:              {estimate.confidence:.0%}",
+    ]
+    return "\n".join(report)
+
+
+if __name__ == "__main__":  # pragma: no cover - CLI entry point
+    run()
 
EOF
)