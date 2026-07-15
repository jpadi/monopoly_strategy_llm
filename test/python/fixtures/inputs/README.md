# Canonical JSON Test Fixtures

This directory contains canonical JSON input fixtures for Static Evaluator tests.

## Design Philosophy

### JSON is the Source of Truth

Every committed test scenario is stored as a complete canonical JSON file. The JSON contains:

- Complete metadata (evaluation_id, game_id, platform, timestamps, etc.)
- Game configuration (ruleset, house/hotel counts, mortgage rates, etc.)
- Full board state before trade (all 28 properties for classic, all players)
- Full board state after trade (mirrors before with trade effects applied)
- Complete trade structure (participants, transfers)

### One Python Function per Scenario

Each JSON fixture has a corresponding Python function in `scenarioInputs.py` that:

1. **Documents** the scenario (docstring explaining the test purpose)
2. **Identifies** the JSON fixture path
3. **Loads** the fixture via the shared loader

Python functions do **not** procedurally construct scenarios.

### Complete Classic Boards

Every fixture declaring `ruleset_name = classic_monopoly` contains:

- 28 purchasable properties total
- 22 streets across 8 color groups
- 4 railroads
- 2 utilities

Unowned properties are explicit with `owner_player_id = null`.

### Ownership Consistency

The JSON must be internally consistent:

- `player.owned_properties` must match `property.owner_player_id`
- No silent synchronization occurs at load time
- Inconsistencies produce validation errors

### Transfer Semantics

#### Cash Transfers
```json
{
  "asset_type": "cash",
  "asset_id": null,
  "amount": 100
}
```

#### Property Transfers
```json
{
  "asset_type": "property",
  "asset_id": "property_st_james",
  "amount": 0
}
```

## Directory Structure

```
inputs/
├── trade_ratio/           # Trade ratio boundary scenarios
├── base_asset_value/      # Asset valuation scenarios
├── development_capability/# Monopoly development scenarios
├── railroad_value/        # Railroad ownership scenarios
├── blocking_value/        # Strategic blocking scenarios
├── risk_coverage/         # Risk calculation scenarios
├── automatic_flags/       # Flag trigger scenarios
├── initiator_adjustment/  # Initiator rule scenarios
├── final_classification/  # Classification scenarios
├── invalid_input/         # Intentionally invalid fixtures
└── custom_board/          # Non-classic board scenarios
```

## Loading Fixtures

### Valid Scenarios
```python
from fixtures.fixtureLoader import loadScenarioInput

data = loadScenarioInput("trade_ratio/ratio_exactly_three.json")
```

### Invalid Scenarios (Skip Validation)
```python
from fixtures.fixtureLoader import loadRawScenarioInput

data = loadRawScenarioInput("invalid_input/property_positive_amount.json")
```

### Via Named Functions (Recommended)
```python
from fixtures.scenarioInputs import ratioExactlyThreeInput

data = ratioExactlyThreeInput()
```

## Adding a New Scenario

1. **Identify** the normative behavior to test
2. **Create** the complete JSON fixture with:
   - Explicit metadata (deterministic timestamp)
   - Complete board state (all 28 properties for classic)
   - Consistent ownership
   - Canonical transfer semantics
3. **Add** the Python function to `scenarioInputs.py`:
   ```python
   def newScenarioInput() -> dict[str, Any]:
       """Brief description.
       
       Trade setup and expected behavior.
       """
       return loadScenarioInput("category/new_scenario.json")
   ```
4. **Validate** the fixture loads without errors
5. **Write** the test with expected value assertions
6. **Run** the full test suite

## Validation Rules

The fixture loader validates:

1. JSON syntax and UTF-8 encoding
2. Root is a JSON object
3. Required sections present: metadata, game_configuration, board_state_before, board_state_after, trade
4. Metadata completeness
5. Trade structure
6. Transfer semantics (cash/property rules)
7. Classic board completeness (28 properties)
8. Ownership consistency
9. Before/after property ID parity

## Invalid Fixtures

Intentionally invalid fixtures test error handling. Each contains **exactly one** defect:

| Fixture | Defect |
|---------|--------|
| `property_positive_amount.json` | Property with amount > 0 |
| `cash_zero_amount.json` | Cash with amount = 0 |
| `cash_with_asset_id.json` | Cash with non-null asset_id |
| `property_missing_asset_id.json` | Property with null asset_id |
| `multi_party_trade.json` | 3+ participants |
| `non_tradable_property.json` | is_tradable = false |

## Expected Output Separation

Input fixtures contain only evaluator input. Expected output values belong in:

- Test assertions
- Separate `expected/` directory (if needed)

Do not mix inputs with expected outputs.
