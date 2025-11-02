 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/tests/test_estimator.py b/tests/test_estimator.py
new file mode 100644
index 0000000000000000000000000000000000000000..7253601c9fc805f5b126172ec45882f1b2e8c225
--- /dev/null
+++ b/tests/test_estimator.py
@@ -0,0 +1,36 @@
+from sintrix_wholesale_estimator import MarketNotFoundError, PropertyRequest, WholesaleEstimator
+
+
+def test_estimate_returns_expected_fields():
+    estimator = WholesaleEstimator()
+    request = PropertyRequest(
+        location="Austin, TX",
+        square_feet=1800,
+        beds=3,
+        baths=2,
+        condition="light_rehab",
+        property_type="single_family",
+    )
+    estimate = estimator.estimate(request)
+
+    assert estimate.arv > estimate.as_is_value
+    assert estimate.maximum_allowable_offer <= estimate.arv
+    assert estimate.recommended_offer <= estimate.maximum_allowable_offer
+    assert estimate.comparable_range[0] < estimate.comparable_range[1]
+
+
+def test_invalid_market_raises():
+    estimator = WholesaleEstimator()
+    request = PropertyRequest(
+        location="Unknown City",
+        square_feet=1500,
+        beds=3,
+        baths=2,
+    )
+
+    try:
+        estimator.estimate(request)
+    except MarketNotFoundError as exc:
+        assert "Available markets" in str(exc)
+    else:
+        raise AssertionError("Expected MarketNotFoundError to be raised")
 
EOF
)