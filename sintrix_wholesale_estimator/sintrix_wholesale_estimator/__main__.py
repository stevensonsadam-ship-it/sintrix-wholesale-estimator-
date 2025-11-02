 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/sintrix_wholesale_estimator/__main__.py b/sintrix_wholesale_estimator/__main__.py
new file mode 100644
index 0000000000000000000000000000000000000000..cbe9295c48d319881716cd63711a3ebc2ae08b7b
--- /dev/null
+++ b/sintrix_wholesale_estimator/__main__.py
@@ -0,0 +1,6 @@
+"""Allows running the estimator with `python -m sintrix_wholesale_estimator`."""
+from .cli import run
+
+
+if __name__ == "__main__":  # pragma: no cover - module entry point
+    run()
 
EOF
)