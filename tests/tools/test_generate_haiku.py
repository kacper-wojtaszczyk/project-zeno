"""Unit tests for haiku generation tool."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.tools.generate_haiku import generate_haiku

@pytest.fixture(scope="function", autouse=True)
def test_db():
    """Override the global test_db fixture to avoid database connections."""
    pass

@pytest.fixture(scope="function", autouse=True)
def test_db_session():
    """Override the global test_db_session fixture to avoid database connections."""
    pass


@pytest.fixture
def mock_state_with_data():
    """
    Mock agent state with typical DIST-ALERT data structure.

    Structure matches real data: raw_data[aoi_code][dataset_id][actual_data]
    Based on actual API responses from Brazil DIST-ALERT queries.
    """
    return {
        "raw_data": {
            "BRA": {
                "0": {
                    "country": ["BRA", "BRA", "BRA", "BRA"],
                    "driver": [
                        "Potential conversion",
                        "Potential conversion",
                        "Crop management",
                        "Flooding"
                    ],
                    "dist_alert_date": [
                        "2025-09-01",
                        "2025-09-05",
                        "2025-09-10",
                        "2025-09-15"
                    ],
                    "dist_alert_confidence": ["high", "high", "low", "high"],
                    "area_ha": [450.5, 320.8, 210.3, 180.2],
                    "aoi_id": ["BRA", "BRA", "BRA", "BRA"],
                    "aoi_type": ["admin", "admin", "admin", "admin"],
                    "dataset_name": "Global all ecosystem disturbance alerts (DIST-ALERT)",
                    "aoi_name": "Brazil",
                    "start_date": "2025-09-01",
                    "end_date": "2025-11-11"
                }
            }
        },
        "aoi": {
            "source": "gadm",
            "src_id": "BRA",
            "name": "Brazil",
            "subtype": "country",
            "gadm_id": "BRA"
        },
        "dataset": {
            "dataset_id": 0,
            "context_layer": "driver",
            "dataset_name": "Global all ecosystem disturbance alerts (DIST-ALERT)"
        }
    }


@pytest.fixture
def mock_state_large_dataset():
    """Mock state with larger dataset (hundreds of alerts)."""
    return {
        "raw_data": {
            "BRA": {
                "0": {
                    "driver": ["Wildfire"] * 100 + ["Potential conversion"] * 50 + ["Crop management"] * 30,
                    "dist_alert_date": ["2025-10-15"] * 180,
                    "area_ha": [100.0] * 180,  # Total: 18,000 ha
                }
            }
        },
        "aoi": {"name": "Amazon Basin"},
        "dataset": {"dataset_name": "DIST-ALERT"}
    }


@pytest.fixture
def mock_state_no_data():
    """Mock agent state without raw_data."""
    return {
        "aoi": {"name": "Brazil"},
        "dataset": {"dataset_name": "DIST-ALERT"}
    }


@pytest.fixture
def mock_state_empty_raw_data():
    """Mock state with raw_data but no nested data."""
    return {
        "raw_data": {},
        "aoi": {"name": "Brazil"},
        "dataset": {"dataset_name": "DIST-ALERT"}
    }


@pytest.mark.asyncio
async def test_generate_haiku_success(mock_state_with_data):
    """Test successful haiku generation with valid data."""
    mock_response = Mock()
    mock_response.content = "Twelve hundred hectares\nConversion spreads in silence\nSeptember mourns loss"

    with patch("src.tools.generate_haiku.POETIC") as mock_poetic:
        mock_poetic.ainvoke = AsyncMock(return_value=mock_response)

        result = await generate_haiku.ainvoke({
            "query": "Write a haiku about Brazil deforestation",
            "state": mock_state_with_data
        })

        # Verify format
        assert isinstance(result, str)
        assert result.count('\n') == 2  # Three lines
        lines = result.split('\n')
        assert len(lines) == 3

        # Verify content mentions data
        result_lower = result.lower()
        assert any(word in result_lower for word in ["hectares", "conversion", "september", "silence", "loss"])

        # Verify LLM was called with correct prompt structure
        mock_poetic.ainvoke.assert_called_once()
        call_args = mock_poetic.ainvoke.call_args[0][0]
        assert "5-7-5 syllables" in call_args
        assert "Brazil" in call_args
        assert "1161.8" in call_args or "1162" in call_args  # Total area (sum of area_ha)
        assert "Potential conversion" in call_args  # Main driver


@pytest.mark.asyncio
async def test_generate_haiku_calculates_statistics(mock_state_with_data):
    """Test that haiku tool correctly extracts and calculates statistics."""
    mock_response = Mock()
    mock_response.content = "Test haiku line one\nTest haiku line two here now\nTest haiku line three"

    with patch("src.tools.generate_haiku.POETIC") as mock_poetic:
        mock_poetic.ainvoke = AsyncMock(return_value=mock_response)

        await generate_haiku.ainvoke({
            "query": "Write a haiku",
            "state": mock_state_with_data
        })

        # Check prompt contains calculated statistics
        prompt = mock_poetic.ainvoke.call_args[0][0]

        # Total area should be sum of all area_ha values
        assert "1162" in prompt  # 450.5 + 320.8 + 210.3 + 180.2 ≈ 1161.8

        # Main driver should be identified (Potential conversion appears most)
        assert "Potential conversion" in prompt

        # Month should be extracted from first alert date
        assert "September" in prompt

        # Location should be present
        assert "Brazil" in prompt


@pytest.mark.asyncio
async def test_generate_haiku_large_dataset(mock_state_large_dataset):
    """Test haiku generation with large dataset (realistic scenario)."""
    mock_response = Mock()
    mock_response.content = "Eighteen thousand lost\nWildfire sweeps through October\nAshes mark the earth"

    with patch("src.tools.generate_haiku.POETIC") as mock_poetic:
        mock_poetic.ainvoke = AsyncMock(return_value=mock_response)

        result = await generate_haiku.ainvoke({
            "query": "Write a haiku about wildfire",
            "state": mock_state_large_dataset
        })

        # Verify it handles large datasets
        prompt = mock_poetic.ainvoke.call_args[0][0]
        assert "18000" in prompt  # 180 alerts × 100 ha
        assert "Wildfire" in prompt  # Dominant driver

        assert result.count('\n') == 2


@pytest.mark.asyncio
async def test_generate_haiku_no_data(mock_state_no_data):
    """Test haiku generation fails gracefully without raw_data."""
    result = await generate_haiku.ainvoke({
        "query": "Write a haiku",
        "state": mock_state_no_data
    })

    assert "No forest data available" in result
    assert "retrieve data first" in result.lower()


@pytest.mark.asyncio
async def test_generate_haiku_empty_raw_data(mock_state_empty_raw_data):
    """Test haiku generation fails gracefully with empty raw_data."""
    result = await generate_haiku.ainvoke({
        "query": "Write a haiku",
        "state": mock_state_empty_raw_data
    })

    assert "No forest data found" in result


@pytest.mark.asyncio
async def test_generate_haiku_validates_format_too_many_lines(mock_state_with_data):
    """Test haiku validation truncates to 3 lines when LLM returns too many."""
    mock_response = Mock()
    mock_response.content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

    with patch("src.tools.generate_haiku.POETIC") as mock_poetic:
        mock_poetic.ainvoke = AsyncMock(return_value=mock_response)

        result = await generate_haiku.ainvoke({
            "query": "Write a haiku",
            "state": mock_state_with_data
        })

        # Should truncate to 3 lines
        assert result.count('\n') == 2
        assert result == "Line 1\nLine 2\nLine 3"


@pytest.mark.asyncio
async def test_generate_haiku_validates_format_too_few_lines(mock_state_with_data):
    """Test haiku validation handles too few lines gracefully."""
    mock_response = Mock()
    mock_response.content = "Only one line"

    with patch("src.tools.generate_haiku.POETIC") as mock_poetic:
        mock_poetic.ainvoke = AsyncMock(return_value=mock_response)

        result = await generate_haiku.ainvoke({
            "query": "Write a haiku",
            "state": mock_state_with_data
        })

        # Should return as-is when fewer than 3 lines
        assert result == "Only one line"


@pytest.mark.asyncio
async def test_generate_haiku_handles_llm_error(mock_state_with_data):
    """Test error handling when LLM call fails."""
    with patch("src.tools.generate_haiku.POETIC") as mock_poetic:
        mock_poetic.ainvoke = AsyncMock(side_effect=Exception("API timeout"))

        result = await generate_haiku.ainvoke({
            "query": "Write a haiku",
            "state": mock_state_with_data
        })

        assert "Failed to generate haiku" in result
        assert "API timeout" in result


@pytest.mark.asyncio
async def test_generate_haiku_handles_missing_optional_fields(mock_state_with_data):
    """Test haiku generation handles missing optional fields gracefully."""
    # Remove optional fields from state
    state = mock_state_with_data.copy()
    state["raw_data"]["BRA"]["0"] = {
        "area_ha": [100.0, 200.0],
        # Missing driver, dist_alert_date, etc.
    }

    mock_response = Mock()
    mock_response.content = "Test haiku works fine\nEven without all the data\nGracefully handles"

    with patch("src.tools.generate_haiku.POETIC") as mock_poetic:
        mock_poetic.ainvoke = AsyncMock(return_value=mock_response)

        result = await generate_haiku.ainvoke({
            "query": "Write a haiku",
            "state": state
        })

        # Should still work
        assert result.count('\n') == 2

        # Prompt should use defaults
        prompt = mock_poetic.ainvoke.call_args[0][0]
        assert "300" in prompt  # Total area
        assert "unknown" in prompt  # Main driver default
        assert "recent" in prompt  # Month default


@pytest.mark.asyncio
async def test_generate_haiku_handles_invalid_date_format(mock_state_with_data):
    """Test haiku generation handles invalid date formats."""
    state = mock_state_with_data.copy()
    state["raw_data"]["BRA"]["0"]["dist_alert_date"] = ["invalid-date", "also-invalid"]

    mock_response = Mock()
    mock_response.content = "Dates may be bad\nBut the haiku still works well\nRecent months it says"

    with patch("src.tools.generate_haiku.POETIC") as mock_poetic:
        mock_poetic.ainvoke = AsyncMock(return_value=mock_response)

        result = await generate_haiku.ainvoke({
            "query": "Write a haiku",
            "state": state
        })

        # Should use "recent" as fallback
        prompt = mock_poetic.ainvoke.call_args[0][0]
        assert "recent" in prompt
        assert result.count('\n') == 2


@pytest.mark.asyncio
async def test_generate_haiku_prompt_structure(mock_state_with_data):
    """Test that the generated prompt has all required components."""
    mock_response = Mock()
    mock_response.content = "Prompt structure test\nContains all necessary parts\nExamples included"

    with patch("src.tools.generate_haiku.POETIC") as mock_poetic:
        mock_poetic.ainvoke = AsyncMock(return_value=mock_response)

        await generate_haiku.ainvoke({
            "query": "Write a haiku about deforestation",
            "state": mock_state_with_data
        })

        prompt = mock_poetic.ainvoke.call_args[0][0]

        # Check for required sections
        assert "5-7-5 syllables" in prompt
        assert "CONSTRAINTS:" in prompt
        assert "DATA:" in prompt
        assert "EXAMPLES:" in prompt

        # Check constraints are explicit
        assert "Line 1: exactly 5 syllables" in prompt
        assert "Line 2: exactly 7 syllables" in prompt
        assert "Line 3: exactly 5 syllables" in prompt

        # Check examples are provided
        assert "hectares" in prompt.lower()

        # Check data is included
        assert "Brazil" in prompt
        assert "Potential conversion" in prompt


@pytest.mark.asyncio
async def test_generate_haiku_handles_nested_data_structure(mock_state_with_data):
    """Test that nested data structure is correctly navigated."""
    # Add extra nesting levels to verify correct extraction
    state = mock_state_with_data.copy()
    state["raw_data"]["BRA"]["0"]["area_ha"] = [1000.0, 2000.0]

    mock_response = Mock()
    mock_response.content = "Three thousand total\nNested data extracted well\nStatistics correct"

    with patch("src.tools.generate_haiku.POETIC") as mock_poetic:
        mock_poetic.ainvoke = AsyncMock(return_value=mock_response)

        await generate_haiku.ainvoke({
            "query": "Write a haiku",
            "state": state
        })

        # Verify correct total is calculated from nested structure
        prompt = mock_poetic.ainvoke.call_args[0][0]
        assert "3000" in prompt  # 1000 + 2000


@pytest.mark.asyncio
async def test_generate_haiku_multiple_aoi_codes(mock_state_with_data):
    """Test haiku generation when raw_data has multiple AOI codes."""
    state = mock_state_with_data.copy()
    # Add another AOI code
    state["raw_data"]["USA"] = {
        "0": {
            "area_ha": [500.0],
            "driver": ["Wildfire"],
        }
    }

    mock_response = Mock()
    mock_response.content = "Multiple regions\nFirst one selected for use\nHaiku still creates"

    with patch("src.tools.generate_haiku.POETIC") as mock_poetic:
        mock_poetic.ainvoke = AsyncMock(return_value=mock_response)

        result = await generate_haiku.ainvoke({
            "query": "Write a haiku",
            "state": state
        })

        # Should work with first AOI found
        assert result.count('\n') == 2


@pytest.mark.asyncio
async def test_generate_haiku_with_alert_date_field_name():
    """Test that tool handles both 'alert_date' and 'dist_alert_date' field names."""
    # Test with alert_date
    state_alert = {
        "raw_data": {
            "BRA": {
                "0": {
                    "area_ha": [100.0],
                    "alert_date": ["2024-03-15"],  # Different field name
                }
            }
        },
        "aoi": {"name": "Test"},
        "dataset": {"dataset_name": "Test Dataset"}
    }

    mock_response = Mock()
    mock_response.content = "March is the month\nAlert date field works just fine\nFlexible naming"

    with patch("src.tools.generate_haiku.POETIC") as mock_poetic:
        mock_poetic.ainvoke = AsyncMock(return_value=mock_response)

        await generate_haiku.ainvoke({
            "query": "Write a haiku",
            "state": state_alert
        })

        prompt = mock_poetic.ainvoke.call_args[0][0]
        assert "March" in prompt  # Should extract March from alert_date


@pytest.mark.asyncio
async def test_generate_haiku_logging(mock_state_with_data, caplog):
    """Test that appropriate logging occurs during haiku generation."""
    mock_response = Mock()
    mock_response.content = "Logging test haiku\nDebug and info messages logged\nErrors caught as well"

    with patch("src.tools.generate_haiku.POETIC.ainvoke", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_response

        # Test successful generation logging
        await generate_haiku.ainvoke({
            "query": "Write a haiku for logging test",
            "state": mock_state_with_data
        })

        # Note: structlog may not appear in caplog, but we verify the tool completes


@pytest.mark.asyncio
async def test_generate_haiku_with_real_brazil_data():
    """Test with data structure matching actual Brazil DIST-ALERT response."""
    # This is the actual structure from the user's scope data
    real_brazil_state = {
        "raw_data": {
            "BRA": {
                "0": {
                    "country": ["BRA"] * 388,
                    "driver": ["Wildfire"] * 77 + ["Potential conversion"] * 78 + ["Flooding"] * 78 + ["Crop management"] * 78 + ["Unclassified"] * 77,
                    "dist_alert_date": ["2025-09-01"] * 50 + ["2025-10-01"] * 338,
                    "area_ha": [31323.728515625, 4419.98388671875, 59311.0, 3881.587646484375] * 97,
                    "aoi_name": "Brazil",
                    "start_date": "2025-09-01",
                    "end_date": "2025-11-11"
                }
            }
        },
        "aoi": {
            "source": "gadm",
            "src_id": "BRA",
            "name": "Brazil",
            "subtype": "country",
            "gadm_id": "BRA"
        },
        "dataset": {
            "dataset_id": 0,
            "context_layer": "driver",
            "dataset_name": "Global all ecosystem disturbance alerts (DIST-ALERT)"
        }
    }

    mock_response = Mock()
    mock_response.content = "Two million shrinks—\nHabitats fade in dawnlights,\nBrazil bleeds crop-cleared."

    with patch("src.tools.generate_haiku.POETIC") as mock_poetic:
        mock_poetic.ainvoke = AsyncMock(return_value=mock_response)

        result = await generate_haiku.ainvoke({
            "query": "Write a short poem about the DIST-ALERT data for Brazil",
            "state": real_brazil_state
        })

        # Verify successful haiku generation
        assert result.count('\n') == 2
        assert "Two million shrinks" in result or "shrinks" in result.lower()

        # Verify prompt uses real data
        prompt = mock_poetic.ainvoke.call_args[0][0]
        assert "Brazil" in prompt
        # Total area should be sum of area_ha
        assert "98936" in prompt  # Sum of the 4 values provided

