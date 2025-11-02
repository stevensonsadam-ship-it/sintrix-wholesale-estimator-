 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/sintrix_wholesale_estimator/__init__.py b/sintrix_wholesale_estimator/__init__.py
new file mode 100644
index 0000000000000000000000000000000000000000..b8f442a8e280dc099567c05bfb59b9efeca0b0cf
--- /dev/null
+++ b/sintrix_wholesale_estimator/__init__.py
@@ -0,0 +1,15 @@
+"""Sintrix Wholesale Estimator package."""
+
+from .estimator import (
+    MarketNotFoundError,
+    PropertyEstimate,
+    PropertyRequest,
+    WholesaleEstimator,
+)
+
+__all__ = [
+    "MarketNotFoundError",
+    "PropertyEstimate",
+    "PropertyRequest",
+    "WholesaleEstimator",
+]
 
EOF
)