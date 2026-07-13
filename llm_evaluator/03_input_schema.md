# Monopoly Trade Evaluation Input Schema

Version: 1.0

## Purpose

This document defines a concrete structured input schema for the Monopoly Trade Evaluation System.

The schema translates the conceptual input model into a practical data structure that can be serialized as JSON.

The schema should allow the evaluator to reconstruct the complete game state, understand the trade being evaluated, review supporting evidence, and compare the trade against documented Decision Pattern Profiles.

The input schema is designed around stable identifiers.

Players, properties, assets, trades, algorithms, and profiles should all use identifiers that remain consistent across the full input.

---

## Top-Level Structure

The input should be a single JSON object with the following top-level sections.

```json
{
  "metadata": {},
  "game_configuration": {},
  "board_state_before": {},
  "trade": {},
  "board_state_after": {},
  "static_analysis_control": {},
  "static_algorithm_evidence": [],
  "player_profiles": [],
  "decision_pattern_profiles": []
}
```

---

## Required Sections

The following sections are required for a complete evaluation:

```text
metadata
game_configuration
board_state_before
trade
board_state_after
```

These sections provide the minimum information needed to understand the game and evaluate the competitive impact of the trade.

---

## Optional Sections

The following sections are optional:

```text
static_analysis_control
static_algorithm_evidence
player_profiles
decision_pattern_profiles
```

Optional sections improve context and explanation quality.

They should be included whenever available.

Missing optional sections should not prevent evaluation.

When `static_analysis_control` is absent, the evaluator behaves exactly as if `{ "mode": "auto", "fallback_allowed": false }` had been supplied.

---

## Identifier Rules

All important entities should use stable identifiers.

Examples:

```text
player_1
player_2
property_oriental_avenue
property_reading_railroad
trade_000123
static_algorithm_v1
decision_pattern_liquidity_first
```

Identifiers should be:

- stable;
- unique within their entity type;
- reused consistently across all sections;
- machine-readable;
- not dependent on display names.

Display names may be included for readability, but evaluation should rely on identifiers whenever possible.

## Metadata

The Metadata section contains general information describing the evaluation.

Metadata identifies the evaluation but should never influence the competitive classification.

Its purpose is traceability, auditing, logging, reproducibility, and future integration with external systems.

---

### JSON Structure

```json
{
  "evaluation_id": "",
  "game_id": "",
  "platform": "",
  "game_version": "",
  "evaluation_timestamp": "",
  "schema_version": "",
  "language": ""
}
```

---

### Field Definitions

#### evaluation_id

Unique identifier for the current evaluation.

Every evaluation should have a unique identifier.

This identifier is primarily intended for logging and future review.

---

#### game_id

Unique identifier of the Monopoly game being evaluated.

Multiple trade evaluations may reference the same game.

---

#### platform

Identifies the Monopoly platform or implementation.

Examples include:

- Marmalade
- Monopoly Plus
- Tabletop Simulator
- Custom Engine

This field helps interpret platform-specific Game Configuration values.

---

#### game_version

Version of the Monopoly implementation.

Different versions may introduce rule changes.

---

#### evaluation_timestamp

Timestamp indicating when the evaluation was performed.

This field is informational only.

---

#### schema_version

Version of the Input Schema specification.

Allows backward compatibility when the schema evolves.

---

#### language

Preferred language for textual explanations.

This field affects only the generated report.

It should never influence the competitive evaluation.

## Game Configuration

The Game Configuration section describes rule values and platform-specific settings that may affect the evaluation.

The evaluator is expected to understand standard Monopoly rules and strategy.

Game Configuration should only define values, rules, or behaviours that may vary between implementations or platforms.

Whenever Game Configuration provides a value, that value overrides the evaluator's default Monopoly knowledge.

---

### JSON Structure

```json
{
  "ruleset_name": "",
  "ruleset_version": "",
  "starting_cash": 1500,
  "salary_for_passing_go": 200,
  "income_tax_amount": 200,
  "luxury_tax_amount": 100,
  "total_houses": 32,
  "total_hotels": 12,
  "mortgage_interest_rate": 0.10,
  "must_pay_interest_on_mortgaged_property_transfer": true,
  "can_keep_transferred_property_mortgaged_after_paying_interest": true,
  "auction_if_property_declined": true,
  "even_building_required": true,
  "even_selling_required": true,
  "house_sell_back_ratio": 0.50,
  "hotel_sell_back_ratio": 0.50,
  "hotel_liquidation_basis": "houses_plus_hotel",
  "building_allowed_with_mortgaged_group_member": false,
  "group_rent_requires_all_members_unmortgaged": false,
  "group_multipliers": {},
  "free_parking_rule": "no_bonus",
  "jail": {
    "bail_amount": 50,
    "max_turns_before_forced_payment": 3,
    "allow_get_out_of_jail_card": true
  },
  "custom_rules": []
}
```

---

### Field Definitions

#### ruleset_name

Name of the rule set used by the game.

Examples:

- `classic_monopoly`
- `platform_default`
- `custom_rules`

---

#### ruleset_version

Version of the rule set.

This helps distinguish different platform or house-rule variants.

---

#### starting_cash

Cash each player receives at the beginning of the game.

---

#### salary_for_passing_go

Cash received when a player passes or lands on GO, if applicable.

---

#### income_tax_amount

Amount paid when landing on Income Tax.

If the platform uses a different tax formula, that formula should be described in `custom_rules`.

---

#### luxury_tax_amount

Amount paid when landing on Luxury Tax.

---

#### total_houses

Total number of houses available in the game.

This is important for evaluating house shortages and house-control strategies.

---

#### total_hotels

Total number of hotels available in the game.

---

#### mortgage_interest_rate

Interest rate applied when unmortgaging properties or receiving mortgaged properties, depending on the platform rules.

---

#### must_pay_interest_on_mortgaged_property_transfer

Whether a player receiving a mortgaged property must immediately pay mortgage interest.

---

#### can_keep_transferred_property_mortgaged_after_paying_interest

Whether a player receiving a mortgaged property may keep it mortgaged after paying the required interest.

---

#### auction_if_property_declined

Whether a property is auctioned if the player who lands on it declines to buy it.

---

#### even_building_required

Whether houses must be built evenly across a color group.

---

#### even_selling_required

Whether houses and hotels must be sold evenly across a color group.

---

#### house_sell_back_ratio

Fraction of `house_cost` recovered when a house is sold back to the bank.

The classic Monopoly default is `0.50`.

Evaluators use this value to compute the recoverable liquidation value of houses received through a trade.

---

#### hotel_sell_back_ratio

Fraction of a hotel's construction cost recovered when a hotel is liquidated.

The classic Monopoly default is `0.50`.

---

#### hotel_liquidation_basis

How a hotel's construction cost is composed for liquidation purposes.

Values include:

- `houses_plus_hotel` — four houses plus the hotel upgrade cost (classic);
- `hotel_cost_only` — the hotel upgrade cost only;
- `explicit` — the per-property `hotel_liquidation_value` field supplies the recoverable value directly.

Evaluators must not assume any particular composition unless this field defines it.

---

#### building_allowed_with_mortgaged_group_member

Whether a player may build on a color group while one or more of its properties are mortgaged.

The classic Monopoly default is `false`.

When `false`, capability simulations must pay the required unmortgage costs before simulating construction.

---

#### group_rent_requires_all_members_unmortgaged

Whether group rent bonuses and development rents require every property in the group to be unmortgaged.

The classic Monopoly default is `false`: only the landed-on property must be unmortgaged to collect rent.

---

#### group_multipliers

Optional map of `group_id` to an explicit Group Strategic Multiplier supplied by the platform.

When present for a group, this value takes priority over any evaluator default.

This is the primary mechanism for describing the strategic strength of custom street groups.

---

#### free_parking_rule

Describes the Free Parking rule.

Examples:

- `no_bonus`
- `collect_taxes`
- `custom`

---

#### jail

Jail-related configuration.

Includes bail amount, maximum jail turns, and Get Out of Jail card support.

---

#### custom_rules

Array of any additional platform-specific or house-rule behaviours that may affect evaluation.

Each custom rule should be described clearly enough that the evaluator can understand its strategic impact.

## Board State

The Board State represents the complete factual state of the Monopoly game at a specific moment.

This schema is used by both `board_state_before` and `board_state_after`.

For trades that have not been executed (for example, trades with status `proposed`), `board_state_after` contains the projected state the game would reach if the trade were executed.

It is the primary source of evidence used during trade evaluation.

The Board State should contain only objective facts.

It should never contain strategic interpretations, recommendations, or conclusions.

The evaluator is responsible for interpreting the Board State.

---

### JSON Structure

```json
{
  "players": [],
  "properties": [],
  "tradable_assets": [],
  "game_state": {}
}
```

---

### Components

#### players

Contains every active player currently participating in the game.

Each player should be described using the Player schema.

Every player should appear exactly once.

---

#### properties

Contains every purchasable board property.

Each property should be described using the Property schema.

Every property should appear exactly once.

The collection should include:

- street properties;
- railroads;
- utilities.

Ownership is defined inside each Property object.

---

#### tradable_assets

Contains tradable assets that are not board properties.

Examples include:

- Get Out of Jail Free cards;
- platform-specific tradable cards;
- custom tradable assets.

Cash should normally be represented inside each Player object.

However, cash transfers must also be explicitly represented inside Trade Information.

---

#### game_state

Contains information that belongs to the game itself rather than to any individual player or property.

Examples include:

- available houses;
- available hotels;
- current turn;
- active player count;
- eliminated players;
- current game phase;
- other global information required for evaluation.

---

### Design Principles

The Board State should satisfy the following principles.

#### Complete

Every fact required to reconstruct the game should exist somewhere inside the Board State.

---

#### Clear

Some redundancy is acceptable if it helps the evaluator understand the game more reliably.

Clarity is more important than minimizing tokens.

---

#### Deterministic

Two identical Board States should always produce identical factual information.

---

#### Factual

The Board State should never include:

- strategic opinions;
- player rankings;
- estimated winners;
- trade recommendations;
- competitive classifications.

Those belong to the evaluator.

---

#### Stable

Every object inside the Board State should use stable identifiers.

These identifiers should remain consistent throughout the complete input.

## Player

The Player object describes the complete current state of a single player.

Every active player should appear exactly once within the Board State.

A Player object contains only factual information describing the player's current situation.

It should never contain strategic opinions, evaluations, recommendations, or predictions.

---

### JSON Structure

```json
{
  "id": "",
  "display_name": "",
  "status": "active",
  "turn_order": 0,
  "board_position": 0,
  "cash": 1500,
  "in_jail": false,
  "jail_turns": 0,
  "get_out_of_jail_free_cards": 0,
  "owned_properties": [],
  "owned_tradable_assets": [],
  "mortgaged_properties": [],
  "statistics": {}
}
```

---

### Field Definitions

#### id

Unique identifier of the player.

The identifier must remain stable throughout the complete evaluation.

All references to this player should use this identifier.

---

#### display_name

Human-readable player name.

This field exists only for readability.

The evaluator should always identify players using the player identifier.

---

#### status

Current player status.

Possible values include:

- active
- eliminated
- bankrupt
- disconnected (if supported by the platform)

---

#### turn_order

The player's current position in the turn sequence.

Turn order is important because it affects:

- immediate risk;
- development opportunities;
- negotiation timing;
- expected future play.

---

#### board_position

Current board position.

The position should uniquely identify the player's current location on the Monopoly board.

---

#### cash

Current immediately available cash.

Cash should represent only liquid money.

It should not include:

- mortgage capacity;
- property value;
- estimated net worth;
- future rent.

---

#### in_jail

Indicates whether the player is currently in jail.

---

#### jail_turns

Number of consecutive turns already spent in jail.

This allows the evaluator to understand how soon the player may leave jail.

---

#### get_out_of_jail_free_cards

Number of Get Out of Jail Free cards currently owned by the player.

---

#### owned_properties

List of Property identifiers currently owned by the player.

These identifiers reference Property objects defined elsewhere in the Board State.

---

#### owned_tradable_assets

List of Tradable Asset identifiers currently owned by the player.

These identifiers reference objects defined in the Tradable Assets section.

---

#### mortgaged_properties

List of Property identifiers that are currently mortgaged.

This field exists for convenience and quick access.

The authoritative mortgage state remains the corresponding Property object.

---

#### statistics

Optional precomputed factual summaries.

Examples include:

- total property count;
- monopoly count;
- railroad count;
- utility count;
- developed property count;
- mortgaged property count;
- available mortgage capacity;
- total asset value.

Statistics should summarize factual information only.

Strategic evaluation belongs to the evaluator.

## Property

The Property object describes a single purchasable board property.

This includes street properties, railroads, and utilities.

Every purchasable property should appear exactly once within the Board State.

A Property object contains factual information only.

It should never contain strategic opinions, evaluations, recommendations, or predictions.

---

### JSON Structure

```json
{
  "id": "",
  "display_name": "",
  "category": "street",
  "board_position": 0,
  "group_id": "",
  "owner_player_id": null,
  "purchase_price": 0,
  "mortgage_value": 0,
  "unmortgage_cost": 0,
  "is_mortgaged": false,
  "is_tradable": true,
  "houses": 0,
  "has_hotel": false,
  "house_cost": 0,
  "hotel_cost": 0,
  "hotel_liquidation_value": null,
  "rent_table": {},
  "statistics": {}
}
```

---

### Field Definitions

#### id

Unique identifier of the property.

The identifier must remain stable throughout the complete evaluation.

All references to this property should use this identifier.

---

#### display_name

Human-readable property name.

This field exists only for readability.

The evaluator should always identify properties using the property identifier.

---

#### category

Type of property.

Common values include:

- street
- railroad
- utility

The category affects how the property creates competitive value.

---

#### board_position

Position of the property on the Monopoly board.

---

#### group_id

Identifier of the group this property belongs to.

Examples include:

- brown
- light_blue
- pink
- orange
- red
- yellow
- green
- dark_blue
- railroad
- utility

Group membership is important for monopoly completion, blocking, development, and rent evaluation.

---

#### owner_player_id

Identifier of the current owner.

Use `null` if the property is currently unowned or owned by the bank.

---

#### purchase_price

Cost to buy the property from the bank.

---

#### mortgage_value

Cash received when mortgaging the property.

---

#### unmortgage_cost

Total cost required to unmortgage the property.

This should include any required interest according to the Game Configuration.

---

#### is_mortgaged

Whether the property is currently mortgaged.

---

#### is_tradable

Whether the property can currently be traded.

Some platforms or game states may restrict trading.

---

#### houses

Number of houses currently built on the property.

For railroads and utilities, use `0`.

---

#### has_hotel

Whether the property currently has a hotel.

For railroads and utilities, use `false`.

---

#### house_cost

Cost to build one house on this property.

For railroads and utilities, use `0` or `null`.

---

#### hotel_cost

Cost to upgrade from four houses to one hotel.

For railroads and utilities, use `0` or `null`.

---

#### hotel_liquidation_value

Optional explicit recoverable value of the hotel on this property.

When present, this value overrides any liquidation value computed from `game_configuration.hotel_sell_back_ratio` and `hotel_liquidation_basis`, following the same precedent as `unmortgage_cost` overriding the interest formula.

For properties without a hotel, and for railroads and utilities, use `null`.

---

#### rent_table

Exact rent values for this property.

For street properties, this may include rent by development level.

For railroads and utilities, this may include the platform-specific rent rules or multipliers.

The evaluator must use the provided rent values whenever available.

---

#### statistics

Optional precomputed factual summaries.

Examples include:

- is_part_of_complete_group;
- group_owner_player_id;
- group_property_count;
- owned_group_property_count_by_owner;
- development_level;
- maximum_possible_rent;
- current_rent_if_landed_on.

Statistics should summarize factual information only.

Strategic evaluation belongs to the evaluator.

## Tradable Asset

The Tradable Asset object describes any tradable game asset that is not a board property.

Tradable Assets allow the input schema to support Monopoly variants without modifying the evaluator.

Every Tradable Asset should appear exactly once within the Board State.

Tradable Assets contain factual information only.

They should never contain strategic opinions, evaluations, recommendations, or predictions.

---

### JSON Structure

```json
{
  "id": "",
  "display_name": "",
  "asset_type": "",
  "owner_player_id": null,
  "is_tradable": true,
  "quantity": 1,
  "metadata": {},
  "statistics": {}
}
```

---

### Field Definitions

#### id

Unique identifier of the asset.

The identifier must remain stable throughout the complete evaluation.

All references to this asset should use this identifier.

---

#### display_name

Human-readable name of the asset.

Examples include:

- Get Out of Jail Free Card
- Community Chest Get Out of Jail Free Card
- Chance Get Out of Jail Free Card

---

#### asset_type

Type of tradable asset.

Examples include:

- get_out_of_jail_card
- custom_asset

Additional asset types may be introduced by different Monopoly implementations.

---

#### owner_player_id

Identifier of the player currently owning the asset.

Use `null` if the asset is currently owned by the bank or is otherwise unavailable.

---

#### is_tradable

Indicates whether the asset may currently be included in a trade.

---

#### quantity

Number of identical assets represented by this object.

Most Monopoly assets will use a value of `1`.

---

#### metadata

Optional implementation-specific information.

This field allows Monopoly implementations to attach additional factual information without modifying the schema.

The evaluator should ignore unknown metadata fields unless documented by the Game Configuration.

---

#### statistics

Optional precomputed factual summaries.

Examples include:

- times_used;
- remaining_uses;
- implementation-specific counters.

Statistics should summarize factual information only.

Strategic evaluation belongs to the evaluator.

## Trade

The Trade object describes the complete exchange being evaluated.

A Trade represents the agreement between two or more players.

It contains only factual information describing the proposed or completed exchange.

It should never contain strategic opinions, evaluations, recommendations, or predictions.

---

### JSON Structure

```json
{
  "id": "",
  "status": "completed",
  "initiating_player_id": "",
  "participants": [],
  "transfers": [],
  "metadata": {},
  "statistics": {}
}
```

---

### Field Definitions

#### id

Unique identifier of the trade.

The identifier must remain stable throughout the complete evaluation.

---

#### status

Current trade status.

Common values include:

- proposed
- accepted
- completed
- rejected
- cancelled

---

#### initiating_player_id

Identifier of the player who initiated the trade.

This field must never influence the Judge's Competitive Classification.

The competitive evaluation should depend on the trade itself rather than who proposed it.

Deterministic algorithms may use this field for the flag adjustment defined by the Static Algorithm Specification (Step 10 — Trade Initiator Evaluation).

---

#### participants

List of every player participating in the trade.

Each participant should reference a valid Player identifier.

The evaluator should be able to determine every player directly involved.

---

#### transfers

Complete list of every asset transferred as part of the trade.

Each transfer should be represented explicitly.

Buildings on a transferred property move with it, exactly as reflected in the authoritative board states. Trade legality, including whether developed properties may be transferred, is the responsibility of the platform and its Game Configuration.

A transfer of a property with `is_tradable = false` is a state-consistency error; evaluators record it rather than silently treating the transfer as valid.

Nothing exchanged should be implied.

---

#### metadata

Optional implementation-specific information.

This field allows Monopoly platforms to include additional factual information without modifying the schema.

Unknown metadata fields should be ignored unless documented by the Game Configuration.

---

#### statistics

Optional precomputed factual summaries.

Examples include:

- total_assets_transferred;
- total_cash_transferred;
- total_properties_transferred;
- total_cards_transferred.

Statistics summarize factual information only.

Strategic evaluation belongs to the evaluator.

---

### Design Principles

A Trade should completely describe the exchange.

The evaluator should never need to compare Board States simply to determine what was exchanged.

The Trade object should be self-contained.

Board States are used to understand the consequences of the trade.

The Trade object is used to understand the exchange itself.

Every transferred asset should appear exactly once.

Every transfer should identify:

- the sender;
- the receiver;
- the transferred object.

No transfer should require inference by the evaluator.

## Transfer

The Transfer object describes a single asset movement inside a Trade.

Every item exchanged in a trade should be represented as one Transfer object.

A Trade may contain one transfer or many transfers.

Each Transfer contains only factual information.

It should never contain strategic opinions, evaluations, recommendations, or predictions.

---

### JSON Structure

```json
{
  "id": "",
  "from_player_id": "",
  "to_player_id": "",
  "asset_type": "cash",
  "asset_id": null,
  "amount": 0,
  "metadata": {},
  "statistics": {}
}
```

---

### Field Definitions

#### id

Unique identifier of the transfer.

The identifier must remain stable throughout the complete evaluation.

---

#### from_player_id

Identifier of the player giving the asset.

This should reference a valid Player identifier.

---

#### to_player_id

Identifier of the player receiving the asset.

This should reference a valid Player identifier.

---

#### asset_type

Type of asset being transferred.

Common values include:

- cash
- property
- tradable_asset

Additional asset types may be supported by the Game Configuration.

---

#### asset_id

Identifier of the transferred asset.

For property transfers, this should reference a valid Property identifier.

For tradable asset transfers, this should reference a valid Tradable Asset identifier.

For cash transfers, use `null`.

---

#### amount

Amount transferred.

For cash transfers, this represents the cash amount.

For property or tradable asset transfers, this may be `1` unless the asset represents a quantity.

---

#### metadata

Optional implementation-specific information.

This field allows Monopoly platforms to include additional factual information without modifying the schema.

Unknown metadata fields should be ignored unless documented by the Game Configuration.

---

#### statistics

Optional precomputed factual summaries.

Examples include:

- transfer_value;
- mortgage_transfer_fee;
- mandatory_payment_created;
- post_transfer_cash_effect.

Statistics summarize factual information only.

Strategic evaluation belongs to the evaluator.

---

### Design Principles

Each Transfer should describe exactly one asset movement.

No transfer should combine unrelated assets.

For example, a trade where Player A gives `$400` and two properties should contain three Transfer objects:

- one cash transfer;
- one transfer for the first property;
- one transfer for the second property.

This makes the trade easier to inspect, audit, and evaluate.

Every Transfer should be explicit.

No asset movement should be implied.

## Game State

The Game State object describes the global state of the Monopoly game.

Unlike Player and Property objects, Game State contains information that belongs to the game itself rather than to any individual entity.

Game State contains factual information only.

It should never contain strategic opinions, evaluations, recommendations, or predictions.

---

### JSON Structure

```json
{
  "current_turn": 0,
  "current_player_id": "",
  "active_player_count": 0,
  "eliminated_player_count": 0,
  "available_houses": 32,
  "available_hotels": 12,
  "game_phase": "",
  "statistics": {}
}
```

---

### Field Definitions

#### current_turn

Sequential turn number since the beginning of the game.

This field is informational and may be used for logging, replay, or historical analysis.

---

#### current_player_id

Identifier of the player whose turn it currently is.

This field is important because turn order may influence:

- immediate development opportunities;
- bankruptcy risk;
- negotiation opportunities;
- short-term competitive pressure.

---

#### active_player_count

Number of players currently active in the game.

Eliminated players should not be included.

---

#### eliminated_player_count

Number of players that have already been eliminated.

---

#### available_houses

Number of houses currently available in the bank.

This field is critical because house shortages may significantly affect competitive value.

---

#### available_hotels

Number of hotels currently available in the bank.

Hotel availability may affect immediate development opportunities.

---

#### game_phase

Optional description of the current stage of the game.

Examples include:

- opening
- early_game
- mid_game
- late_game
- end_game

The evaluator should treat this value as contextual information only.

It should not replace conclusions derived from the Board State.

---

#### statistics

Optional precomputed factual summaries.

Examples include:

- total_properties_owned;
- total_monopolies;
- total_mortgaged_properties;
- total_houses_on_board;
- total_hotels_on_board;
- total_cash_in_play.

Statistics summarize factual information only.

Strategic evaluation belongs to the evaluator.

---

### Design Principles

Game State contains only global information.

Information belonging to an individual player should remain inside the corresponding Player object.

Information belonging to an individual property should remain inside the corresponding Property object.

This separation minimizes ambiguity and allows the evaluator to distinguish between global game conditions and entity-specific information.

Game State should remain independent from strategic analysis.

Its purpose is to describe the current state of the game, not to interpret it.

## Static Analysis Control

The Static Analysis Control object declares how Static Algorithm Evidence must be handled for the current evaluation.

The conceptual model is defined by the Input Specification (`02_input_specification.md`).

The runtime behavior produced by each mode is defined by the Judge Specification (`01_judge.md`).

This section is optional.

When it is absent, the evaluator behaves exactly as if `{ "mode": "auto", "fallback_allowed": false }` had been supplied.

---

### JSON Structure

```json
{
  "mode": "auto",
  "fallback_allowed": false,
  "required_algorithm": {
    "id": "monopoly_static_algorithm",
    "version": "1.0"
  },
  "required_dependencies": [
    {
      "id": "monopoly_risk_reference",
      "version": "1.0"
    }
  ]
}
```

---

### Field Definitions

#### mode

Required when the section is present.

Exactly one of:

- `auto`
- `require_provided_evidence`
- `allow_llm_fallback`
- `disable_static_analysis`

The semantics of each mode are defined by the Static Analysis Control chapter of the Input Specification.

Default when the section is absent: `auto`.

---

#### fallback_allowed

Optional boolean.

Declares whether the Judge is authorized to execute the Static Algorithm itself (LLM Static Fallback) when no usable supplied evidence exists.

Default: `false`.

In `auto` mode, fallback may execute only when this field is `true`.

In `allow_llm_fallback` mode, the mode itself grants the authorization, and this field is treated as `true`.

In `require_provided_evidence` and `disable_static_analysis` modes, this field is ignored and fallback never executes.

---

#### required_algorithm

Optional object identifying the Static Algorithm Specification that fallback execution must use.

```json
{
  "id": "",
  "version": ""
}
```

- `id` — stable specification identifier, matched against the `specification_id` declared by the Static Algorithm Specification.
- `version` — required specification version, matched against the declared `specification_version`.

A version is compatible when it equals the required version.

When omitted, the canonical Static Algorithm Specification distributed with this repository is used (`monopoly_static_algorithm`, version `1.0`).

This object is also used to validate the `algorithm_id` and `algorithm_version` of supplied Static Algorithm Evidence.

---

#### required_dependencies

Optional array of objects identifying every mandatory dependency of the Static Algorithm Specification.

Each entry uses the same structure as `required_algorithm`:

```json
{
  "id": "",
  "version": ""
}
```

Each entry is matched against the Specification Identity metadata declared by the dependency document.

When omitted, the mandatory dependencies declared by the Static Algorithm Specification itself are used (for the canonical algorithm: `monopoly_risk_reference`, version `1.0`).

## Static Algorithm Evidence

The Static Algorithm Evidence object contains deterministic calculations generated before the trade is evaluated.

Its purpose is to provide additional objective evidence to the evaluator.

The evaluator remains fully responsible for the final competitive classification.

Static Algorithm Evidence should never replace the evaluator's own reasoning.

The conceptual evidence contract is defined by the Static Algorithm Evidence Specification (`04_static_algorithm_specification.md`).

A concrete deterministic algorithm producing this evidence is defined in `../static_evaluator/static_algorithm_specification.md`.

---

### JSON Structure

```json
{
  "id": "",
  "algorithm_id": "",
  "algorithm_name": "",
  "algorithm_version": "",
  "purpose": "",
  "intermediate_calculations": [],
  "final_conclusions": {},
  "metadata": {},
  "statistics": {}
}
```

---

### Field Definitions

#### id

Unique identifier of this Static Algorithm Evidence object.

The identifier must remain stable throughout the complete evaluation.

---

#### algorithm_id

Stable machine-readable identifier of the Static Algorithm that generated this evidence.

It must equal the `specification_id` declared by the algorithm's specification (for the canonical algorithm: `monopoly_static_algorithm`).

This field is matched against `static_analysis_control.required_algorithm.id` during evidence validation.

---

#### algorithm_name

Human-readable name of the Static Algorithm.

---

#### algorithm_version

Version of the Static Algorithm that generated this evidence.

It must equal the `specification_version` implemented by the producing algorithm.

This field is matched against `static_analysis_control.required_algorithm.version` during evidence validation.

---

#### purpose

Short description of what this Static Algorithm evaluates.

Examples include:

- property valuation;
- liquidity calculation;
- mortgage calculation;
- development calculation;
- blocking calculation;
- monopoly calculation;
- railroad calculation;
- utility calculation;
- house control calculation;
- bankruptcy risk calculation;
- trade ratio calculation;
- competitive advantage calculation.

---

#### intermediate_calculations

List of deterministic intermediate calculations produced by the Static Algorithm.

These calculations expose how the algorithm reached its conclusions.

Every element is one canonical **Intermediate Calculation Item** with the following structure, defined conceptually by the Static Algorithm Evidence Specification (`04_static_algorithm_specification.md`). Both documents define the same field names, required fields, status values, side values, and value semantics.

```json
{
  "id": "",
  "calculation_type": "",
  "description": "",
  "status": "COMPLETE",
  "side": "before",
  "subject": {
    "player_ids": [],
    "property_ids": [],
    "group_ids": [],
    "trade_id": null,
    "transfer_ids": []
  },
  "input_references": [],
  "input_values": {},
  "sources": {},
  "formula": null,
  "procedure": null,
  "intermediate_values": {},
  "result": null,
  "unit": null,
  "limitations": [],
  "missing_inputs": [],
  "dependent_calculation_ids": [],
  "metadata": {}
}
```

Field semantics:

- `id` — unique, stable identifier of the item within the evidence object; referenced by `final_conclusions`.
- `calculation_type` — stable machine-readable identifier defined by the producing algorithm's Evidence Output Mapping registry (for example `base_asset_value`, `monopoly_value`, `immediate_risk`, `trade_ratio`). Synonymous identifiers for registered types are forbidden.
- `description` — concise human-readable explanation of what was calculated.
- `status` — exactly one of `COMPLETE`, `PARTIAL`, `UNAVAILABLE`, `ERROR`.
- `side` — exactly one of `before`, `after`, `delta`, `trade`.
- `subject` — stable identifiers of every entity materially involved in the calculation.
- `input_references` — machine-readable references to the exact input objects or fields used (for example `board_state_before.players[player_1].cash`).
- `input_values` — named factual values read from the referenced input.
- `sources` — provenance of configurable or default values (for example `GAME_CONFIGURATION_OVERRIDE`, `BOARD_STATE_RENT_TABLE`, `CLASSIC_DEFAULT`, `NEUTRAL_CUSTOM_GROUP_DEFAULT`, `RISK_REFERENCE_DEFAULT`, `SPECIFICATION_DEFAULT`, `IMPLEMENTATION_OVERRIDE`).
- `formula` / `procedure` — how the result was produced; at least one must be present for every completed material calculation.
- `intermediate_values` — every intermediate value necessary to independently reproduce the result.
- `result` — number, boolean, string, array, structured object, or `null` when unavailable.
- `unit` — optional unit or semantic type (for example `currency`, `ratio`, `houses`, `classification`).
- `limitations` — known limitations affecting interpretation of the result.
- `missing_inputs` — required inputs that were unavailable; mandatory when status is `PARTIAL` or `UNAVAILABLE`.
- `dependent_calculation_ids` — identifiers of calculations that consume this result or whose reliability is affected by it.
- `metadata` — optional implementation-specific information that does not alter the calculation meaning.

Required fields for every item: `id`, `calculation_type`, `description`, `status`, `side`, `subject`, `input_references`, `input_values`, `sources`, `intermediate_values`, `result`, `limitations`, `missing_inputs`.

For `COMPLETE` items, `result` must not be null and `missing_inputs` must be empty. For `UNAVAILABLE` items, `result` is normally null and the attempted calculation must still be published. For `ERROR` items, the error condition must be identified in `limitations` and no fabricated result may be published.

---

#### final_conclusions

Final deterministic conclusions produced by the Static Algorithm.

Examples include:

- total player valuation;
- competitive ratios;
- trade balance;
- estimated strategic advantage;
- estimated strategic disadvantage;
- calculated bonuses;
- calculated penalties.

Every material final conclusion must reference the `id` values of the supporting intermediate calculation items.

---

#### metadata

Optional implementation-specific information.

This object must declare every Implementation Override applied to a Specification Default Value of the producing algorithm, including for each override the parameter name, the specification default value, the overridden value, and an optional reason.

An implementation using only Specification Default Values publishes an empty override declaration.

This object must also declare the version of every specification dependency used by the producing algorithm — for the canonical algorithm, the Risk Reference (`monopoly_risk_reference` and its `specification_version`).

Unknown metadata fields should be ignored unless documented by the Game Configuration.

---

#### statistics

Optional factual summaries about the Static Algorithm execution.

Examples include:

- number of calculations performed;
- evaluated players;
- evaluated properties;
- evaluated trade items.

Statistics should describe the algorithm execution only.

They should not contain strategic recommendations.

## Player Profile

The Player Profile object summarizes historical decision-making behavior for a single player.

Player Profiles provide contextual evidence.

They should help the evaluator understand how a player has historically approached Monopoly decisions.

They must never override the factual Board State.

---

### JSON Structure

```json
{
  "player_id": "",
  "profile_source": "",
  "games_analyzed": 0,
  "confidence": 0.0,
  "historical_behavior": {},
  "statistical_summary": {},
  "behavioral_consistency": "",
  "metadata": {},
  "statistics": {}
}
```

---

### Field Definitions

#### player_id

Identifier of the player this profile describes.

This should reference a valid Player identifier.

---

#### profile_source

Name of the system, module, or process that generated the Player Profile.

---

#### games_analyzed

Number of historical games used to generate this profile.

A higher number may increase reliability, but quality of data also matters.

---

#### confidence

Confidence level of the Player Profile.

Expected range:

- `0.0` = no confidence
- `1.0` = maximum confidence

This confidence describes the reliability of the profile, not the player's skill.

---

#### historical_behavior

Summary of the player's observed long-term tendencies.

Examples include:

- liquidity preference;
- monopoly preference;
- railroad preference;
- utility preference;
- blocking preference;
- development preference;
- mortgage behavior;
- negotiation style;
- risk tolerance;
- preferred game phase;
- typical endgame behavior.

---

#### statistical_summary

Optional statistical summaries about the player.

Examples include:

- historical win rate;
- average finishing position;
- average trade frequency;
- average cash reserve;
- average mortgage usage;
- average development timing.

---

#### behavioral_consistency

Description of how consistently the player follows similar decision-making patterns.

Examples include:

- highly_consistent
- moderately_consistent
- adaptive
- unpredictable
- unknown

---

#### metadata

Optional implementation-specific information.

Unknown metadata fields should be ignored unless documented by the Game Configuration.

---

#### statistics

Optional factual summaries related to the Player Profile.

Statistics should describe the profile data only.

They should not contain trade recommendations.

## Decision Pattern Profile

The Decision Pattern Profile object describes one documented Monopoly decision-making pattern.

Its purpose is to help explain why a player may reasonably have accepted or proposed a trade.

Decision Pattern Profiles are explanatory evidence.

They are never used to determine the competitive classification of a trade.

The evaluator should analyze Decision Pattern Profiles only after completing the competitive evaluation.

---

### JSON Structure

```json
{
  "id": "",
  "name": "",
  "category": "",
  "description": "",
  "purpose": "",
  "pattern_characteristics": {},
  "metadata": {},
  "statistics": {}
}
```

---

### Field Definitions

#### id

Unique identifier of the Decision Pattern Profile.

The identifier should remain stable across all evaluations.

---

#### name

Human-readable name of the Decision Pattern.

Examples include:

- Liquidity First
- Blocking Strategy
- Printed Value Bias
- Kingmaking-like

---

#### category

Category describing the nature of the documented pattern.

Examples include:

- competitive_pattern
- behavioral_pattern
- evaluation_bias
- non_competitive_pattern

---

#### description

General description of the documented decision pattern.

The description should explain the overall idea of the pattern without evaluating whether it is strategically correct.

---

#### purpose

Describes the objective typically pursued by this decision pattern.

The purpose should explain what type of outcome the player is usually attempting to achieve.

---

#### pattern_characteristics

Collection of documented characteristics describing the pattern.

Examples may include:

- typical situations;
- common decisions;
- expected advantages;
- expected disadvantages;
- known weaknesses;
- typical examples.

The evaluator should compare the observed trade against these documented characteristics.

---

#### metadata

Optional implementation-specific information.

Unknown metadata fields should be ignored unless documented elsewhere.

---

#### statistics

Optional factual summaries describing the Decision Pattern Profile.

Examples include:

- profile version;
- number of documented examples;
- confidence of the documentation.

Statistics describe the profile itself.

They should never influence the competitive classification directly.

---

### Design Principles

A Decision Pattern Profile documents a recognizable Monopoly decision pattern.

It does not describe a particular player.

Multiple players may exhibit the same documented pattern.

Likewise, a single player may match different Decision Pattern Profiles in different situations.

Decision Pattern Profiles may be generated from the strategies documented in the Strategy Knowledge Base (`07_strategy_knowledge_base.md`), using the mapping defined in that document, or provided by any other documented source.

Decision Pattern Profiles exist only to explain possible reasoning after the competitive evaluation has been completed.

They should never modify the competitive classification.