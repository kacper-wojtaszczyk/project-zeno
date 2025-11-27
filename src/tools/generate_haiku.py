"""
Haiku generation tool for forest change narratives.
Transforms quantitative forest loss data into 5-7-5 syllable poetic form.
"""

from typing import Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from src.utils.llms import POETIC
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


@tool("generate_haiku")
async def generate_haiku(
    query: str,
    state: Annotated[dict, InjectedState]
) -> str:
    """
    Generate a 5-7-5 syllable haiku about forest loss data.

    Use when user asks for: haiku, poem, poetry, poetic interpretation, creative format

    Args:
        query: User's original query
        state: Agent state with raw_data, aoi, dataset

    Returns:
        Three-line haiku (5-7-5 syllables)

    Example:
        "Twelve thousand hectares / Conversion spreads like fire / October's silence"
    """
    logger.info("GENERATE-HAIKU-TOOL invoked", query=query)

    # Extract data from state
    raw_data = state.get("raw_data")
    if not raw_data:
        return "No forest data available. Please retrieve data first using pick_aoi, pick_dataset, and pull_data."

    aoi = state.get("aoi", {})
    aoi_name = aoi.get("name", "unknown location")

    dataset = state.get("dataset", {})
    dataset_name = dataset.get("dataset_name", "forest change")

    # Navigate nested raw_data structure: raw_data[aoi_code][dataset_id]
    # The structure is: {"BRA": {"0": {actual_data}}}
    actual_data = None
    for aoi_code, datasets in raw_data.items():
        for dataset_id, data in datasets.items():
            actual_data = data
            break
        if actual_data:
            break

    if not actual_data:
        return "No forest data found in raw_data structure."

    # Calculate statistics
    area_ha = actual_data.get("area_ha", [])
    total_area = sum(area_ha) if area_ha else 0

    # Identify main driver
    drivers = actual_data.get("driver", [])
    if drivers:
        from collections import Counter
        driver_counts = Counter(drivers)
        main_driver = driver_counts.most_common(1)[0][0] if driver_counts else "unknown"
    else:
        main_driver = "unknown"

    # Get temporal context - try both possible field names
    alert_dates = actual_data.get("alert_date") or actual_data.get("dist_alert_date", [])
    if alert_dates:
        import datetime
        try:
            first_date = datetime.datetime.strptime(alert_dates[0], "%Y-%m-%d")
            month_name = first_date.strftime("%B")
        except (ValueError, IndexError):
            month_name = "recent"
    else:
        month_name = "recent"

    logger.debug(
        "Extracted haiku context",
        aoi_name=aoi_name,
        total_area=total_area,
        main_driver=main_driver,
        month=month_name
    )

    # Generate haiku
    haiku_prompt = f"""You are a master haiku poet. Create a haiku (exactly 5-7-5 syllables) about forest loss.

CONSTRAINTS:
- Line 1: exactly 5 syllables
- Line 2: exactly 7 syllables
- Line 3: exactly 5 syllables
- Use concrete, sensory imagery
- Make it data-driven. reference the location, area lost, main cause, and time period (not necessarily directly, can be metaphoric).
- Evoke loss and melancholy
- NO explanations, ONLY the haiku

DATA:
- Location: {aoi_name}
- Total area lost: {total_area:.0f} hectares
- Main cause: {main_driver}
- Time period: {month_name}
- Dataset: {dataset_name}

EXAMPLES:
"Twelve thousand hectares / Conversion spreads through silence / October weeps"
"Fire-scarred earth remains / Seven hundred hectares gone / Smoke obscures the stars"

Now create a haiku about this specific data. Return ONLY the haiku, nothing else.
"""

    try:
        logger.debug("Calling POETIC model for haiku generation")
        response = await POETIC.ainvoke(haiku_prompt)
        haiku = response.content.strip()

        # Validate format (3 lines)
        lines = haiku.split('\n')
        if len(lines) != 3:
            logger.warning("Generated haiku doesn't have 3 lines", haiku=haiku, line_count=len(lines))
            haiku = '\n'.join(lines[:3]) if len(lines) > 3 else haiku

        logger.info("Successfully generated haiku", haiku=haiku)
        return haiku

    except Exception as e:
        error_msg = f"Failed to generate haiku: {str(e)}"
        logger.error("Haiku generation failed", error=str(e), exc_info=True)
        return error_msg
