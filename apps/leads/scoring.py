import json
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)

STAGES_BASE_PATH = Path(__file__).resolve().parents[2] / "stages"
logger.debug(f"Using stages base path: {STAGES_BASE_PATH}")

def normalize(text: str) -> str:
    return (
        text.strip()
        .lower()
        .replace("–", "-")
        .replace("—", "-")
    )

# Resolve lead score based on stage and substage json files
def resolve_lead_score(stage: Optional[str], substage: Optional[str] = None) -> int:
    try:
        if not stage:
            logger.warning("No stage provided, defaulting score to 0.")
            return 0
        stage_path = STAGES_BASE_PATH / stage
        if not stage_path.exists():
            logger.warning(f"Stage '{stage}' not found.")
            return 0
        if substage:
            for substages_file in stage_path.rglob("substages.json"):
                with open(substages_file, "r", encoding="utf-8") as f:
                    substages = json.load(f)

                for item in substages:
                    if item.get("status") == substage:
                        score = item.get("score", 0)
                        logger.info(
                            f"Resolved lead score={score} "
                            f"for stage='{stage}', substage='{substage}'")
                        return score
            logger.warning(
                f"No matching substage '{substage}' found for stage '{stage}'. Falling back to stage score.")
            
            
        
        # Fallback to stage score if substage not found or not provided
        for stage_file in stage_path.rglob("*.json"):
            with open(stage_file, "r", encoding="utf-8") as f:
                stage_data = json.load(f)


            if isinstance(stage_data, dict) and "score" in stage_data:
                score = stage_data.get("score", 0)
                logger.info(
                    f"Resolved stage-level score={score} for stage='{stage}'"
                )
                return score

        logger.warning(
            f"No matching substage '{substage}' found for stage '{stage}', defaulting score to 0.")
        return 0
        
    except Exception as e:
        logger.exception("Failed to resolve lead score")
        return 0