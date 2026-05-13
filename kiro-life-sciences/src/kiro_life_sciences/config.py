"""Configuration constants for the Kiro for Life Sciences bundle."""

from pathlib import Path

# ---------------------------------------------------------------------------
# Bundle identity
# ---------------------------------------------------------------------------
BUNDLE_NAME: str = "kiro-life-sciences"
BUNDLE_VERSION: str = "0.1.0"
BUNDLE_DESCRIPTION: str = (
    "A unified Kiro Power that provides life sciences developers, "
    "bioinformaticians, clinical researchers, and other life sciences "
    "professionals with a comprehensive suite of tools, databases, "
    "pipelines, and skills."
)

# ---------------------------------------------------------------------------
# Paths (relative to the Power root)
# ---------------------------------------------------------------------------
POWER_ROOT: Path = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR: Path = POWER_ROOT / "skills"
STEERING_DIR: Path = POWER_ROOT / "steering"
MANIFEST_PATH: Path = POWER_ROOT / "bundle-manifest.json"

# ---------------------------------------------------------------------------
# MCP server naming convention
# ---------------------------------------------------------------------------
MCP_SERVER_PREFIX: str = "life-sciences-"
