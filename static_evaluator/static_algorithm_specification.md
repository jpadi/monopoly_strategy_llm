# Monopoly Multiplayer Trade Evaluation System
## Static Algorithm for Detecting Highly Suspicious Trades

**Author:** Jorge Padilla

Version: 1.0

---

# Specification Identity

This document exposes the following stable identity metadata:

```text
specification_type = STATIC_ALGORITHM_SPECIFICATION
specification_id = monopoly_static_algorithm
specification_version = 1.0
```

`specification_version` always equals the document version declared above.

Mandatory dependencies of this specification:

```text
specification_id = monopoly_risk_reference
specification_version = 1.0
```

(the Risk Reference, `risk_reference.md`).

This metadata is used for fallback discovery and version validation:

- `static_analysis_control.required_algorithm` in the input schema is matched against `specification_id` and `specification_version`;
- `static_analysis_control.required_dependencies` is matched against the identity metadata of each dependency;
- the `algorithm_id` and `algorithm_version` of every Static Algorithm Evidence object produced by this algorithm must equal `specification_id` and the implemented `specification_version`.

A version is compatible when it equals the required version.

---

# Execution Agents

This specification may be executed by:

- deterministic software implementing it (the preferred producer);
- the LLM Judge, under the LLM Static Fallback rules defined by the Judge Specification (`../llm_evaluator/01_judge.md`), when the evaluation input explicitly authorizes it.

Both agents must follow the same normative execution order, the same formulas and deterministic procedures, and the same Evidence Output Mapping, and must publish the same canonical Static Algorithm Evidence.

Fallback execution never relaxes any requirement of this specification.

---

# Overview

This document proposes a static, deterministic algorithm designed to identify highly suspicious property trades in Monopoly multiplayer games.

The objective of this algorithm is **not** to determine whether a trade is correct or incorrect, nor to automatically punish players.

Instead, its purpose is to estimate the strategic value gained by each player after a trade and determine whether the exchange is unusually unbalanced compared to what would normally be expected from rational competitive play.

When a trade appears significantly more beneficial to one player than the other, the system may generate an internal flag for later analysis.

This algorithm is intentionally conservative.

Monopoly contains many advanced strategic trades that may initially appear unfair but are completely legitimate. Examples include:

- Paying a very large amount of cash to obtain house control.
- Giving away cash in exchange for a critical blocking property.
- Sacrificing short-term value to obtain four railroads.
- Paying above market value to immediately develop a monopoly.
- Trading for strategic board control instead of nominal property value.

Because of this, the algorithm should **never** attempt to determine whether a player is intentionally kingmaking.

Its only responsibility is to identify trades that are statistically unusual after considering multiple strategic factors.

The final decision should always remain outside the algorithm.

---

# Design Philosophy

Traditional Monopoly trade evaluation methods usually compare only:

- Printed property values.
- Cash exchanged.

Unfortunately, this approach fails to capture how Monopoly is actually played at higher levels.

The true value of a trade depends on the current state of the board.

Examples include:

- Immediate monopoly completion.
- Immediate development potential.
- House supply.
- Railroad ownership.
- Blocking dangerous monopolies.
- Future negotiation opportunities.
- Board control.
- Available liquidity.
- Mortgage capacity.

A player may intentionally "overpay" in cash while actually improving their position significantly.

Likewise, another player may receive properties with a high printed value while becoming strategically weaker.

Therefore, this algorithm estimates **Strategic Value**, not simply **Nominal Value**.

---

# Goals

The algorithm has four primary goals:

1. Estimate the strategic value gained by each player after a trade.

2. Detect trades that are extremely unbalanced after considering strategic factors.

3. Generate an internal flag for later analysis.

4. Minimize false positives by recognizing legitimate advanced strategies.

The algorithm is intentionally static.

No machine learning model is required.

Every decision is based on deterministic calculations that can easily be reproduced and adjusted by developers.

---

# Important Principle

This algorithm **does not enforce penalties.**

Its output is limited to one of the following:

- NO_FLAG
- SOFT_FLAG
- STRONG_FLAG
- REVIEW_RECOMMENDED

The algorithm never:

- Sends warnings.
- Restricts players.
- Blocks accounts.
- Determines intent.
- Makes moderation decisions.

Its only responsibility is to classify trades according to their estimated strategic imbalance.

Any moderation, review process, or player reporting system should exist independently from this algorithm.

---

# Input And Output Contract

This algorithm consumes the structured input model defined in:

**../llm_evaluator/03_input_schema.md**

The algorithm primarily analyzes:

- `game_configuration`
- `board_state_before`
- `trade`
- `board_state_after`

Every calculation must reuse the entity identifiers defined by the input schema, including player identifiers, property identifiers, the trade identifier, and transfer identifiers.

The complete output of this algorithm must be published as a Static Algorithm Evidence object, as defined by the Static Algorithm Evidence Specification:

**../llm_evaluator/04_static_algorithm_specification.md**

The mapping between the calculations defined in this document and the evidence object is described in the Evidence Output Mapping chapter of this document.

This algorithm supports trades with exactly two participants.

When a trade has more than two participants, the algorithm must not produce a classification.

It must publish an evidence object whose `final_conclusions` record the limitation (unsupported participant count), following the Missing Data rule of the Static Algorithm Evidence Specification.

---

## Trade Legality And Authoritative States

Trade legality is the responsibility of the Monopoly platform and its Game Configuration.

The algorithm evaluates the authoritative `board_state_before` and `board_state_after` exactly as supplied.

It never normalizes a trade (for example, by simulating the sale of buildings before applying the transfer), and it never rejects a platform-permitted trade on legality grounds, including transfers of developed properties.

If any transferred property has `is_tradable = false`, the algorithm records a state-consistency error in its published evidence and produces no classification, using the same degraded-output mechanism defined above for unsupported participant counts.

---

## Generic Street Groups

All street-group calculations operate generically using the `group_id`, the properties belonging to that group, the number of properties in the group, and the supplied economic and development data.

No group-based rule may assume that the board contains only the eight classic color groups.

---

## Capability And Exposure Metrics

Capability metrics evaluate what a player could immediately and legally do from the supplied Board State.

Exposure metrics evaluate only what is currently true and collectible in the supplied Board State.

Capability metrics include the Development Capability Predicates, blocking development potential, and the construction simulations of Steps 3 and 5.

Exposure metrics include the Largest Threat and Immediate Risk (Step 9).

The algorithm never predicts or simulates future opponent behavior, including hypothetical unmortgaging, construction, sales, or negotiations by opponents.

---

# Strategic Value Model

The algorithm evaluates every completed trade independently.

Instead of comparing only the printed value of exchanged properties, it estimates the **Strategic Value** gained by each player immediately after the trade.

Each player's Strategic Value is calculated as the sum of several independent components.

```
Strategic Value =
    Base Asset Value
  + Monopoly Value
  + House Control Value
  + Railroad Value
  + Blocking Value
  + Strategic Opportunity Value
  - Immediate Risk Change
```

Immediate Development Potential (Step 3) is not an additive component.

It enters the Strategic Value exclusively through the Development Multiplier applied inside Monopoly Value (Step 4).

Each component attempts to model one aspect of competitive Monopoly.

---

## Component Calculation Rule

Every Strategic Value component is calculated as a difference:

- calculate the component for the player's position immediately before the trade;
- calculate the component for the player's position immediately after the trade;
- the component's contribution is the difference (after − before).

**Base Asset Value is the only exception.** It is computed directly from the assets and cash the player receives, exactly as defined in Step 1.

This rule applies without exception to Immediate Risk (Step 9) and to the Strategic Opportunity Score (Step 8). Every component must therefore be defined as a **position function** — a value computable from a single board state — never as a trade-level predicate.

Strategic Value measures the change caused by the trade, never the absolute quality of the post-trade position.

This keeps the two players' Strategic Values comparable as gains: each value measures what the player obtained, and the position-based components measure how the trade changed the player's position rather than the value the player already possessed.

Base Asset Value carries the nominal recoverable value of what was received (Step 1). Monopoly Value, development strength, House Control, rent exposure, and repair exposure carry the strategic consequences of the same assets. These remain separate components by design; this is not double-counting.

This rule takes precedence over the per-step wording.

When a step describes evaluating received properties or newly completed monopolies, that description covers the "after" side of the calculation only.

Value lost by giving properties away — including broken monopolies and surrendered blocking properties — is captured by the same difference and produces negative contributions.

---

## Value Sources

The system distinguishes three sources of values, which must remain distinguishable in every published evidence object.

### 1. Specification Default Values

Every numeric value documented by this specification — multipliers, bonuses, penalties, thresholds, balancing constants, and reference values — is a **Specification Default Value**.

These values are normative defaults.

Any implementation using only Specification Default Values must produce equivalent deterministic evidence for the same input.

Formulas, procedures, tier structures, table-application rules, predicate thresholds that define terms (such as the 3-house Dangerous threshold), flag names, classification labels, and enumerated vocabularies are **normative structure** and are never tunable.

### 2. Game Configuration Values

Game Configuration represents facts about the Monopoly implementation being evaluated: property prices, rent tables, house and hotel costs, custom groups, custom board rules, and custom group multipliers explicitly supplied by the platform.

Game Configuration values are not implementation overrides.

They describe the game being evaluated.

### 3. Implementation Overrides

Implementation Overrides modify Specification Default Values.

Every override must be explicitly declared inside the evidence object's `metadata`, including:

- parameter name;
- specification default value;
- overridden value;
- optional reason.

Silent tuning is forbidden.

### Source Labels

Every calculation consuming configurable values must identify the origin of those values using, at minimum:

- `SPECIFICATION_DEFAULT`
- `GAME_CONFIGURATION`
- `IMPLEMENTATION_OVERRIDE`

These labels are mutually exclusive for a single value source. More specific sub-labels defined elsewhere in this document (such as `CLASSIC_DEFAULT`, `NEUTRAL_CUSTOM_GROUP_DEFAULT`, `RISK_REFERENCE_DEFAULT` within the `SPECIFICATION_DEFAULT` family, and `GAME_CONFIGURATION_OVERRIDE`, `BOARD_STATE_RENT_TABLE` within the `GAME_CONFIGURATION` family) refine these three origins.

### Normative Principle

The system separates the algorithm, the game configuration, and the implementation tuning.

Two implementations evaluating the same Monopoly game and using only Specification Default Values must produce equivalent deterministic evidence.

Differences caused by Game Configuration represent different Monopoly games.

Differences caused by Implementation Overrides represent different evaluator configurations.

---

## Development Capability Predicates

Capability tests in this document use two canonical predicates. Both use the complete Step 3 procedure, including current cash, eligible mortgage capacity, unmortgage prerequisite costs, even-building rules, available houses and hotels, configured construction costs, and the applicable allocation rules.

**Buildable** — a complete street group is *Buildable* when its owner could immediately and legally build at least one house on every property in the group (at least `1-1` or `1-1-1`, depending on group size). A group is not Buildable when the player cannot reach that level.

**Dangerous** — a complete street group (a monopoly) is *Dangerous* when its owner could immediately and legally reach at least three houses on every property in the group (at least `3-3` or `3-3-3`, depending on group size).

Every use of the term "dangerous monopoly" in this document uses the *Dangerous* predicate.

Every phrase such as "can immediately develop", "can immediately build", or "immediately developable" resolves to exactly one of these two predicates, as assigned by the step or rule that uses it. No undefined development-capability phrase is permitted.

For every capability determination, the evidence must expose: the player identifier, the group identifier, the predicate evaluated, the immediately achievable houses per property, the available construction budget, the unmortgage prerequisite costs, the house and hotel supply constraints, and the boolean result.

---

## Dangerous Monopoly Availability Predicates

**Dangerous Monopoly Available** — a Dangerous Monopoly is *available* to an opponent when at least one street group satisfies both conditions:

1. every property in the group is either already owned by that opponent, or currently unowned and obtainable through ordinary non-trade gameplay;
2. if every currently unowned property in that group were hypothetically assigned to that opponent at zero acquisition cost, the resulting complete group would satisfy the *Dangerous* predicate using the opponent's current factual cash, eligible mortgage capacity, unmortgage prerequisite costs, current bank house and hotel supply, configured building rules, and the complete Step 3 capability procedure.

Properties owned by another player never satisfy the availability condition, even when they are currently tradable, because obtaining them requires a trade.

The zero-acquisition-cost convention exists only to measure the strategic capability exposed by the current board topology. It must not be interpreted as a prediction that the opponent will acquire the properties, a prediction of purchase price, additional cash or value received by the opponent, or an assumption used by unrelated scoring components.

**Fully Blocked Board** — for an evaluated player, the board is *Fully Blocked* when no opponent has any Dangerous Monopoly Available. This is an opponent-relative position predicate.

**Mostly Blocked Board** — a board is *Mostly Blocked* when no street group can currently be completed by any single player without a trade, regardless of whether that group would be Dangerous. This is a pure board-topology predicate, distinct from *Fully Blocked Board*, and is used by Rule 6 in Step 13.

---

The values do not need to be perfectly accurate.

Their purpose is simply to approximate how much stronger each player's position becomes after the trade.

The final comparison is performed only after all strategic factors have been evaluated.

---

# Step 1 — Base Asset Value

The first calculation estimates the nominal value received by each player.

This represents the value that would normally be considered by a casual player.

It includes:

- Cash received.
- Printed property values.
- Mortgage values.
- Buildings received with transferred properties.
- Get Out of Jail cards.

```
Base Asset Value =
      Cash Received
    + Printed Property Value
    + Railroad Printed Value
    + Utility Printed Value
    + Building Value Received
    + Get Out Of Jail Card Value
```

Default values:

```
Get Out Of Jail Card = 75
```

If a received property is mortgaged, its value should be reduced by the cost required to make it usable again.

```
Mortgage Penalty =
    Unmortgage Cost
```

The Unmortgage Cost is the property's `unmortgage_cost` field from the input schema.

When that field is unavailable, calculate:

```
Mortgage Penalty =
    Mortgage Value
  × (1 + mortgage_interest_rate)
```

`mortgage_interest_rate` is defined by `game_configuration`.

The standard Monopoly value is 10%.

Therefore,

```
Adjusted Property Value =
    Printed Value
  - Mortgage Penalty
```

If a received property carries buildings, they contribute their configured recoverable liquidation value — never their full construction cost:

```
House Building Value =
    Houses
  × House Cost
  × house_sell_back_ratio
```

```
Hotel Building Value =
    Configured recoverable value of the hotel,
    including any underlying building value
    only when the platform's liquidation rules
    define it that way
```

The applicable sell-back and liquidation rules are defined by `game_configuration` (`house_sell_back_ratio`, `hotel_sell_back_ratio`, `hotel_liquidation_basis`, and the per-property `hotel_liquidation_value` override).

Do not assume the hotel basis is `4 × house_cost + hotel_cost` unless the supplied Game Configuration defines hotel liquidation that way.

When no override is provided, use the documented classic Monopoly default: 50% of construction cost as defined by the platform's rules.

Building Value Received is nominal recoverable value only. The strategic consequences of the same buildings (development strength, house control, rent exposure, repair exposure) are carried by their own components, as stated in the Component Calculation Rule.

This calculation intentionally ignores strategy.

It simply estimates the nominal economic value exchanged during the trade.

---

# Step 2 — Monopoly Detection

The next step determines whether either player completes one or more monopolies after the trade.

For each color group:

```
If
Player owns every property
after applying the trade

Then

Completed Monopoly = TRUE
```

Each completed monopoly is evaluated independently.

Unlike nominal property value, monopolies are worth dramatically more because they unlock development.

Simply owning three orange properties is significantly more valuable than owning the same printed value spread across unrelated colors.

---

# Step 3 — Immediate Development Potential

Completing a monopoly does not always create the same threat.

The algorithm estimates how much the player can actually build immediately.

The following resources are considered:

- Current cash.
- Mortgage capacity.
- Houses remaining in the bank.

```
Available Construction Budget =
    Cash After Trade
  + Mortgage Capacity
```

Mortgage Capacity is the sum of `mortgage_value` of every unmortgaged, undeveloped property the player owns.

When calculating the Available Construction Budget, the properties of the color group being developed are excluded from Mortgage Capacity.

The same Mortgage Capacity definition applies wherever this document refers to mortgage capacity, including the Available Risk Resources calculation in Step 9 (without the color group exclusion).

A street group containing mortgaged properties cannot be developed until every property required by the platform's building rules has been legally unmortgaged (`game_configuration.building_allowed_with_mortgaged_group_member` defines the platform rule; the classic default is `false`).

The unmortgage costs of those properties are deducted from the group's allocated share of the Available Construction Budget before any houses or hotels are simulated.

This rule applies identically to the before-side and after-side simulations defined in Step 5.

When one player completes multiple monopolies in the same trade, the Available Construction Budget is allocated to the groups in descending order of Monopoly Value.

Each group's Development Multiplier is computed from its allocated share of the budget.

The budget is never counted twice.

Maximum buildable houses:

```
Maximum Houses =
Minimum(

Available Budget / House Cost,

Remaining Houses In Bank,

Maximum Houses Needed
)
```

Maximum Houses Needed is 4 houses per property in the completed group.

Hotel conversion is excluded from this calculation.

`Available Budget / House Cost` uses integer division.

When `game_configuration.even_building_required` is true, houses must be distributed evenly across the group.

This value determines the immediate offensive power created by the trade.

Default multipliers:

```
Cannot Build
Multiplier = 0.40

Can Build 1–2 Houses Each
Multiplier = 1.00

Can Build 3 Houses Each
Multiplier = 1.50

Can Build 4 Houses Each
Multiplier = 2.00
```

Every tier is measured per property.

Apply the highest tier that is fully achievable on every property of the group.

"Cannot Build" means not even one house can be built.

This prevents false positives.

Receiving a monopoly without enough money to build is much less dangerous than receiving one that can immediately become fully developed.

---

# Step 4 — Monopoly Strength

Every street group has a different strategic value.

Orange monopolies generally produce more income than Browns.

Dark Blue produces extremely high rent but requires heavy investment.

The algorithm therefore applies a **Group Strategic Multiplier**.

Default values (canonical classic multipliers, keyed by classic `group_id`):

| Group | Multiplier |
|--------|-----------:|
| brown | 0.80 |
| light_blue | 0.90 |
| pink | 1.10 |
| orange | 1.40 |
| red | 1.20 |
| yellow | 1.10 |
| green | 1.20 |
| dark_blue | 1.30 |

The multiplier for a group is resolved using the following priority:

1. Explicit multiplier supplied in `game_configuration.group_multipliers[group_id]`.
2. The canonical classic multiplier above, when the `group_id` matches a recognized classic color group.
3. A neutral fallback multiplier of `1.00` for an unknown street group.

The `1.00` fallback is a neutral deterministic default only. It must not be described as an accurate estimate of the custom group's positional strength.

For every multiplier used, the evidence must expose the multiplier value, the affected `group_id`, and the source, using at least these labels:

- `GAME_CONFIGURATION_OVERRIDE`
- `CLASSIC_DEFAULT`
- `NEUTRAL_CUSTOM_GROUP_DEFAULT`

Estimated Monopoly Value:

```
Monopoly Value =

Maximum Expected Rent

×

Group Strategic Multiplier

×

Development Multiplier
```

Maximum Expected Rent is the maximum rent of the most expensive property in the group, evaluated at the development level the player can immediately afford, as calculated in Step 3.

Rent values are resolved using the following priority:

1. Explicit Game Configuration overrides.
2. The property `rent_table` supplied by the Board State.
3. Classic Monopoly default values from **risk_reference.md**.
4. Calculation unavailable.

The risk reference defines the normative calculation methodology; its numeric tables are the canonical Classic Monopoly defaults. The evidence must expose which rent source was used for every calculation.

When a custom group lacks sufficient rent or economic data at every priority level, the affected calculation must be marked `UNAVAILABLE` rather than estimated.

Developers may tune the multiplier values through declared Implementation Overrides (see Value Sources).

Perfect accuracy is unnecessary.

Only relative strength matters.

---

# Step 5 — House Supply Control

House supply is one of the strongest strategic resources in Monopoly.

Many trade evaluation systems ignore this completely.

However, experienced players know that controlling the house supply can be more valuable than the printed value of the exchanged properties.

A player may intentionally pay significantly above market value to obtain a monopoly that allows immediate construction, not because of the rent itself, but because purchasing most of the available houses prevents every other player from developing their own monopolies.

For this reason, house control must be evaluated independently from monopoly value.

---

## Immediate House Control

House Control and House Denial are position-based functions calculated identically on both sides of the trade.

For each player, simulate the maximum immediate legal construction on `board_state_before` using the player's pre-trade cash, mortgage capacity, monopolies, house and hotel availability, building costs, even-building rules, unmortgage prerequisites (Step 3), and the applicable allocation rules. The simulation covers every monopoly the player owns in that state, using the budget calculation defined in Step 3.

Then repeat the same procedure independently on `board_state_after`.

The before-side and after-side simulations must use the same algorithm. Never compare actual houses on one side against simulated houses on the other.

For each side, calculate:

```
Total Houses Controlled =
Current Houses Owned
+
Houses Purchased Immediately
```

Hotels are not houses.

Current Houses Owned counts physical houses only.

Houses returned to the bank through hotel conversion count as remaining in the bank.

Then calculate:

```
Remaining Houses In Bank =
Total Houses - Total Houses Controlled
```

Total Houses is defined by `game_configuration.total_houses`.

The standard Monopoly value is 32.

This simulation is local to the House Control and House Denial calculations. Simulated construction must not mutate the authoritative Board State or affect unrelated calculations such as cash, Available Risk Resources, repair exposure, or Immediate Risk, unless another section explicitly requires it.

---

## House Control Bonus

Default bonus values:

| Houses Controlled | Bonus |
|------------------:|------:|
| 20 | +1000 |
| 24 | +1800 |
| 28 | +3000 |
| 32 | +5000 |

Apply the single row with the highest threshold that is met.

Controlling fewer than 20 houses produces no bonus.

Rows are never summed and values are never interpolated.

The bonus is computed separately for each side, and the component contribution follows the Component Calculation Rule:

```
House Control Contribution =
House Control Bonus After - House Control Bonus Before
```

These values are intentionally aggressive.

Once a player controls most of the available houses, the strategic value increases dramatically because opponents may no longer be able to develop newly acquired monopolies.

---

## House Denial Bonus

The fewer houses remain in the bank, the greater the strategic advantage.

Default values:

| Houses Remaining | Bonus |
|-----------------:|------:|
| ≤ 8 | +1000 |
| ≤ 4 | +2000 |
| 0 | +3000 |

Apply the single row with the highest bonus whose condition is met.

Rows are never summed.

The bonus is computed separately for each side, and the component contribution follows the Component Calculation Rule:

```
House Denial Contribution =
House Denial Bonus After - House Denial Bonus Before
```

This bonus represents the ability to deny future development to every opponent.

---

## Why This Matters

Consider the following trade:

Player A pays:

- $1500

Player B gives:

- One property completing a monopoly.

At first glance, Player A appears to have massively overpaid.

However, after the trade:

- Player A immediately builds 24 houses.
- Only a few houses remain in the bank.
- Every opponent is prevented from developing their own monopolies.

Although the nominal trade appears heavily unbalanced, the strategic value strongly favors Player A.

Without evaluating house control, this trade could be incorrectly flagged as suspicious.

Therefore, house supply must always be included in the strategic evaluation.

---

# Step 6 — Railroad Evaluation

Railroads represent a unique economic engine.

Unlike monopolies, they require no additional investment.

They generate continuous income while preserving liquidity for future negotiations and property development.

Because of this, railroad ownership should be evaluated separately from printed property values.

Default values:

| Railroads Owned | Strategic Value |
|----------------:|----------------:|
| 1 | 200 |
| 2 | 500 |
| 3 | 900 |
| 4 | 1800 |

These values can be adjusted through declared Implementation Overrides using gameplay statistics.

The important point is that the fourth railroad is considerably more valuable than the first.

---

## Board Context Adjustment

Railroads become more valuable on blocked boards.

If 0 or 1 developed monopolies exist on the board:

```
Railroad Value *= 1.30
```

Reason:

Players rely more heavily on railroad income while searching for future negotiations.

Conversely, when 2 or more developed monopolies already exist, railroads become relatively less important.

```
Railroad Value *= 0.80
```

A monopoly is considered developed when any of its properties has at least one house.

This adjustment helps the algorithm understand different stages of the game.

---

## Fourth Railroad Special Case

Obtaining the fourth railroad is often much stronger than its printed value suggests.

The player immediately increases every railroad rent to the maximum while maintaining full liquidity.

If the trade grants the fourth railroad without meaningful strategic compensation, the algorithm should generate an additional flag.

Example:

```
Player receives:

Fourth Railroad

Player gives:

Minor cash
or
Low strategic value

↓

Flag:

STRATEGIC_RAILROAD_GIVEAWAY
```

The exact trigger conditions for this flag are defined exclusively by Rule 6 in Step 13, including the mostly blocked board condition.

This does not automatically indicate kingmaking.

It simply identifies trades where an important economic engine has been transferred without an obvious competitive justification.

---

# Step 7 — Blocking Value

One of the most underestimated strategic resources in Monopoly is board control through blocking.

A property does not need to complete a monopoly in order to have significant strategic value.

Simply owning a single property from a color group may completely prevent another player from completing a dangerous monopoly.

For this reason, every received property should also be evaluated according to its blocking potential.

---

## Basic Blocking Value

A player is **blocked** by a property when they own at least one property of the color group and cannot complete the group without acquiring it.

A player is **immediately blocked** when they own every property of the group except the evaluated property.

These definitions apply everywhere this document refers to blocked players, including the Future Negotiation Bonus and the Strategic Opportunity Score.

If a received property immediately blocks another player:

```
Blocking Value = +500
```

This value represents the strategic advantage of delaying an opponent's development.

---

## Dangerous Monopoly Block

Not all blocked monopolies represent the same threat.

If the blocked group would be *Dangerous* in the opponent's hands, the blocking value becomes significantly larger.

The determination uses the *Dangerous* predicate (see Development Capability Predicates): evaluate the blocked opponent as hypothetically receiving the missing blocking property at zero acquisition cost, then determine whether the completed group would be Dangerous using that opponent's current factual resources and the Step 3 capability calculation.

The zero-acquisition-cost assumption exists only to measure the maximum offensive capability currently prevented by the blocking property. It must not be treated as a prediction of a future trade price or as free value received by the opponent in any other component.

```
If
Blocked group would be Dangerous
in the opponent's hands

Then

Blocking Value += 1000
```

This reflects the fact that preventing an immediate threat is usually much more valuable than preventing a future possibility.

---

## Multi-Player Blocking

Sometimes a single property blocks multiple players simultaneously.

Example:

In a three-property color group, Player B owns one property and Player C owns one property.

The remaining property is held by Player A.

Neither Player B nor Player C can complete the monopoly without negotiating with Player A.

In this case:

```
Blocking Value += 500

for each blocked player
beyond the first
```

Blocked players are identified using the definitions given in Basic Blocking Value.

Multi-Player Blocking applies whether or not any player is immediately blocked.

When no player is immediately blocked, the base Blocking Value is 0 and this increment is applied on top of it.

The property becomes strategically stronger because it controls multiple future negotiations.

---

## Future Negotiation Value

Some properties are valuable because they create future negotiation opportunities.

For example:

Player A owns:

- 1 Red

Player B owns:

- 2 Reds

Player C owns:

- 1 Red

Player A's property prevents everyone else from completing the monopoly.

Even if no monopoly is completed immediately, Player A now owns the key negotiation piece.

Default bonus:

```
Future Negotiation Bonus =

300
+
250 × Additional Blocked Players

capped at 800
```

Additional Blocked Players is the number of players, beyond the first, that require the property to complete the same color group.

This keeps the bonus deterministic while increasing it whenever multiple players require the same property.

The Future Negotiation Bonus is part of Blocking Value.

It stacks with the Basic and Multi-Player blocking values and is not subject to the Strategic Opportunity Score cap defined in Step 8.

---

# Step 8 — Strategic Opportunity Evaluation

The algorithm should also estimate how the trade changes the player's future strategic position.

Examples include:

- Negotiation leverage.
- Board control.
- Multiple monopoly potential.
- A fully blocked board.

These situations may not immediately generate income, but they significantly improve future winning chances.

The **Strategic Opportunity Score** is a position function, computed independently on `board_state_before` and on `board_state_after`:

```
Strategic Opportunity Score =

200 × Position Criteria Satisfied

capped at 800
```

The cap applies to each position's score, not to the difference.

One criterion is satisfied for each of the following deterministic position predicates:

- **Negotiation Leverage** — at least one opponent requires one of the player's properties to complete a color group;
- **Board Control** — the player holds blocking properties in two or more color groups;
- **Multiple Monopoly Potential** — the player is within one property of completing two or more color groups;
- **Fully Blocked Board** — the *Fully Blocked Board* predicate holds (no opponent has any Dangerous Monopoly Available; see Dangerous Monopoly Availability Predicates).

Financial survival security is intentionally **not** a Strategic Opportunity criterion.

It is scored gradedly by the Risk Coverage model of Step 9.

Scoring it here as well would count the same financial fact twice.

The component contribution follows the Component Calculation Rule:

```
Strategic Opportunity Value =

Strategic Opportunity Score After
-
Strategic Opportunity Score Before
```

A trade that merely preserves a satisfied criterion produces no change for that criterion. A trade that loses a criterion — for example, opening a Dangerous Monopoly Available to an opponent — produces a negative contribution. A trade that newly satisfies a criterion produces a positive contribution.

For every opponent and candidate group evaluated by the Fully Blocked Board criterion, the evidence must expose: the opponent player identifier; the group identifier; the properties already owned by the opponent; the unowned properties included in the hypothetical completion; the properties owned by other players that prevent availability; the Dangerous predicate inputs; the immediately achievable development level; the availability result; and the final Fully Blocked Board result.

---

# Step 9 — Immediate Risk (Risk Coverage)

Every trade also changes the player's exposure.

Sometimes a player receives valuable assets but becomes immediately vulnerable because they cannot financially absorb the risk already present on the board.

This step calculates a deterministic **Risk Coverage** result: it compares the player's immediately accessible financial resources against the worst currently collectible exposure, and scores the position according to how much money would remain or be missing after paying.

Immediate Risk is an exposure metric (see Capability And Exposure Metrics). Every value in this step is a position function, computed independently on `board_state_before` and on `board_state_after`.

Each side is evaluated on its own state, before any simulated construction.

The construction simulated in Steps 3 and 5 affects only the development and house-control components; it does not reduce the cash or increase the repair exposure used in this step.

## Largest Threat

The Largest Threat of a position is the highest single-landing Total Exposure **currently collectible** from that board state:

```
Largest Threat =

Landing Exposure
+
Repair Exposure
```

This is the Total Exposure rule of the risk reference (`Total Exposure = Repair Cost + Landing Cost`), applied to the worst collectible landing.

The calculation methodology is defined by **risk_reference.md**; its numeric tables are the canonical Classic Monopoly defaults.

### Landing Exposure

Landing Exposure is the highest single-landing rent currently collectible from the evaluated player by any opponent.

It is calculated deterministically:

- a mortgaged property contributes no rent while it remains mortgaged — this is a fact of the state, not a penalty;
- the algorithm must not grant opponents hypothetical unmortgaging, construction, sales, negotiations, or any other actions; risk conservatism means choosing the worst currently collectible outcome, not inventing future actions;
- every contributing opponent monopoly is evaluated at its current development level, normalized using the Development Classification rules of the risk reference, and every landing is assumed to occur on the most expensive collectible property of the group (the Landing Cost rule);
- railroad and utility ownership-count rent tiers may include mortgaged group members when the configured rules define them that way (classic default: they do); the landed-on railroad or utility must itself be unmortgaged to collect rent; platform-specific deviations must come from Game Configuration;
- group rent bonuses require only the landed-on property to be unmortgaged, unless `game_configuration.group_rent_requires_all_members_unmortgaged` is `true`;
- rent values are resolved using the source priority defined in Step 4 (Game Configuration overrides → Board State `rent_table` → classic defaults from the risk reference → calculation unavailable), and the evidence must expose which rent source was used.

The evidence must identify the property or space producing the Landing Exposure, and any maximum-rent property excluded from collectible exposure because it is mortgaged.

As additional exposure evidence only, the cumulative two- through six-landing exposures of the threat-producing row (per the Number of Landings rule of the risk reference) must be exposed inside the landing-exposure evidence item.

These multi-landing values are never summed into the score; only the single-landing Largest Threat drives the Risk Coverage scoring.

### Repair Exposure

Repair Exposure uses the **Both Cards** column of the risk reference repair tables, applied to the evaluated player's own houses and hotels in that state.

The evidence must identify the houses counted, the hotels counted, the repair table used, the repair-card scenario used (`Both Cards`), and the resulting repair cost.

## Risk Reference Usage

This step consumes the risk reference as follows:

| Risk Reference content | Nature | Use in this step |
|---|---|---|
| Development Classification rules | Normative methodology | Normalize opponent monopoly development levels |
| Landing Cost rule (most expensive property) | Normative methodology | Select the collectible landing rent |
| Total Exposure rule | Normative methodology | `Largest Threat = Landing Exposure + Repair Exposure` |
| Color, Railroad, and Utility risk matrices | Classic defaults | Landing rent values at priority level 3 of the Step 4 source priority |
| Repair Exposure tables (Both Cards) | Classic defaults for the classic card costs | Repair Exposure of the player's own buildings |
| Number of Landings columns (2–6) | Classic defaults | Additional exposure evidence only; never scored |
| Monopoly Development Cost, House Consumption Reference | Informational precomputations | Not consumed by this algorithm; Step 3 uses configured building costs directly |

Every value taken from the risk reference numeric tables is recorded with the `RISK_REFERENCE_DEFAULT` source label, and the evidence object's `metadata` must declare the risk reference version used (see Evidence Output Mapping).

## Available Risk Resources

Available Risk Resources represent the maximum immediately accessible financial resources that may legally be used to pay the evaluated exposure:

```
Available Risk Resources =

Cash
+ Available Mortgage Capacity
+ Recoverable Building Liquidation Value
- Mandatory Immediate Costs
```

- **Cash** — the position's immediately available cash.
- **Available Mortgage Capacity** — the Step 3 Mortgage Capacity definition, without the color-group exclusion: the sum of `mortgage_value` of every unmortgaged, undeveloped property the player owns. Already mortgaged properties contribute nothing. Hypothetical mortgage capacity of developed properties after selling their buildings is intentionally not counted; this keeps the term deterministic and conservative.
- **Recoverable Building Liquidation Value** — the amount recoverable by legally selling every house and hotel the player owns, using the same configured liquidation rules as Step 1 (`house_sell_back_ratio`, `hotel_sell_back_ratio`, `hotel_liquidation_basis`, per-property `hotel_liquidation_value`). Recoverable liquidation value is used, never construction cost. Even-selling rules do not change the total when every building is liquidated.
- **Mandatory Immediate Costs** — configured obligations attached to the evaluated position that are documented in the input and not already reflected in the position's cash (for example, mortgage interest due on transferred mortgaged properties when `must_pay_interest_on_mortgaged_property_transfer` is `true` and the authoritative Board State has not already deducted it). Speculative future costs are never subtracted. When the authoritative Board States already reflect every mandatory payment, this term is `0`.

Available Risk Resources is the resources measure of the Risk Coverage evaluation. Its inclusion of recoverable building value is consistent with the Liquidity concept of the Input Specification (`../llm_evaluator/02_input_specification.md`), which recognizes cash, mortgage capacity, and building sell-back values.

## Risk Margin And Coverage Ratio

```
Risk Margin =

Available Risk Resources
-
Largest Threat
```

```
Surplus Amount = max(Risk Margin, 0)

Deficit Amount = max(-Risk Margin, 0)
```

Interpretation:

- `Risk Margin > 0` — the player can pay and retains a surplus;
- `Risk Margin = 0` — the player can pay exactly;
- `Risk Margin < 0` — the player cannot fully pay and has a deficit.

```
Coverage Ratio =

Available Risk Resources
/
Largest Threat
```

Special cases:

- when `Largest Threat > 0`, the normal ratio is calculated;
- when `Largest Threat = 0` and Available Risk Resources are nonnegative, the Coverage Ratio is published as `null` with the documented limitation `NO_EXPOSURE`, and the ratio-based scoring rules treat the position as satisfying the highest ratio tier — no arbitrary large number is ever substituted;
- when required data is missing, the calculation is marked `PARTIAL` or `UNAVAILABLE`.

Precision rule: every ratio comparison against a threshold is evaluated exactly using integer cross-multiplication (for example, `Coverage Ratio ≥ 1.25` is evaluated as `4 × Available Risk Resources ≥ 5 × Largest Threat`). The Coverage Ratio published in evidence is rounded to two decimal places for reporting only; rounding never affects tier selection.

## Risk Penalty (Risk Coverage Score)

The Risk Penalty of a position is a **signed** value.

A positive Risk Penalty worsens the position (deficit).

A negative Risk Penalty represents a coverage bonus (surplus).

The score never depends only on a boolean ability to pay; it is monotonic in the player's resources and bounded to the range `[-450, +1200]`.

### Deficit Side

When `Risk Margin < 0`:

```
Risk Penalty =

Ratio Severity
+
Deficit Severity
```

| Condition | Ratio Severity |
|-----------|---------------:|
| Coverage Ratio < 0.5 | 600 |
| 0.5 ≤ Coverage Ratio < 1.0 | 300 |

| Condition | Deficit Severity |
|-----------|-----------------:|
| Deficit Amount ≥ 1000 | 600 |
| 500 ≤ Deficit Amount < 1000 | 400 |
| 200 ≤ Deficit Amount < 500 | 300 |
| 0 < Deficit Amount < 200 | 100 |

The resulting penalty ranges from `+400` (marginal deficit) to `+1200` (critical deficit), preserving the historical maximum penalty magnitude.

A player missing `$1` therefore never receives the same penalty as a player missing `$1,000`.

### Coverage Side

When `Risk Margin ≥ 0`:

```
Risk Penalty =

- (Ratio Cushion + Surplus Cushion)
```

| Condition | Ratio Cushion |
|-----------|--------------:|
| Coverage Ratio ≥ 2.0, or `NO_EXPOSURE` | 200 |
| 1.25 ≤ Coverage Ratio < 2.0 | 100 |
| 1.0 ≤ Coverage Ratio < 1.25 | 0 |

| Condition | Surplus Cushion |
|-----------|----------------:|
| Surplus Amount ≥ 2000 | 250 |
| 1000 ≤ Surplus Amount < 2000 | 150 |
| 500 ≤ Surplus Amount < 1000 | 100 |
| Surplus Amount < 500 | 0 |

The resulting value ranges from `0` (exact or marginal coverage — the neutral zone) to `-450` (very strong coverage).

A player who can pay with `$10` remaining therefore never receives the same bonus as a player who can pay and retain `$2,000`.

The Ratio Cushion cap of `200` intentionally prevents large bonuses produced merely by very small exposures; an absolute cushion is additionally required through the Surplus Cushion.

### Scoring Structure

The additive two-part tier structure, the tier boundaries' existence, and the sign convention are normative structure.

The numeric tier boundaries and tier values are Specification Default Values, adjustable only through declared Implementation Overrides.

No rounding is required: all inputs are integer currency amounts and all tier values are integers.

## Risk Labels And Warnings

Each side's evaluation produces exactly one deterministic Risk Label, banded on the signed Risk Penalty:

| Condition | Risk Label |
|-----------|------------|
| Risk Penalty ≥ 900 | `SURVIVAL_RISK_CRITICAL` |
| 600 ≤ Risk Penalty < 900 | `SURVIVAL_RISK_HIGH` |
| 0 < Risk Penalty < 600 | `SURVIVAL_RISK_MODERATE` |
| Risk Penalty = 0 | `SURVIVAL_RISK_LOW` |
| Risk Penalty < 0 | `SURVIVAL_RISK_VERY_LOW` |

The following deterministic warnings are evaluated on the **after** side and published in `final_conclusions`:

- `PLAYER_CANNOT_SURVIVE_ONE_LANDING` — `Risk Margin After < 0`;
- `PLAYER_CANNOT_COVER_REPAIR_EXPOSURE` — `Available Risk Resources After < Repair Exposure After`.

These warnings report the absolute post-trade condition.

They must be published even when the Immediate Risk Change is `0` — for example, when a player was unable to pay before the trade and remains unable to pay after it.

They are not Step 13 flags and never modify the final classification.

## Immediate Risk Change

The component contribution follows the Component Calculation Rule:

```
Immediate Risk Change =

Risk Penalty After
-
Risk Penalty Before
```

Immediate Risk Change is subtracted in the Strategic Value sum. Worsening risk therefore lowers Strategic Value; improving risk raises it. A player whose Risk Coverage does not change contributes 0, regardless of how risky the position already was.

The per-side signed Risk Penalty is the position's Risk Coverage Score, and the Immediate Risk Change is the Risk Coverage Contribution consumed by the Strategic Value.

When the Largest Threat or the Available Risk Resources of a side cannot be calculated, the affected items are published with status `PARTIAL` or `UNAVAILABLE`, the component contributes `0` to the Strategic Value, and the limitation must be recorded in the evidence and in `final_conclusions`.

Example:

```
Before the trade:

Cash = $1700
Available Mortgage Capacity = $300
Recoverable Building Liquidation Value = $0
Mandatory Immediate Costs = $0
Available Risk Resources = $2000

Largest Threat = $950
Risk Margin = +$1050
Coverage Ratio = 2.11

Ratio Cushion = 200 (ratio ≥ 2.0)
Surplus Cushion = 150 (1000 ≤ surplus < 2000)
Risk Penalty Before = -350
Risk Label Before = SURVIVAL_RISK_VERY_LOW

After the trade:

Available Risk Resources = $150

Largest Threat = $950
Risk Margin = -$800
Coverage Ratio = 0.16

Ratio Severity = 600 (ratio < 0.5)
Deficit Severity = 400 (500 ≤ deficit < 1000)
Risk Penalty After = +1000
Risk Label After = SURVIVAL_RISK_CRITICAL
Warning: PLAYER_CANNOT_SURVIVE_ONE_LANDING

↓

Immediate Risk Change = 1000 - (-350) = 1350

Strategic Value contribution = -1350
```

This prevents the algorithm from assuming that a player who spends almost all of their money automatically made a bad trade.

Sometimes becoming temporarily poor is a perfectly valid strategic decision.

However, if two trades provide similar strategic gains, the safer position should receive the higher evaluation.

---

# Step 10 — Trade Initiator Evaluation

This is one of the most important parts of the algorithm.

Many apparently unbalanced trades are actually initiated by the player who appears to be "overpaying."

For example:

A player intentionally offers:

- Large amount of cash

in exchange for

- One property

because obtaining that property allows:

- Immediate monopoly completion.
- Immediate construction.
- House supply control.
- Blocking multiple opponents.

From a nominal perspective, the player appears to lose.

From a strategic perspective, the player may gain a decisive advantage.

Therefore, the algorithm should reduce suspicion whenever the player apparently overpaying voluntarily proposed the trade.

```
If

Apparent Overpayer
==
Trade Initiator

↓

Downgrade Imbalance Flags
```

The Trade Initiator is identified by the `initiating_player_id` field of the Trade object defined in the input schema.

The adjustment is deterministic:

- `HIGHLY_SUSPICIOUS_IMBALANCE` is downgraded to `SUSPICIOUS_IMBALANCE`;
- `SUSPICIOUS_IMBALANCE` is removed.

Flags other than the two imbalance flags are never modified by this adjustment.

This does not automatically validate the trade.

It simply acknowledges that experienced players often choose to sacrifice nominal value in exchange for strategic value.

---

## Important Distinction

The algorithm should distinguish between:

**Strategic Overpayment**

and

**Uncompensated Giveaway**

Strategic overpayment occurs when the player giving more nominal value receives one or more of the following:

- Immediate monopoly.
- Immediate development.
- House control.
- Strong board block.
- Future negotiation leverage.
- Economic engine (railroads).

Uncompensated giveaway occurs when the player gives significant strategic value while receiving no meaningful competitive advantage.

This distinction is one of the key elements that helps reduce false positives.

---

# Step 11 — Strategic Value Calculation

After evaluating every independent component, the algorithm calculates the final Strategic Value gained by each player.

```
Strategic Value =

Base Asset Value

+

Monopoly Value
(including the Development Multiplier)

+

House Control Bonus

+

House Denial Bonus

+

Railroad Value

+

Blocking Value

+

Strategic Opportunity Value

-

Immediate Risk Change
```

Strategic Value is floored at 0.

A negative result is always treated as 0.

Each component is intentionally independent.

Developers can adjust individual weights through declared Implementation Overrides without modifying the overall structure of the algorithm.

The objective is not to perfectly predict the outcome of the game.

Instead, the algorithm estimates how much stronger each player's position becomes immediately after the trade.

---

## Example

Player A receives:

- Orange Monopoly
- Enough cash to immediately build 3 houses each

Player B receives:

- $1200

Nominally, the trade appears close to balanced.

Strategically:

```
Player A

Base Assets .............................. 800
Monopoly (× development multiplier) ...... 4300
House Control ............................ 1500
Blocking ................................. 500

Strategic Value = 7100
```

```
Player B

Cash ..................... 1200
Properties ............... 400

Strategic Value = 1600
```

Although the printed values appear similar, the strategic imbalance is substantial.

---

# Step 12 — Trade Comparison

After both Strategic Values are calculated, compare them.

```
Highest Value =
max(Value A, Value B)

Lowest Value =
min(Value A, Value B)
```

Then calculate:

```
Trade Ratio =

Highest Value

/

Lowest Value
```

The Lowest Value used in the division is floored at 1.

This prevents division by zero and keeps the ratio finite when one player receives no measurable strategic value.

The ratio estimates how asymmetric the trade is.

---

## Default Thresholds

| Ratio | Classification |
|-------:|----------------|
| ratio < 2.0 | Normal Trade |
| 2.0 ≤ ratio < 3.0 | Slightly Unbalanced |
| 3.0 ≤ ratio < 5.0 | Suspicious |
| ratio ≥ 5.0 | Highly Suspicious |

These values are intentionally conservative.

Only very large strategic differences should generate strong flags.

---

# Step 13 — Automatic Flag Rules

Besides the strategic ratio, several individual situations should generate additional flags.

These flags increase confidence that the trade deserves review.

---

## Flag Semantics

Flags are a set of distinct flag types per trade.

Each rule is evaluated for every trade participant.

A flag type is recorded at most once, regardless of how many participants or rules produce it.

No flag is raised merely because a developed property was transferred (see Trade Legality And Authoritative States).

---

## Rule Predicate Definitions

The following definitions apply to every rule in this step.

- **No equivalent strategic benefit**, **no comparable strategic benefit**, and **weak compensation** — the other player's Strategic Value gain is less than 25% of the flagged player's Strategic Value gain.
- **Very small compensation** and **Strategic Value given away** — "Strategic Value given away" means the Strategic Value gained by the other participant. Rule 3 therefore fires when one participant's Strategic Value gain is less than 10% of the other participant's Strategic Value gain.
- **Mostly blocked board** — the *Mostly Blocked Board* predicate defined in Dangerous Monopoly Availability Predicates: no street group can currently be completed by any single player without a trade, regardless of whether that group would be Dangerous. This is a pure board-topology predicate; it must not be confused with the opponent-relative, danger-filtered *Fully Blocked Board* predicate used by Step 8.

The 25% and 10% thresholds are Specification Default Values.

Implementations that change them must declare the overrides as defined in Value Sources.

---

## Rule 1 — Buildable Monopoly Giveaway

This rule uses the *Buildable* predicate (see Development Capability Predicates). It must not require the stronger *Dangerous* threshold.

```
IF

Player receives a completed monopoly

AND

The monopoly is Buildable

AND

The other player receives
no equivalent strategic benefit

↓

Flag:

BUILDABLE_MONOPOLY_GIVEN_AWAY
```

---

## Rule 2 — Dangerous Monopoly Enabled

This rule uses the *Dangerous* predicate (see Development Capability Predicates).

```
IF

Trade creates a monopoly

AND

The monopoly is Dangerous
(at least 3 houses per property
immediately and legally reachable)

↓

Flag:

DANGEROUS_MONOPOLY_ENABLED
```

---

## Rule 3 — Symbolic Compensation

```
IF

High strategic value

↓

is exchanged for

↓

Very small compensation

↓

Flag:

SYMBOLIC_VALUE_TRADE
```

Example:

- Monopoly
- Fourth Railroad
- Critical Blocking Property

given away for:

- $1
- Small cash
- Low strategic assets

---

## Rule 4 — House Supply Transfer

```
IF

Trade allows one player
to control

24+

houses

↓

AND

The other player receives
no comparable strategic benefit

↓

Flag:

HOUSE_CONTROL_ENABLED
```

---

## Rule 5 — House Supply Denial

```
IF

Immediately after the trade
and the maximum immediate construction

4 or fewer houses
remain in the bank

↓

Flag:

HOUSE_SUPPLY_DENIAL
```

This flag identifies trades that leave the house bank nearly empty, denying future development to every other player.

---

## Rule 6 — Strategic Railroad Transfer

```
IF

Trade grants

Fourth Railroad

↓

AND

The board is mostly blocked

↓

AND

The player giving it away
receives weak compensation

↓

Flag:

STRATEGIC_RAILROAD_GIVEAWAY
```

---

## Rule 7 — Moderate Strategic Imbalance

```
IF

3.0 ≤ Trade Ratio < 5.0

↓

Flag:

SUSPICIOUS_IMBALANCE
```

`SUSPICIOUS_IMBALANCE` is a moderate flag.

It is not part of the strong flag set used by the final classification.

On its own, it produces at most a `SOFT_FLAG` classification.

---

## Rule 8 — Large Strategic Imbalance

```
IF

Trade Ratio ≥ 5.0

↓

Flag:

HIGHLY_SUSPICIOUS_IMBALANCE
```

---

# Step 14 — Final Classification

Every generated flag contributes to the final trade classification.

The classification is exactly one of the following four values. This enumeration is normative structure — the fixed output vocabulary of this algorithm, published inside the evidence `final_conclusions` as defined by the Static Algorithm Evidence Specification (`../llm_evaluator/04_static_algorithm_specification.md`) — and is never tunable. It is intentionally distinct from the Judge's Competitive Classification defined by the Output Specification:

```
NO_FLAG
```

Trade appears strategically reasonable.

---

```
SOFT_FLAG
```

Trade contains moderate imbalance.

Useful for statistical analysis only.

---

```
STRONG_FLAG
```

Trade is highly unusual and deserves additional attention.

---

```
REVIEW_RECOMMENDED
```

Trade contains multiple independent suspicious indicators.

Recommended only as an internal classification for future review.

This classification does **not** imply wrongdoing.

It simply indicates that the trade differs significantly from normal competitive play.

---

# Design Philosophy Behind the Classification

The algorithm should always favor false negatives over false positives.

In other words:

It is preferable to miss some cases of possible kingmaking than to incorrectly flag legitimate advanced strategic trades.

Experienced Monopoly players frequently perform trades that appear irrational when evaluated only by printed property values.

Examples include:

- Paying excessive cash to gain house control.
- Paying far above market value to complete a monopoly.
- Sacrificing liquidity to obtain four railroads.
- Maintaining board-wide blocking positions.
- Giving away nominal value to improve long-term strategic position.

These trades should **not** be considered suspicious merely because they appear financially unequal.

Only when multiple independent indicators point toward an extremely one-sided strategic outcome should the trade receive a stronger classification.

The objective is to identify unusual trades, not to restrict strategic creativity.

---

# Complete Algorithm Pseudocode

The following pseudocode is normative for calculation order, flag handling, and the numeric floors.

The exact implementation language is irrelevant.

The important aspect is that every strategic component is evaluated independently.

---

# Main Entry Point

```python
def evaluate_trade(trade, game_state):

    # Player identifiers come from trade.participants,
    # as defined by the input schema.
    #
    # This reference algorithm evaluates two-participant trades.
    # Trades with more participants require an extended
    # version of this algorithm.
    player_a = trade.participants[0]
    player_b = trade.participants[1]

    value_a = evaluate_player_gain(
        player_a,
        trade,
        game_state
    )

    value_b = evaluate_player_gain(
        player_b,
        trade,
        game_state
    )

    ratio = calculate_trade_ratio(
        value_a,
        value_b
    )

    flags = []

    evaluate_ratio(
        ratio,
        flags
    )

    evaluate_monopoly_rules(
        trade,
        game_state,
        flags
    )

    evaluate_house_rules(
        trade,
        game_state,
        flags
    )

    evaluate_railroad_rules(
        trade,
        game_state,
        flags
    )

    evaluate_symbolic_rules(
        trade,
        game_state,
        flags
    )

    evaluate_initiator(
        trade,
        value_a,
        value_b,
        flags
    )

    return classify_flags(flags)
```

---

# Evaluate One Player

```python
def evaluate_player_gain(
    player,
    trade,
    game_state
):

    base_assets = calculate_base_assets(
        player,
        trade
    )

    monopoly_value = calculate_monopoly_value(
        player,
        trade,
        game_state
    )

    # Immediate Development Potential is not an additive
    # component. It enters through the Development Multiplier
    # applied inside calculate_monopoly_value (Step 4).

    house_control = calculate_house_control(
        player,
        trade,
        game_state
    )

    house_denial = calculate_house_denial(
        player,
        trade,
        game_state
    )

    railroad_value = calculate_railroad_value(
        player,
        trade,
        game_state
    )

    blocking_value = calculate_blocking_value(
        player,
        trade,
        game_state
    )

    # Step 8: Strategic Opportunity Score is a position
    # function, evaluated on each board state (Q1 delta rule).
    opportunity_change = (
        calculate_strategic_opportunity_score(
            player,
            game_state.board_state_after
        )
        - calculate_strategic_opportunity_score(
            player,
            game_state.board_state_before
        )
    )

    # Step 9: Risk Penalty is a signed position function
    # (Risk Coverage Score: positive = deficit penalty,
    # negative = coverage bonus), evaluated on each
    # board state (Q1 delta rule).
    risk_change = (
        calculate_risk_penalty(
            player,
            game_state.board_state_after
        )
        - calculate_risk_penalty(
            player,
            game_state.board_state_before
        )
    )

    strategic_value = (

        base_assets

        + monopoly_value

        + house_control

        + house_denial

        + railroad_value

        + blocking_value

        + opportunity_change

        - risk_change

    )

    return max(
        strategic_value,
        0
    )
```

`calculate_house_control` and `calculate_house_denial` internally evaluate their position bonuses on both board states, using the identical maximum-construction simulation on each side, and return the after-minus-before difference (Step 5).

---

# Trade Ratio

```python
def calculate_trade_ratio(
    value_a,
    value_b
):

    highest = max(
        value_a,
        value_b
    )

    lowest = max(
        1,
        min(
            value_a,
            value_b
        )
    )

    return highest / lowest
```

---

# Ratio Evaluation

```python
def evaluate_ratio(
    ratio,
    flags
):

    if ratio >= 5:
        flags.append(
            "HIGHLY_SUSPICIOUS_IMBALANCE"
        )

    elif ratio >= 3:
        flags.append(
            "SUSPICIOUS_IMBALANCE"
        )
```

---

# Monopoly Rules

```python
def evaluate_monopoly_rules(
    trade,
    game_state,
    flags
):

    # Rule 1: uses the Buildable predicate.
    if gives_buildable_monopoly_without_compensation(
        trade,
        game_state
    ):
        flags.append(
            "BUILDABLE_MONOPOLY_GIVEN_AWAY"
        )

    # Rule 2: uses the Dangerous predicate.
    if enables_dangerous_monopoly(
        trade,
        game_state
    ):
        flags.append(
            "DANGEROUS_MONOPOLY_ENABLED"
        )
```

---

# House Supply Rules

```python
def evaluate_house_rules(
    trade,
    game_state,
    flags
):

    if enables_house_control_without_compensation(
        trade,
        game_state
    ):
        flags.append(
            "HOUSE_CONTROL_ENABLED"
        )

    if leaves_house_bank_nearly_empty(
        trade,
        game_state
    ):
        flags.append(
            "HOUSE_SUPPLY_DENIAL"
        )
```

---

# Railroad Rules

```python
def evaluate_railroad_rules(
    trade,
    game_state,
    flags
):

    # Implements Rule 6 (Step 13): fourth railroad granted,
    # mostly blocked board, and weak compensation.
    if matches_strategic_railroad_transfer_rule(
        trade,
        game_state
    ):
        flags.append(
            "STRATEGIC_RAILROAD_GIVEAWAY"
        )
```

---

# Symbolic Compensation Rules

```python
def evaluate_symbolic_rules(
    trade,
    game_state,
    flags
):

    if valuable_assets_given_for_symbolic_value(
        trade,
        game_state
    ):
        flags.append(
            "SYMBOLIC_VALUE_TRADE"
        )
```

---

# Trade Initiator Adjustment

```python
def evaluate_initiator(
    trade,
    value_a,
    value_b,
    flags
):

    apparent_overpayer = player_with_lower_value(
        value_a,
        value_b
    )

    if apparent_overpayer == trade.initiating_player_id:

        downgrade_imbalance_flags(
            flags
        )
```

```python
def downgrade_imbalance_flags(
    flags
):

    if "HIGHLY_SUSPICIOUS_IMBALANCE" in flags:

        flags.remove(
            "HIGHLY_SUSPICIOUS_IMBALANCE"
        )

        flags.append(
            "SUSPICIOUS_IMBALANCE"
        )

    elif "SUSPICIOUS_IMBALANCE" in flags:

        flags.remove(
            "SUSPICIOUS_IMBALANCE"
        )
```

The initiator adjustment exists because experienced players often intentionally overpay to obtain strategic advantages that are difficult to measure using nominal value alone.

Examples include:

- House control.
- Critical blocking properties.
- Immediate monopoly completion.
- Future negotiation leverage.
- Railroad engines.

The algorithm should therefore downgrade the imbalance flags whenever the player apparently sacrificing value voluntarily proposed the trade.

This adjustment reduces false positives while preserving detection accuracy.

---

# Final Classification

```python
def classify_flags(
    flags
):

    strong_flags = {

        "HIGHLY_SUSPICIOUS_IMBALANCE",

        "BUILDABLE_MONOPOLY_GIVEN_AWAY",

        "DANGEROUS_MONOPOLY_ENABLED",

        "HOUSE_CONTROL_ENABLED",

        "HOUSE_SUPPLY_DENIAL",

        "STRATEGIC_RAILROAD_GIVEAWAY",

        "SYMBOLIC_VALUE_TRADE"

    }

    strong_count = count_flags(
        flags,
        strong_flags
    )

    if strong_count >= 3:

        return "REVIEW_RECOMMENDED"

    if strong_count >= 2:

        return "STRONG_FLAG"

    if strong_count >= 1:

        return "SOFT_FLAG"

    if "SUSPICIOUS_IMBALANCE" in flags:

        return "SOFT_FLAG"

    return "NO_FLAG"
```

`count_flags` counts distinct flag types present in the set.

Duplicate detections of the same flag type never increase the count.

---

# Evidence Output Mapping

The complete result of this algorithm must be published as a Static Algorithm Evidence object, as defined in `../llm_evaluator/04_static_algorithm_specification.md` and serialized inside the `static_algorithm_evidence` section of the input schema.

Every intermediate calculation is published as one canonical Intermediate Calculation Item, as defined by the Static Algorithm Evidence Specification.

The mapping is deterministic.

This chapter is the canonical **calculation-type registry** for this algorithm.

Implementations must not invent synonymous identifiers for calculation types already defined here.

---

## Identification Fields

- `id` — a unique, stable identifier for this evidence object (for example `evidence_static_trade_imbalance_001`)
- `algorithm_id` — `monopoly_static_algorithm` (the `specification_id` declared in Specification Identity)
- `algorithm_name` — `Static Trade Imbalance Evaluator`
- `algorithm_version` — the version of this specification implemented by the algorithm (the implemented `specification_version`)
- `purpose` — `trade ratio calculation and competitive advantage calculation`

---

## Registry Common Rules

Unless a registry entry states otherwise:

- position-function components publish one item per side (`before`, `after`) and one `delta` item per player;
- every item references the players, properties, groups, and transfers involved through the `subject` fields, using input-schema identifiers;
- every item consuming configurable values records the value origins in `sources` (see Value Sources);
- `intermediate_values` must contain every value necessary to independently reproduce the result — intermediate arithmetic must never be hidden inside prose;
- a calculation that cannot be completed is published with status `PARTIAL`, `UNAVAILABLE`, or `ERROR`, never silently skipped;
- results are `PARTIAL` or `UNAVAILABLE` whenever a required input is missing (for example, rent data exhausting the Step 4 source priority), and `ERROR` when supplied input is inconsistent (for example, a transferred property with `is_tradable = false`).

---

## Calculation-Type Registry

### base_asset_value

- Purpose: nominal recoverable value received by a player (Step 1).
- Sides: `trade` (sole exception to the delta rule).
- Subject: player; received property, transfer, and card identifiers.
- Required input values: cash received, printed values, mortgage penalties, building liquidation values (per-property line items when buildings are received), card values.
- Required sources: sell-back and liquidation rule origins.
- Result: number (`currency`).

### mortgage_capacity

- Purpose: sum of `mortgage_value` of unmortgaged, undeveloped properties (Step 3 definition).
- Sides: `before`, `after`.
- Subject: player; contributing property identifiers.
- Result: number (`currency`).

### available_construction_budget

- Purpose: budget for the maximum immediate legal construction simulation (Step 3).
- Sides: `before`, `after`.
- Subject: player; developed group identifiers.
- Required input values: cash, eligible mortgage capacity, allocation order across groups, unmortgage prerequisite costs per group.
- Result: number (`currency`).
- Dependencies: `mortgage_capacity`.

### monopoly_value

- Purpose: Monopoly Value per completed group (Step 4), including the Development Multiplier.
- Sides: `before`, `after`, `delta`.
- Subject: player; group; group property identifiers.
- Required input values: Maximum Expected Rent, Group Strategic Multiplier, Development Multiplier.
- Required sources: rent source (per the Step 4 priority) and multiplier source (`GAME_CONFIGURATION_OVERRIDE`, `CLASSIC_DEFAULT`, or `NEUTRAL_CUSTOM_GROUP_DEFAULT`) with the affected `group_id`.
- Result: number (`currency`).
- Dependencies: `available_construction_budget`.
- `UNAVAILABLE` when rent data is exhausted at every source priority level.

### house_control_bonus / house_denial_bonus

- Purpose: house-supply position bonuses (Step 5).
- Sides: `before`, `after`, `delta`.
- Subject: player.
- Required intermediate values: Total Houses Controlled and Remaining Houses In Bank per side, simulated construction detail, unmortgage prerequisite costs.
- Result: number (`currency`).
- Dependencies: `available_construction_budget`.

### railroad_value

- Purpose: railroad engine value (Step 6), including the Board Context Adjustment.
- Sides: `before`, `after`, `delta`.
- Subject: player; railroad identifiers.
- Required input values: ownership count, context multiplier applied.
- Result: number (`currency`).

### blocking_value

- Purpose: blocking value per blocking property (Step 7), including the Dangerous Monopoly Block and the Future Negotiation Bonus line items.
- Sides: `before`, `after`, `delta`.
- Subject: player; blocking property; blocked opponent identifiers; blocked group.
- Required intermediate values: blocked player determinations, capability determination for the Dangerous Monopoly Block, additional blocked player count.
- Result: number (`currency`).
- Dependencies: `development_capability`.

### strategic_opportunity_score

- Purpose: position-based Strategic Opportunity Score (Step 8).
- Sides: `before`, `after`, `delta`.
- Subject: player.
- Required intermediate values: each of the four criteria with its boolean result per side; for the Fully Blocked Board criterion, the per-opponent availability determinations (see `dangerous_monopoly_availability`).
- Result: number.
- Dependencies: `dangerous_monopoly_availability`.

### available_risk_resources

- Purpose: maximum immediately accessible financial resources for the Risk Coverage evaluation (Step 9).
- Sides: `before`, `after`.
- Subject: player; mortgageable property identifiers; developed property identifiers.
- Required input values: cash; mortgage values counted; assets excluded (mortgaged or developed) and why; recoverable building liquidation values per property; mandatory immediate costs.
- Required sources: liquidation rule origins (`GAME_CONFIGURATION` family or classic defaults).
- Result: number (`currency`).

### landing_exposure

- Purpose: highest currently collectible single-landing rent (Step 9).
- Sides: `before`, `after`.
- Subject: player; threat-producing opponent, property or space, and group identifiers.
- Required input values: the collectible rent; the development level after Development Classification normalization; maximum-rent properties excluded because they are mortgaged.
- Required intermediate values: the cumulative two- through six-landing exposures of the threat-producing row (additional exposure evidence only, never scored).
- Required sources: rent source per the Step 4 priority; `RISK_REFERENCE_DEFAULT` when classic tables are used.
- Result: number (`currency`).
- `PARTIAL` or `UNAVAILABLE` when rent data exhausts the source priority.

### repair_exposure

- Purpose: Both-Cards repair exposure of the player's own buildings (Step 9).
- Sides: `before`, `after`.
- Subject: player.
- Required input values: houses counted; hotels counted; repair table used; repair-card scenario used (`Both Cards`); resulting repair cost.
- Required sources: `RISK_REFERENCE_DEFAULT` for the classic card costs.
- Result: number (`currency`).

### largest_threat

- Purpose: single-landing Total Exposure — `Landing Exposure + Repair Exposure` (Step 9).
- Sides: `before`, `after`.
- Subject: player; threat-producing opponent and space identifiers.
- Result: number (`currency`).
- Dependencies: `landing_exposure`, `repair_exposure`.

### risk_margin

- Purpose: `Available Risk Resources - Largest Threat` (Step 9).
- Sides: `before`, `after`.
- Subject: player.
- Required intermediate values: Surplus Amount (`max(Risk Margin, 0)`) and Deficit Amount (`max(-Risk Margin, 0)`).
- Result: number (`currency`, signed).
- Dependencies: `available_risk_resources`, `largest_threat`.

### coverage_ratio

- Purpose: `Available Risk Resources / Largest Threat` (Step 9).
- Sides: `before`, `after`.
- Subject: player.
- Required intermediate values: the special-case handling applied (`NO_EXPOSURE` when the Largest Threat is `0`); the exact cross-multiplication comparisons used for tier selection.
- Result: number (`ratio`, reported rounded to two decimals) or `null` with limitation `NO_EXPOSURE`.
- Dependencies: `available_risk_resources`, `largest_threat`.

### immediate_risk

- Purpose: signed Risk Penalty (the Risk Coverage Score) per side and the Immediate Risk Change (Step 9).
- Sides: `before`, `after`, `delta`.
- Subject: player; threat-producing opponent and space identifiers.
- Required intermediate values: the tier components applied (Ratio Severity and Deficit Severity, or Ratio Cushion and Surplus Cushion); the Risk Label per side; the warnings triggered on the after side.
- Required sources: rent source per exposure calculation; `RISK_REFERENCE_DEFAULT` when classic tables are used.
- Result: number (signed; the `delta` item is the Risk Coverage Contribution consumed by `strategic_value`).
- Dependencies: `available_risk_resources`, `landing_exposure`, `repair_exposure`, `largest_threat`, `risk_margin`, `coverage_ratio`.

### development_capability

- Purpose: *Buildable* / *Dangerous* predicate determinations (Development Capability Predicates).
- Sides: the side of the state evaluated.
- Subject: player; group.
- Required input values: predicate evaluated; immediately achievable houses per property; available construction budget; unmortgage prerequisite costs; house and hotel supply constraints.
- Result: boolean.

### dangerous_monopoly_availability

- Purpose: *Dangerous Monopoly Available* determinations per opponent and candidate group (Dangerous Monopoly Availability Predicates).
- Sides: the side of the state evaluated.
- Subject: opponent player; candidate group.
- Required input values: properties already owned by the opponent; unowned properties included in the hypothetical completion; properties owned by other players that prevent availability; Dangerous predicate inputs; immediately achievable development level.
- Result: boolean (availability), plus the final Fully Blocked Board boolean per evaluated player.
- Dependencies: `development_capability`.

### strategic_value

- Purpose: final Strategic Value per player (Step 11).
- Sides: `trade`.
- Subject: player.
- Required intermediate values: every component contribution and the floor application.
- Result: number.
- Dependencies: every component calculation type above.

### trade_ratio

- Purpose: Trade Ratio (Step 12).
- Sides: `trade`.
- Subject: both players.
- Required intermediate values: highest value, lowest value, floor application.
- Result: number (`ratio`).
- Dependencies: `strategic_value`.

### final_static_classification

- Purpose: flag evaluation and final classification (Steps 13–14).
- Sides: `trade`.
- Subject: both players.
- Required intermediate values: each rule evaluated, its predicate results, each generated flag, the initiator adjustment, the strong-flag count.
- Result: string (`classification`).
- Dependencies: `trade_ratio`, `strategic_value`, `development_capability`.

---

## final_conclusions

The final conclusions must contain:

- the Strategic Value of each player;
- the Trade Ratio;
- every generated flag;
- the Risk Label of each player on each side, and every triggered risk warning (`PLAYER_CANNOT_SURVIVE_ONE_LANDING`, `PLAYER_CANNOT_COVER_REPAIR_EXPOSURE`), as defined in Step 9;
- the final classification (`NO_FLAG`, `SOFT_FLAG`, `STRONG_FLAG`, or `REVIEW_RECOMMENDED`).

Every material final conclusion — labels, warnings, bonuses, penalties, deterministic scores, review requirements, and the final static classification — must reference the identifiers of the supporting intermediate calculation items.

No final conclusion may depend on unreferenced hidden arithmetic.

---

## metadata

The evidence object's `metadata` must declare every Implementation Override, as defined in Value Sources: parameter name, specification default value, overridden value, and optional reason.

An implementation using only Specification Default Values publishes an empty override declaration.

The `metadata` must also declare the version of every specification dependency used, including the Risk Reference (`monopoly_risk_reference` and its `specification_version`).

---

## Missing Data And Errors

Whenever a calculation cannot be completed because required input data is missing, the limitation must be recorded inside the evidence object rather than silently skipped, using the `PARTIAL` or `UNAVAILABLE` status of the canonical item structure.

State-consistency errors — including transfers of properties with `is_tradable = false` and unsupported participant counts — are recorded with status `ERROR` and in `final_conclusions`, and no classification is produced.

---

# Design Notes

The purpose of this algorithm is **not** to determine intent.

It estimates whether a trade is strategically reasonable according to a deterministic evaluation model.

Its output is limited to a classification describing how unusual the trade appears.

The algorithm never:

- punishes players,
- blocks accounts,
- sends warnings,
- rejects trades,
- or makes moderation decisions.

It simply provides a consistent and reproducible estimate of strategic imbalance that can be combined with other systems if desired.

---

# Future Improvements

The proposed algorithm is intentionally deterministic.

Every rule is static, explainable, reproducible, and easy to tune by developers.

However, several improvements could further increase its accuracy while maintaining transparency.

---

# Adaptive Weight Calibration

The Specification Default Values in this document are initial estimates.

For example:

- Group strategic multipliers
- Railroad values
- House control bonuses
- Blocking bonuses
- Immediate risk penalties

can all be adjusted over time using gameplay statistics.

All such tuning is performed through declared Implementation Overrides, as defined in Value Sources; silent tuning is forbidden.

Developers could compare flagged trades against historical games and gradually refine the weights without changing the overall structure of the algorithm.

---

# Board Position Evaluation

The current proposal evaluates only the resulting board state immediately after the trade.

Future versions could also estimate positional risk.

Examples include:

- Distance to dangerous monopolies.
- Expected probability of landing on developed properties.
- Remaining turns before likely contact.
- Jail status.
- Player turn order.

These factors would improve the estimation of immediate risk without fundamentally changing the algorithm.

---

# Historical Player Behaviour

Repeated suspicious trades from the same player may provide additional context.

Possible statistics include:

- Number of suspicious trades.
- Percentage of flagged trades.
- Frequency of giving away buildable monopolies.
- Frequency of symbolic value trades.
- Number of different opponents involved.

These statistics should never be used alone.

They simply provide additional information that may help identify repeated abnormal behaviour.

---

# Player Reports

Player reports can significantly improve confidence when combined with algorithmic analysis.

The algorithm itself should remain completely independent.

Its responsibility is only to evaluate the trade.

Player reports represent an entirely separate source of information.

When both sources independently identify the same trade as suspicious, confidence naturally increases.

This approach helps reduce false positives while avoiding excessive manual review.

---

# Optional AI Evaluation

One possible future improvement would be to use a Large Language Model (LLM) as a secondary evaluator.

The LLM would **not** replace the deterministic algorithm.

Instead, it would receive:

- Board position.
- Player assets.
- Trade details.
- Strategic evaluation produced by the algorithm.

The model could then answer questions such as:

- Does this trade appear strategically reasonable?
- Does the player giving away value obtain a realistic competitive advantage?
- Is there an obvious strategic justification not captured by the static evaluation?

The deterministic algorithm would continue to provide the primary evaluation.

The LLM would simply contribute an additional opinion.

This combination could reduce false positives in complex situations that are difficult to model using static rules alone.

---

## Why A Static Algorithm First?

Although AI models are becoming increasingly capable, Monopoly contains many fixed strategic concepts that do not require machine learning.

Examples include:

- Immediate monopoly completion.
- House supply control.
- Railroad ownership.
- Blocking value.
- Immediate development potential.
- Mortgage capacity.
- Liquidity.
- Strategic overpayment.

These concepts can all be evaluated using deterministic rules.

Implementing these rules first provides several advantages:

- Predictable behaviour.
- Easy debugging.
- Transparent scoring.
- Fast execution.
- Consistent results.
- Simple balancing.
- No LLM inference costs during gameplay, making the evaluation inexpensive and highly scalable.

Another practical advantage is the maturity of modern AI-assisted software development. Today's coding assistants (such as Cursor) can use the project's source code together with this design document to generate a large portion of the static algorithm in a matter of hours, subject to human review and validation. This significantly reduces implementation time while preserving the transparency, determinism, and maintainability of a rule-based system.

Only after these static concepts have been fully implemented would an AI-based evaluator become beneficial.

---

# Conclusion

This document proposes a deterministic trade evaluation system designed to estimate the strategic value gained by each player after a Monopoly trade.

Unlike traditional evaluations based only on printed property values and exchanged cash, this model considers the actual strategic state of the board.

The algorithm evaluates:

- Base asset value.
- Monopoly completion.
- Immediate development potential.
- House supply control.
- House denial.
- Railroad ownership.
- Blocking value.
- Future negotiation leverage.
- Strategic opportunity.
- Immediate risk.
- Trade initiator.
- Strategic imbalance.

The final output is intentionally limited to an internal classification:

- NO_FLAG
- SOFT_FLAG
- STRONG_FLAG
- REVIEW_RECOMMENDED

The algorithm does **not** determine player intent.

It does **not** punish players.

It does **not** reject trades.

Its only purpose is to consistently identify highly unusual trades whose strategic imbalance differs significantly from normal competitive play.

By combining deterministic strategic evaluation with future improvements such as gameplay statistics, optional player reports, and potentially AI-assisted analysis, developers can build a practical system capable of identifying suspicious trades while preserving legitimate strategic creativity.

---

# Final Design Principle

The purpose of this algorithm is not to eliminate creative trading.

The purpose is to protect competitive multiplayer games by identifying trades that are strategically inconsistent with rational competitive play, while minimizing false positives and preserving the depth of Monopoly's negotiation system.

Example 1

Player A gives:

Green Monopoly

Player B gives:

Fourth Railroad
$500

Result:

Player A
Strategic Value = 5400

Player B
Strategic Value = 5100

Trade Ratio = 1.05

Result:

NO_FLAG

Reason:

Although Player A appears to overpay,
Player A receives a complete railroad engine
plus immediate liquidity.

All numeric values proposed in this document
are Specification Default Values.

Developers may adjust them
through declared Implementation Overrides
using gameplay statistics.

Examples:

Group strategic multipliers

House bonuses

Railroad values

Blocking values

Immediate risk penalties

Trade ratio thresholds

...
Example:

A player pays $2500

for

one Orange property.

At first glance,
the trade appears absurd.

However,

the player immediately:

Completes Orange

Builds 12 houses

Controls almost every house

Blocks future monopolies.

Result:

NO_FLAG

Reason:

The player intentionally exchanged
cash for strategic board control.

Player gives:

$1800

receives:

Fourth Railroad

Reason:

Continuous economic engine.

NO_FLAG

---

# Appendix A — Example Trade Evaluations

The following examples illustrate how the proposed algorithm evaluates different types of Monopoly trades.

The purpose of these examples is not to determine whether a trade was objectively correct.

Instead, they demonstrate how strategic factors influence the final evaluation.

---

# Example 1 — Strategic Overpayment

Player A gives:

- $1800

Player B gives:

- Fourth Railroad

Board State:

- Most monopolies are blocked.
- Few developed properties exist.
- Player A already owns three railroads.

Result:

```
Player A

Receives:

Fourth Railroad

↓

Continuous economic engine

↓

Higher future income

↓

Improved negotiation power

↓

Higher Strategic Value
```

Trade Classification:

```
NO_FLAG
```

Reason:

Although Player A appears to overpay financially, the strategic gain is substantial.

This is a legitimate strategic investment.

---

# Example 2 — House Supply Control

Player A gives:

- Large amount of cash.

Player B gives:

- One property completing a monopoly.

Immediately after the trade:

Player A builds 24 houses.

Only a few houses remain in the bank.

Result:

```
House Control Bonus

+

House Denial Bonus

↓

Very High Strategic Value
```

Trade Classification:

```
NO_FLAG
```

Reason:

The player intentionally exchanged cash for board control.

The apparent financial imbalance is strategically justified.

---

# Example 3 — Dangerous Monopoly Giveaway

Player A gives:

Last property needed to complete Orange.

Player B:

Immediately builds
4 houses on every property.

Player A receives:

- Small amount of cash.

No monopoly.

No blocking property.

No future leverage.

Result:

```
BUILDABLE_MONOPOLY_GIVEN_AWAY

+

HIGHLY_SUSPICIOUS_IMBALANCE
```

Trade Classification:

```
REVIEW_RECOMMENDED
```

Reason:

Player A receives no meaningful competitive advantage while immediately creating a major threat.

---

# Example 4 — Strategic Blocking

Player A owns:

One Red.

Player B owns:

Two Reds.

Player C owns:

One Red.

Player A refuses to trade.

Result:

```
Blocking Value

+

Future Negotiation Bonus
```

Trade Classification:

```
NO_FLAG
```

Reason:

The player is preserving strategic leverage.

No monopoly is completed, but board control increases.

---

# Example 5 — Immediate Development Prevention

Player A gives:

Very large amount of cash.

Player B gives:

Critical property completing a monopoly.

Immediately after the trade:

Player A builds enough houses to leave only two houses available in the bank.

Player B cannot develop any future monopoly.

Result:

```
House Control Bonus

+

House Denial Bonus
```

Trade Classification:

```
NO_FLAG
```

Reason:

The trade appears financially unequal but creates a decisive strategic advantage.

---

# Example 6 — Symbolic Value Trade

Player A gives:

- Complete Monopoly

Player B gives:

- $1

No additional assets.

No strategic compensation.

Result:

```
SYMBOLIC_VALUE_TRADE

+

HIGHLY_SUSPICIOUS_IMBALANCE
```

Trade Classification:

```
REVIEW_RECOMMENDED
```

Reason:

The strategic value transferred is dramatically larger than the value received.

---

# Example 7 — Railroad Engine

Player A owns:

Two Railroads.

Player B owns:

Two Railroads.

Trade:

Player A receives:

Remaining two railroads.

Player B receives:

Large amount of cash.

Immediately after the trade:

Player A now owns all four railroads.

Result:

```
Railroad Engine

+

Future Income

+

Negotiation Power
```

Trade Classification:

```
NO_FLAG
```

Reason:

Although expensive, the trade creates a powerful long-term economic engine.

---

# Example 8 — Future Negotiation Leverage

Player A receives:

One Green property.

No monopoly is completed.

However:

Two different players now require that property in order to complete Green.

Result:

```
Future Negotiation Bonus

+

Blocking Value
```

Trade Classification:

```
NO_FLAG
```

Reason:

The property becomes strategically valuable despite producing no immediate income.

---

# Summary

These examples illustrate an important design principle.

The algorithm does **not** attempt to determine whether a trade looks financially fair.

Instead, it evaluates whether both players receive a reasonable strategic benefit after considering the complete board position.

A player may intentionally overpay in order to obtain:

- Immediate monopoly development.
- House supply control.
- Railroad engines.
- Strong blocking positions.
- Future negotiation leverage.

These situations should not be confused with suspicious trades.

Only when one player transfers significant strategic value without receiving a comparable competitive advantage should the algorithm generate stronger classifications.


---

# Limitations

No deterministic algorithm can perfectly evaluate Monopoly trades.

The purpose of this system is not to determine whether a trade is objectively correct or whether a player intentionally performs kingmaking.

Instead, the algorithm estimates the strategic imbalance created by a trade using a reproducible and explainable evaluation model.

Several limitations should be acknowledged.

---

## Strategic Creativity

Experienced players often perform trades that appear irrational when evaluated only by nominal value.

Examples include:

- Buying house control.
- Creating future negotiation opportunities.
- Sacrificing liquidity for long-term positioning.
- Deliberately accepting short-term weakness in exchange for strategic advantage.

The algorithm attempts to recognize these situations, but it cannot perfectly model every possible strategy.

---

## Hidden Human Intent

The algorithm evaluates board position.

It cannot determine player intent.

A suspicious trade does not necessarily imply kingmaking.

Likewise, a strategically poor trade may simply be the result of inexperience.

Intent should never be inferred directly from the algorithm.

---

## Weight Calibration

The numerical values proposed throughout this document are Specification Default Values, intended as initial estimates.

Real gameplay statistics should be used to calibrate:

- Group strategic multipliers.
- Railroad values.
- House control bonuses.
- Blocking bonuses.
- Immediate risk penalties.
- Trade ratio thresholds.

Different versions of Monopoly may require different tuning, applied through declared Implementation Overrides.

---

## False Positives

The algorithm intentionally favors false negatives over false positives.

It is preferable to miss some suspicious trades than to incorrectly classify legitimate strategic play.

Protecting strategic creativity is more important than maximizing detection rate.

---

## Future Improvements

The proposed architecture is modular.

Additional strategic components can be incorporated without changing the overall design.

Examples include:

- Positional probability.
- Dice probability.
- Jail status.
- Historical player behaviour.
- AI-assisted strategic evaluation.

These additions should complement the deterministic evaluation rather than replace it.

---

# Final Statement

This proposal should be viewed as a practical engineering solution rather than a perfect competitive evaluation system.

Its objective is to provide developers with a transparent, explainable, and computationally efficient method for identifying highly unusual trades while preserving the strategic depth that makes Monopoly negotiations interesting.


# Core Design Principles

The following principles guided the design of this algorithm.

Every future modification should preserve these principles.

---

## 1. Strategy Over Nominal Value

Strategic value is more important than printed property value.

A player may intentionally overpay in cash to obtain a decisive strategic advantage.

---

## 2. Immediate Impact Is More Important Than Future Potential

A *Buildable* monopoly is considerably more valuable than a monopoly that cannot be developed immediately (see Development Capability Predicates).

Immediate competitive impact should therefore receive greater weight.

---

## 3. Board State Matters

The same trade may be reasonable in one board position and highly suspicious in another.

The algorithm must always evaluate the current board state.

---

## 4. No Automatic Moderation

The algorithm classifies trades.

It never determines player intent.

It never applies punishments.

It never rejects trades.

---

## 5. Minimize False Positives

Protecting legitimate strategic creativity is more important than detecting every suspicious trade.

When uncertainty exists, the algorithm should prefer not flagging.

---

## 6. Every Rule Must Be Explainable

Every score assigned by the algorithm should have a deterministic explanation.

Developers should always be able to explain why a trade received a particular classification.

---

## 7. Modularity

Every strategic component should be independently adjustable.

Developers should be able to modify railroad values, group strategic multipliers, house bonuses or thresholds without changing the overall architecture.

All such modifications are declared Implementation Overrides (see Value Sources).

# Why A Static Algorithm?

This proposal intentionally starts with a deterministic model rather than an AI model.

There are several reasons for this decision.

## Explainability

Every score generated by the algorithm can be explained.

Developers can always understand why a trade received a particular evaluation.

This greatly simplifies debugging and balancing.

---

## Consistency

The same trade evaluated under the same board conditions will always produce the same result.

No randomness or model drift is introduced.

---

## Performance

The algorithm consists of simple deterministic calculations.

It can evaluate trades in real time with negligible computational cost.

---

## Tunability

Every strategic component can be adjusted independently.

Developers may modify:

- Group strategic multipliers
- House bonuses
- Railroad values
- Blocking values
- Risk penalties

without affecting the overall architecture.

Every modification is a declared Implementation Override (see Value Sources); silent tuning is forbidden.

---

## AI Can Be Added Later

Once the deterministic evaluation is complete,
an AI model may be added as a second opinion.

The AI would not replace the algorithm.

Instead, it would evaluate situations where deterministic rules cannot fully capture strategic complexity.

This layered approach combines the transparency of deterministic systems with the flexibility of AI-assisted analysis.