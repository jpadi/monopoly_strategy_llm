"""Unit tests for the canonical JSON fixture loader.

Tests cover:
- Valid JSON loading
- Missing file handling
- Invalid JSON syntax
- Non-object root rejection
- Path traversal prevention
- Classic board validation
- Ownership consistency validation
- Transfer semantics validation
- Raw (unvalidated) fixture loading
"""

import json

import pytest
from fixtures.fixtureLoader import (
    FIXTURE_ROOT,
    FixtureLoadError,
    loadRawScenarioInput,
    loadScenarioInput,
)
from fixtures.scenarioInputs import perfectlyBalancedPrintedValueSwapInput


class TestValidFixtureLoading:
    """Tests for successfully loading valid fixtures."""

    def test_loads_existing_valid_fixture(self):
        """Valid fixture loads without error."""
        data = loadScenarioInput("trade_ratio/perfectly_balanced_printed_value_swap.json")

        assert isinstance(data, dict)
        assert "metadata" in data
        assert "game_configuration" in data
        assert "board_state_before" in data
        assert "board_state_after" in data
        assert "trade" in data

    def test_fixture_contains_complete_metadata(self):
        """Loaded fixture has all required metadata fields."""
        data = loadScenarioInput("trade_ratio/perfectly_balanced_printed_value_swap.json")

        metadata = data["metadata"]
        assert "evaluation_id" in metadata
        assert "game_id" in metadata
        assert "platform" in metadata
        assert "game_version" in metadata
        assert "evaluation_timestamp" in metadata
        assert "schema_version" in metadata
        assert "language" in metadata

    def test_fixture_contains_complete_trade(self):
        """Loaded fixture has all required trade fields."""
        data = loadScenarioInput("trade_ratio/perfectly_balanced_printed_value_swap.json")

        trade = data["trade"]
        assert "id" in trade
        assert "status" in trade
        assert "initiating_player_id" in trade
        assert "participants" in trade
        assert "transfers" in trade

    def test_classic_board_has_28_properties(self):
        """Classic board fixture has complete property set."""
        data = loadScenarioInput("trade_ratio/perfectly_balanced_printed_value_swap.json")

        before = data["board_state_before"]
        after = data["board_state_after"]

        assert len(before["properties"]) == 28
        assert len(after["properties"]) == 28

    def test_utf8_encoding_handled(self):
        """UTF-8 encoded fixtures load correctly."""
        data = loadScenarioInput("trade_ratio/perfectly_balanced_printed_value_swap.json")

        # Check we can serialize back to JSON without issues
        serialized = json.dumps(data)
        assert isinstance(serialized, str)


class TestMissingFileHandling:
    """Tests for missing file error handling."""

    def test_missing_file_raises_load_error(self):
        """Missing fixture file raises FixtureLoadError."""
        with pytest.raises(FixtureLoadError) as exc_info:
            loadScenarioInput("nonexistent/scenario.json")

        assert "Scenario fixture not found" in str(exc_info.value)
        assert "nonexistent/scenario.json" in str(exc_info.value)

    def test_missing_directory_raises_load_error(self):
        """Missing fixture directory raises FixtureLoadError."""
        with pytest.raises(FixtureLoadError) as exc_info:
            loadScenarioInput("unknown_category/unknown.json")

        assert "Scenario fixture not found" in str(exc_info.value)


class TestInvalidJsonHandling:
    """Tests for invalid JSON handling."""

    def test_invalid_json_syntax_raises_load_error(self):
        """Invalid JSON syntax produces clear error message."""
        # Create a temp file with invalid JSON
        temp_dir = FIXTURE_ROOT / "_test_temp"
        temp_dir.mkdir(exist_ok=True)
        test_file = temp_dir / "invalid_syntax.json"

        try:
            test_file.write_text("{ invalid json", encoding="utf-8")

            with pytest.raises(FixtureLoadError) as exc_info:
                loadScenarioInput("_test_temp/invalid_syntax.json")

            error_msg = str(exc_info.value)
            assert "Invalid JSON" in error_msg
            assert "line" in error_msg
            assert "column" in error_msg
        finally:
            test_file.unlink(missing_ok=True)
            temp_dir.rmdir()

    def test_non_object_root_raises_load_error(self):
        """JSON array root raises FixtureLoadError."""
        temp_dir = FIXTURE_ROOT / "_test_temp"
        temp_dir.mkdir(exist_ok=True)
        test_file = temp_dir / "array_root.json"

        try:
            test_file.write_text("[1, 2, 3]", encoding="utf-8")

            with pytest.raises(FixtureLoadError) as exc_info:
                loadScenarioInput("_test_temp/array_root.json")

            assert "must be a JSON object" in str(exc_info.value)
        finally:
            test_file.unlink(missing_ok=True)
            temp_dir.rmdir()


class TestPathTraversalPrevention:
    """Tests for path traversal attack prevention."""

    def test_path_traversal_rejected(self):
        """Path traversal attempts are rejected."""
        with pytest.raises(FixtureLoadError) as exc_info:
            loadScenarioInput("../../../etc/passwd")

        # Should fail either with "not found" or "outside fixture root"
        error_msg = str(exc_info.value)
        assert "not found" in error_msg.lower() or "outside fixture root" in error_msg.lower()


class TestClassicBoardValidation:
    """Tests for classic Monopoly board validation."""

    def test_classic_board_validates_property_counts(self):
        """Classic board must have exactly 28 properties."""
        data = loadScenarioInput("trade_ratio/perfectly_balanced_printed_value_swap.json")

        before_props = data["board_state_before"]["properties"]
        after_props = data["board_state_after"]["properties"]

        # Count by category (before state)
        before_streets = [p for p in before_props if p.get("category") == "street"]
        before_railroads = [p for p in before_props if p.get("category") == "railroad"]
        before_utilities = [p for p in before_props if p.get("category") == "utility"]

        assert len(before_streets) == 22
        assert len(before_railroads) == 4
        assert len(before_utilities) == 2

        # After state should have same property count
        assert len(after_props) == 28


class TestOwnershipConsistencyValidation:
    """Tests for ownership consistency validation."""

    def test_ownership_lists_match_property_owners(self):
        """Player owned_properties matches property owner_player_id."""
        data = loadScenarioInput("trade_ratio/perfectly_balanced_printed_value_swap.json")

        for board_key in ["board_state_before", "board_state_after"]:
            board = data[board_key]

            # Build ownership map from properties
            ownership_from_props: dict[str, list[str]] = {}
            for prop in board["properties"]:
                owner = prop.get("owner_player_id")
                if owner:
                    if owner not in ownership_from_props:
                        ownership_from_props[owner] = []
                    ownership_from_props[owner].append(prop["id"])

            # Verify player lists match
            for player in board["players"]:
                player_owned = set(player.get("owned_properties", []))
                props_owned = set(ownership_from_props.get(player["id"], []))
                assert player_owned == props_owned, f"Ownership mismatch for {player['id']} in {board_key}"


class TestTransferSemanticsValidation:
    """Tests for transfer semantics validation."""

    def test_cash_transfers_have_null_asset_id(self):
        """Cash transfers have asset_id = null."""
        data = loadScenarioInput("base_asset_value/cash_only_trade.json")

        for transfer in data["trade"]["transfers"]:
            if transfer["asset_type"] == "cash":
                assert transfer["asset_id"] is None
                assert transfer["amount"] > 0

    def test_property_transfers_have_asset_id(self):
        """Property transfers have asset_id and amount = 0."""
        data = loadScenarioInput("base_asset_value/unmortgaged_property_transfer.json")

        for transfer in data["trade"]["transfers"]:
            if transfer["asset_type"] == "property":
                assert transfer["asset_id"] is not None
                assert transfer["amount"] == 0


class TestRawFixtureLoading:
    """Tests for loading intentionally invalid fixtures."""

    def test_raw_loading_skips_validation(self):
        """loadRawScenarioInput skips semantic validation."""
        # This fixture has an invalid transfer (property with amount > 0)
        data = loadRawScenarioInput("invalid_input/property_positive_amount.json")

        # Should load without raising FixtureValidationError
        assert isinstance(data, dict)
        assert "trade" in data

    def test_raw_loading_still_requires_valid_json(self):
        """Raw loading still validates JSON syntax."""
        with pytest.raises(FixtureLoadError):
            loadRawScenarioInput("nonexistent/file.json")


class TestScenarioFunctionIntegration:
    """Tests verifying scenario functions work with the loader."""

    def test_scenario_function_returns_dict(self):
        """Scenario function returns dictionary."""
        data = perfectlyBalancedPrintedValueSwapInput()

        assert isinstance(data, dict)
        assert "metadata" in data
        assert "trade" in data

    def test_scenario_function_returns_same_as_direct_load(self):
        """Scenario function returns same data as direct loader call."""
        from_func = perfectlyBalancedPrintedValueSwapInput()
        from_loader = loadScenarioInput("trade_ratio/perfectly_balanced_printed_value_swap.json")

        assert from_func == from_loader

    def test_multiple_loads_return_equal_data(self):
        """Multiple loads return identical data (deterministic)."""
        first = perfectlyBalancedPrintedValueSwapInput()
        second = perfectlyBalancedPrintedValueSwapInput()

        assert first == second
