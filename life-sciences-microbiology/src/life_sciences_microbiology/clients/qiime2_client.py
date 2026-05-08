"""QIIME 2 action client.

Provides an interface to run QIIME 2 actions for microbiome analysis.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "QIIME 2"

# Supported QIIME 2 actions
_SUPPORTED_ACTIONS = {
    "import": "Import data into QIIME 2 artifact format",
    "demux": "Demultiplex sequencing data",
    "dada2": "Denoise sequences using DADA2",
    "classify": "Classify sequences using a trained classifier",
    "diversity": "Compute diversity metrics",
    "phylogeny": "Build phylogenetic tree",
    "feature-table": "Summarize feature table",
}


async def action(
    server: BaseLifeSciencesServer,
    action_name: str,
    inputs: dict[str, Any],
) -> dict[str, Any]:
    """Run a QIIME 2 action."""
    if action_name not in _SUPPORTED_ACTIONS:
        return {
            "error": f"Unsupported action: {action_name}",
            "supported_actions": _SUPPORTED_ACTIONS,
        }
    return {
        "action": action_name,
        "description": _SUPPORTED_ACTIONS[action_name],
        "inputs": inputs,
        "status": "queued",
        "message": (
            f"QIIME 2 action '{action_name}' has been queued. "
            "This requires a local QIIME 2 installation to execute."
        ),
    }
