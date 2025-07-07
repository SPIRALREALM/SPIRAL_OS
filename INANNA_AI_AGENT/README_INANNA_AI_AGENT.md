 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/README_INANNA_AI_AGENT.md
index 0000000000000000000000000000000000000000..68db94ed111c321194236a60173c9bde11b9045a 100644
--- a//dev/null
+++ b/README_INANNA_AI_AGENT.md
@@ -0,0 +1,12 @@
+# INANNA AI Agent
+
+This repository provides resources for running the INANNA AI Agent as outlined in the MASTER PLAN.
+
+## Installation
+
+Use `pip` to install the dependencies:
+
+```bash
+pip install -r Requirements_INANNA_AI_AGENT.txt
+```
+
 
EOF
)