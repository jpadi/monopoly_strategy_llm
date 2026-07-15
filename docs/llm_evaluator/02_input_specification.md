# Monopoly Trade Evaluation Input Specification

Version: 1.0

## Purpose

This document defines the complete input model used by the Monopoly Trade Evaluation System.

Its purpose is to describe every piece of information that may be provided to the evaluator.

This document does not define how the evaluator reasons or reaches conclusions.

It only defines the meaning of each input section and the information it should contain.

The evaluator treats each input section as an independent source of evidence.

Different sources of evidence may describe the same situation from different perspectives.

These sources should complement each other whenever possible.

When multiple sources disagree, the evaluator must resolve the conflict using the reasoning process defined in the Judge Specification.

The input model is intentionally modular.

Each input section may be independently generated, omitted, or extended without affecting the meaning of the remaining sections.

The complete input is composed of the following logical sections:

1. Metadata

2. Board State (immediately before and immediately after the trade)

3. Trade Information

4. Game Configuration

5. Static Analysis Control (Optional)

6. Static Algorithm Evidence (Optional)

7. Player Profiles (Optional)

8. Decision Pattern Profiles (Optional)

Every section is described independently in the following chapters.

## Metadata

The Metadata section contains general information describing the evaluation itself.

Examples include:

- the evaluation identifier;
- the game identifier;
- the platform and game version;
- the evaluation timestamp;
- the schema version;
- the preferred report language.

Metadata exists for traceability, auditing, logging, reproducibility, and integration with external systems.

Metadata must never influence the Competitive Classification.

## Board State

The Board State represents the complete competitive state of the Monopoly game at a specific moment.

The complete input contains two Board States:

- one describing the game immediately before the trade;
- one describing the game immediately after the trade.

Unless explicitly stated otherwise, every rule in this chapter applies to both Board States.

The Board State is the primary source of evidence used by the evaluator.

Every competitive conclusion should ultimately be traceable to the Board State.

The Board State should contain enough information to allow the evaluator to completely reconstruct the current game without making assumptions.

Whenever information is missing, the evaluator should acknowledge the limitation rather than attempting to infer unknown values.

The Board State should describe the current situation of the entire game, not only the players participating in the trade.

A complete Board State should allow the evaluator to understand:

- the current position of every active player;
- every owned property;
- every unowned property;
- every monopoly;
- every incomplete monopoly;
- every mortgaged property;
- every developed property;
- every railroad;
- every utility;
- every player's liquidity;
- every player's overall financial position;
- remaining houses in the bank;
- remaining hotels in the bank;
- current game phase.

The Board State should contain factual information only.

It should not contain strategic opinions, evaluations, recommendations, or conclusions.

Its purpose is to accurately describe the current game.

Strategic interpretation belongs to the evaluator, not to the Board State.

### Board State Components

A complete Board State should describe every element that may influence the competitive evaluation of a trade.

The exact implementation is left to the input format, but the Board State should logically contain the following components.

---

#### Players

Every active player currently participating in the game.

Each player should be individually identifiable throughout the evaluation.

The Board State should provide enough information to understand each player's current competitive position.

---

#### Assets

Every game asset that may influence the evaluation.

Examples include:

- properties;
- railroads;
- utilities;
- Get Out of Jail Free cards;
- cash;
- any additional tradable assets supported by the current Monopoly implementation.

Every asset should have a clearly defined current owner.

---

#### Developments

The current development status of every property group.

This includes information necessary to understand the current building distribution across the board.

Examples include:

- houses;
- hotels;
- undeveloped monopolies;
- remaining houses available in the bank;
- remaining hotels available in the bank.

---

#### Financial State

The current financial position of every active player.

The evaluator should be able to understand each player's ability to survive, negotiate, mortgage, develop properties, and continue competing.

Examples include:

- available cash;
- mortgaged assets;
- total asset value;
- available mortgage capacity;
- other financial information relevant to the current Monopoly implementation.

---

#### Player Status

The current state of every player.

Examples include:

- board position;
- jail status;
- turn order;
- elimination status;
- any temporary condition that materially affects gameplay.

---

#### Game State

The overall competitive state of the current game.

Examples include:

- current game phase;
- remaining active players;
- available houses;
- available hotels;
- other global information that may influence competitive evaluation.

---

### Completeness

The Board State should be sufficiently complete for the evaluator to reconstruct the competitive situation without making assumptions.

Whenever relevant information is unavailable, it should be explicitly marked as unknown rather than omitted.

Providing incomplete but explicitly identified information is preferable to silently omitting important evidence.

## Player Information

Player Information describes the current state of every player in the game.

Every active player should be included, even if the player is not directly involved in the trade.

A trade between two players may significantly affect the winning chances of other players.

Therefore, excluding non-participating players may cause the evaluator to misunderstand the competitive impact of the trade.

---

### Required Player Concepts

Each player should be described with enough information to evaluate their current position.

Player Information should include:

- unique player identifier;
- player display name or label;
- active or eliminated status;
- current cash;
- current board position;
- jail status;
- turn order;
- owned assets;
- mortgaged assets;
- developed properties;
- available mortgage capacity, if calculated;
- total asset value, if calculated;
- Get Out of Jail Free cards;
- any temporary state that materially affects gameplay.

---

### Cash

Cash represents immediately available money.

Cash should not include:

- mortgage capacity;
- sellable house value;
- sellable hotel value;
- expected future rent;
- potential trade value.

Cash is important because it determines whether a player can immediately:

- pay rent;
- buy property;
- accept or propose cash trades;
- unmortgage property;
- build houses or hotels;
- survive immediate financial pressure.

---

### Liquidity

Liquidity represents the player's broader ability to generate usable cash.

Liquidity may include:

- current cash;
- mortgage capacity;
- value recoverable from selling houses;
- value recoverable from selling hotels;
- other immediately convertible resources allowed by the game configuration.

Liquidity is different from cash.

A player may have low cash but high liquidity if they own unmortgaged properties or developed monopolies.

A player may have low cash and low liquidity if most assets are already mortgaged and no developments can be sold.

Liquidity is critical when evaluating whether a player can survive after accepting a trade.

---

### Strategic Position

Player Information may optionally include precomputed factual summaries of each player's position.

Examples include:

- controlled monopolies;
- near-completed monopolies;
- railroad count;
- utility count;
- developed property count;
- mortgaged property count;
- available mortgage capacity;
- total asset value.

These summaries must remain factual.

Interpretive assessments — such as blocking power, development potential, bankruptcy risk, or threat level — are strategic evaluations.

They belong to Static Algorithm Evidence or to the evaluator itself, never to the Board State.

If calculated summaries disagree with factual data, the factual data should take priority.

## Asset Information

Asset Information describes every tradable asset currently existing in the game.

Every asset should have exactly one current owner unless the asset is still controlled by the bank.

The evaluator should always be able to determine the ownership and current state of every asset.

Assets represent objective facts.

They should never contain strategic opinions or recommendations.

---

### Asset Categories

The input may contain different categories of assets depending on the Monopoly implementation.

Examples include:

- properties;
- railroads;
- utilities;
- Get Out of Jail Free cards;
- cash;
- any additional tradable assets supported by the current game configuration.

Every asset category should be represented consistently throughout the evaluation.

---

### Ownership

Every asset should have a clearly identified owner.

Possible owners include:

- an active player;
- the bank;
- another game entity defined by the current game configuration.

Ownership should always reflect the current game state immediately before the trade.

---

### Asset State

Each asset should describe its current factual state.

Examples include:

- mortgaged or unmortgaged;
- developed or undeveloped;
- number of houses;
- number of hotels;
- current owner;
- any temporary state that materially affects gameplay.

Only factual information should be included.

Strategic interpretation belongs to the evaluator.

---

### Asset Relationships

Some assets have relationships with other assets.

Examples include:

- belonging to the same color group;
- belonging to the railroad group;
- belonging to the utility group.

These relationships should be explicitly represented whenever they influence competitive evaluation.

The evaluator should never be required to infer relationships that can be directly provided.

---

### Tradability

Asset Information should clearly indicate whether an asset can currently be traded.

Most Monopoly assets are tradable.

Some Monopoly implementations may introduce restrictions.

Whenever trading restrictions exist, they should be explicitly described by the Game Configuration rather than inferred by the evaluator.

---

### Completeness

Every tradable asset existing in the game should appear exactly once within the complete Board State.

No asset should be duplicated.

No asset should be omitted.

A complete Asset Information section should allow the evaluator to reconstruct ownership of every tradable asset without making assumptions.

## Property Information

Property Information describes every purchasable board space that can be owned, traded, mortgaged, developed, or used to collect rent.

Properties are a special category of asset because they may create monopolies, enable development, affect house supply, and generate rent.

Every property should be represented with enough information to evaluate both its current value and its strategic value.

---

### Property Identity

Each property should have a unique identifier.

The identifier should remain stable across:

- Board State;
- Trade Information;
- Static Algorithm Evidence;
- Player Profiles;
- Decision Pattern Profiles;
- output reports.

The evaluator should never need to rely only on the display name of a property when a unique identifier is available.

---

### Property Category

Each property should clearly indicate its category.

Common categories include:

- street property;
- railroad;
- utility.

The category matters because different property types create value in different ways.

Street properties may create color monopolies and development opportunities.

Railroads may create repeated cash flow and negotiation leverage.

Utilities may create variable rent and may have situational value depending on the current game.

---

### Group Membership

Every property that belongs to a group should identify that group.

Examples include:

- brown group;
- light blue group;
- pink group;
- orange group;
- red group;
- yellow group;
- green group;
- dark blue group;
- railroad group;
- utility group.

Group membership is essential for evaluating:

- monopoly completion;
- blocking value;
- development potential;
- rent potential;
- house control;
- negotiation leverage.

---

### Economic Values

Each property should provide all relevant economic values.

Examples include:

- purchase price;
- mortgage value;
- unmortgage cost;
- house cost;
- hotel cost;
- rent table;
- rent with monopoly but no houses;
- rent with each house level;
- rent with hotel.

The evaluator should use the provided values.

If provided values differ from standard Monopoly values, the provided values always take priority.

---

### Current Property State

Each property should describe its current factual state.

Examples include:

- current owner;
- mortgaged status;
- number of houses;
- hotel status;
- whether the property is currently tradable;
- whether the property is currently developable.

This information should reflect the state immediately before the trade when used as part of Board State.

---

### Development State

For street properties, development state is especially important.

The evaluator should be able to determine:

- whether the owner controls the full color group;
- whether houses can be built;
- how many houses are currently built;
- whether a hotel is currently built;
- whether the house supply limits further development;
- whether building rules restrict immediate development.

Development state strongly affects the real competitive value of a property.

A monopoly that cannot be developed immediately may be much less dangerous than a monopoly that can be fully developed at once.

---

### Strategic Importance

Property Information itself should remain factual.

However, it should contain enough data for the evaluator to determine strategic importance.

Examples of strategic importance include:

- completing a monopoly;
- blocking another player's monopoly;
- enabling immediate development;
- controlling house supply;
- creating negotiation leverage;
- increasing rent threat;
- increasing survival risk for opponents.

These conclusions should be made by the evaluator, not embedded as opinions inside the Property Information.

## Trade Information

Trade Information describes the proposed or completed exchange being evaluated.

It must describe exactly what each participating player gives and receives.

The evaluator should be able to reconstruct the trade without guessing or inferring hidden transfers.

---

### Trade Identity

Each trade should have a unique identifier.

The identifier should remain stable across:

- input data;
- Static Algorithm Evidence;
- output reports;
- logs;
- future review systems.

This allows the trade evaluation to be traced and audited.

---

### Trade Status

The trade should indicate whether it is:

- proposed;
- accepted;
- completed;
- rejected;
- cancelled.

The evaluator should know whether it is reviewing a hypothetical trade or a trade that actually changed the game state.

---

### Participants

Every player directly participating in the trade should be listed.

Each participant should be referenced using the same stable player identifier used in Player Information.

The evaluator should distinguish between:

- the player who proposed the trade;
- the player who received the proposal;
- any additional participating players, if the platform supports multi-player trades.

---

### Assets Exchanged

Every asset transferred by the trade should be listed.

Examples include:

- cash;
- properties;
- railroads;
- utilities;
- Get Out of Jail Free cards;
- any other tradeable asset supported by the game configuration.

Each transfer should clearly identify:

- the asset being transferred;
- the player giving the asset;
- the player receiving the asset.

No exchanged asset should be omitted.

---

### Cash Transfers

Cash transfers should be represented explicitly.

The evaluator should know:

- how much cash each player gives;
- how much cash each player receives;
- each player's cash before the trade;
- each player's cash after the trade.

Cash is especially important because a trade may look valuable on paper while leaving a player unable to develop, survive rent, pay mortgage interest, or absorb immediate risk.

---

### Property Transfers

Property transfers should reference the unique property identifiers defined in Property Information.

The evaluator should know whether each transferred property is:

- mortgaged;
- unmortgaged;
- developed;
- undeveloped;
- part of a monopoly;
- part of a near-monopoly;
- strategically blocking another player.

The factual property state should come from the Board State.

Trade Information should identify the transfer itself.

For every Transfer, `amount` is quantitatively meaningful only for quantitative asset types such as `cash`.

For `property` and other unique non-quantitative assets:

- `asset_id` identifies the transferred object;
- `amount` must equal `0`;
- `amount = 0` does not mean zero properties were transferred.

---

### Transfer Amount Validation

| asset_type | asset_id | amount |
|---|---|---:|
| cash | null | greater than 0 |
| property | required | 0 |
| other unique non-quantitative asset | required | 0 |
| quantitative custom asset | according to asset definition | greater than 0 |

---

### Mortgage Consequences

If a trade transfers mortgaged properties, the input should clearly describe any mandatory financial consequences created by the game configuration.

Examples include:

- immediate mortgage interest payment;
- option to keep the property mortgaged;
- requirement to unmortgage immediately;
- bankruptcy risk caused by mandatory transfer costs.

The evaluator should not infer platform-specific mortgage transfer rules if they are not provided.

---

### Before And After Comparison

The evaluator should compare the complete game state before the trade with the complete game state after the trade.

Trade Information describes the exchange.

The before and after Board States describe the result.

Together, they allow the evaluator to determine:

- liquidity changes;
- monopoly creation;
- monopoly destruction;
- blocking changes;
- development changes;
- house supply changes;
- competitive balance changes;
- immediate bankruptcy risk;
- future negotiation leverage.

---

### Completeness

Trade Information should be complete enough for the evaluator to identify every competitive consequence of the exchange.

If any part of the trade is unknown, it should be explicitly marked as unknown.

Silent omission of exchanged assets may lead to incorrect evaluation.

## Game Configuration

Game Configuration describes every rule, value, or behavior that may differ from the evaluator's default Monopoly knowledge.

The evaluator is expected to understand the standard rules and strategic concepts of Monopoly.

Game Configuration exists only to define variations introduced by the current implementation.

Whenever a configuration value is explicitly provided, it overrides the evaluator's default Monopoly knowledge.

The evaluator must never replace a provided configuration value with a standard Monopoly value.

---

### Purpose

The purpose of Game Configuration is to eliminate ambiguity.

Every rule capable of affecting the competitive evaluation of a trade should be explicitly defined whenever it differs from the standard Monopoly rules.

Rules that exactly match the evaluator's standard Monopoly knowledge do not need to be included.

---

### Economic Configuration

Game Configuration may define the economic values used by the current implementation.

Examples include:

- property purchase prices;
- mortgage values;
- unmortgage costs;
- house costs;
- hotel costs;
- building sell-back and liquidation rules;
- custom group strategic multipliers;
- rent tables;
- starting cash;
- salary for passing GO;
- tax values.

---

### Building Rules

Building rules directly affect competitive value.

Examples include:

- house supply limits;
- hotel supply limits;
- even building requirements;
- development restrictions;
- hotel replacement rules;
- house shortage behavior.

---

### Trading Rules

Some Monopoly implementations modify trading behavior.

Examples include:

- assets that cannot be traded;
- timing restrictions;
- multiplayer trade support;
- mortgage transfer rules;
- auction behavior after declined purchases.

---

### Jail Rules

Different Monopoly implementations may modify jail behavior.

Examples include:

- maximum jail turns;
- bail amount;
- Get Out of Jail Free card behavior;
- mandatory payment rules;
- custom jail mechanics.

---

### Optional House Rules

Some implementations introduce optional house rules.

Examples include:

- Free Parking jackpot;
- auction variations;
- custom bankruptcy rules;
- custom income rules;
- custom development rules.

Every optional rule that may influence competitive evaluation should be explicitly described.

---

### Platform-Specific Rules

Online platforms may introduce behaviors that do not exist in the original board game.

Examples include:

- automatic auctions;
- automatic mortgage handling;
- automatic bankruptcy handling;
- forced trade limitations;
- turn timers;
- AI player behavior;
- platform-specific mechanics.

These rules should be documented whenever they materially affect trade evaluation.

---

### Configuration Completeness

Only configuration values that differ from the evaluator's default Monopoly knowledge should be provided.

The evaluator should rely on its existing Monopoly knowledge whenever no alternative configuration is specified.

This keeps the input concise while ensuring deterministic evaluation across different Monopoly implementations.

## Static Analysis Control (Optional)

Static Analysis Control declares how the evaluator must handle Static Algorithm Evidence for the current evaluation.

It answers two questions explicitly:

- whether supplied Static Algorithm Evidence must be consumed;
- whether the Judge is authorized to execute the Static Algorithm itself when no usable supplied evidence exists (LLM Static Fallback).

Fallback execution is never inferred from the mere availability of specification documents.

It must be explicitly authorized by this section.

The runtime behavior produced by each mode — including evidence validation, fallback activation, and execution reporting — is defined by the Judge Specification (`01_judge.md`).

The serialized structure is defined by the Input Schema (`03_input_schema.md`).

---

### Static Analysis Modes

Static Analysis Control declares exactly one of the following modes.

#### auto

1. Use valid supplied Static Algorithm Evidence when available.
2. Otherwise, execute LLM Static Fallback only when:
   - fallback is explicitly allowed by this section;
   - the required Static Algorithm Specification is positively identified;
   - every mandatory dependency is available and version-compatible.
3. Otherwise, continue the evaluation without Static Algorithm Evidence and report the limitation.

#### require_provided_evidence

- Use only supplied Static Algorithm Evidence.
- Never execute LLM Static Fallback.
- If no usable supplied evidence exists, continue without static evidence and report the limitation.

This mode guarantees that every static calculation was produced by deterministic software.

#### allow_llm_fallback

1. Use valid supplied Static Algorithm Evidence when available.
2. Otherwise, execute LLM Static Fallback when the required Static Algorithm Specification and every mandatory dependency are available and version-compatible.
3. If fallback cannot execute, report the limitation and continue using the remaining evidence.

#### disable_static_analysis

- Do not consume supplied Static Algorithm Evidence.
- Do not execute LLM Static Fallback.
- Perform the evaluation using the remaining evidence only.

---

### Fallback Authorization

Independently of the mode, Static Analysis Control declares whether fallback is allowed.

In `auto` mode, fallback may execute only when fallback is explicitly allowed.

In `allow_llm_fallback` mode, the mode itself grants the authorization.

In `require_provided_evidence` and `disable_static_analysis` modes, fallback never executes.

---

### Required Algorithm And Dependencies

Static Analysis Control may declare:

- the required Static Algorithm, identified by its specification identifier and version;
- every mandatory dependency, identified the same way.

These declarations are matched against the Specification Identity metadata exposed by the Static Algorithm Specification and its dependencies.

When no required algorithm or dependencies are declared, the canonical specifications distributed with this repository are used:

- Static Algorithm Specification — `monopoly_static_algorithm`;
- Risk Reference — `monopoly_risk_reference`.

---

### Default Behavior

Static Analysis Control is optional.

When it is absent, the evaluator must behave exactly as if the following had been supplied:

- mode: `auto`;
- fallback not allowed.

This default is backward compatible: supplied Static Algorithm Evidence is consumed as before, and the Judge never executes the Static Algorithm without explicit authorization.

This default is documented identically in the Input Schema, the Judge Specification, and the repository README.

## Static Algorithm Evidence (Optional)

Static Algorithm Evidence contains deterministic calculations generated before the trade is evaluated.

Its purpose is to provide additional objective evidence to the evaluator.

The evaluator remains fully responsible for the final competitive classification.

Static Algorithm Evidence should never replace the evaluator's own reasoning.

The complete evidence format is defined by the Static Algorithm Evidence Specification (`04_static_algorithm_specification.md`).

A concrete deterministic algorithm producing this evidence is defined in `../static_evaluator/static_algorithm_specification.md`.

---

### Purpose

The purpose of Static Algorithm Evidence is to expose deterministic analysis that may help the evaluator better understand the competitive situation.

Rather than providing only a final score, the Static Algorithm should expose its complete reasoning process whenever practical.

The evaluator should be able to understand how every important conclusion was reached.

---

### Intermediate Calculations

Whenever possible, the Static Algorithm should provide intermediate calculations in addition to final results.

Examples include:

- property valuations;
- liquidity calculations;
- mortgage calculations;
- development calculations;
- monopoly calculations;
- blocking calculations;
- railroad calculations;
- utility calculations;
- house control calculations;
- hotel control calculations;
- bankruptcy risk calculations;
- negotiation leverage calculations;
- competitive advantage calculations;
- trade ratio calculations.

Every intermediate calculation follows the canonical Intermediate Calculation Item structure defined by the Static Algorithm Evidence Specification (`04_static_algorithm_specification.md`).

Intermediate calculations provide transparency and allow the evaluator to independently verify the reasoning.

---

### Final Results

The Static Algorithm may also provide summarized conclusions.

Examples include:

- total player valuation;
- competitive ratios;
- trade balance;
- estimated strategic advantage;
- estimated strategic disadvantage;
- calculated bonuses;
- calculated penalties.

These summaries should always be supported by the underlying calculations whenever possible.

---

### Evidence, Not Authority

Static Algorithm Evidence represents expert deterministic analysis.

It is an important source of evidence.

It is not the final authority.

The evaluator may:

- fully agree;
- partially agree;
- disagree.

Whenever disagreement exists, the evaluator should explain which evidence supports the alternative conclusion.

---

### Multiple Static Algorithms

The input may contain evidence generated by multiple independent Static Algorithms.

Different algorithms may use different evaluation methods.

The evaluator should consider the reasoning provided by each algorithm before reaching a conclusion.

Agreement between multiple algorithms may increase confidence.

Disagreement does not automatically invalidate any algorithm.

Instead, disagreements should be analysed using the available evidence.

---

### Transparency

Static Algorithm Evidence should prioritize transparency over simplicity.

Providing the reasoning behind a calculation is generally more valuable than providing only a final score.

The evaluator should be able to trace important conclusions back to their supporting calculations whenever practical.


## Player Profiles (Optional)

Player Profiles summarize the historical decision-making behavior of individual players.

Their purpose is to provide additional context that may help explain why a player values certain trades differently.

Player Profiles are contextual evidence.

They are not objective evidence of the current game.

The evaluator must never allow historical behavior to override the factual Board State.

---

### Purpose

The purpose of a Player Profile is to summarize how a player typically approaches Monopoly over many games.

Player Profiles should describe behavioral tendencies rather than isolated decisions.

The evaluator should use this information only after understanding the current game.

---

### Historical Behavior

A Player Profile may summarize recurring tendencies such as:

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

These tendencies should represent long-term observations rather than individual games.

---

### Statistical Information

A Player Profile may also include statistical summaries.

Examples include:

- games analyzed;
- estimated skill level;
- historical win rate;
- average finishing position;
- average trade frequency;
- average cash reserve;
- average mortgage usage;
- average development timing.

Statistical summaries help estimate the reliability of the observed behavioral tendencies.

---

### Behavioral Consistency

Some players consistently follow similar decision-making patterns.

Others adapt significantly between games.

Whenever available, the Player Profile should describe the player's overall consistency.

Highly consistent players may be more predictable.

Highly adaptive players may intentionally deviate from historical behavior.

---

### Use During Evaluation

Player Profiles should only be used to better understand possible reasoning behind a trade.

They should never determine whether a trade is competitively correct.

A historically strong player may make a poor trade.

A historically weak player may make an excellent trade.

The current game always has higher priority than historical behavior.

---

### Missing Player Profiles

Player Profiles are optional.

If no Player Profile is available, the evaluator should continue using the remaining evidence.

The absence of a Player Profile should never reduce the quality of the competitive evaluation.

It only reduces the amount of contextual information available to explain the player's possible reasoning.

## Decision Pattern Profiles (Optional)

Decision Pattern Profiles describe documented Monopoly decision-making patterns.

Their purpose is to help explain why a player may reasonably have accepted or proposed a trade.

Decision Pattern Profiles are explanatory evidence.

They are not used to determine the competitive classification of a trade.

The competitive classification must always be completed before Decision Pattern Profiles are analysed.

---

### Purpose

The purpose of a Decision Pattern Profile is to document a recognizable pattern of Monopoly decision making.

A pattern may describe:

- a competitive strategy;
- a behavioral tendency;
- a recurring evaluation bias;
- a non-competitive pattern;
- any other documented decision process.

The evaluator compares the observed trade against every provided Decision Pattern Profile to determine whether meaningful similarities exist.

---

### Pattern Categories

Decision Pattern Profiles may belong to different categories.

Examples include:

- Competitive Patterns;
- Behavioral Patterns;
- Evaluation Biases;
- Non-Competitive Patterns.

The category does not determine whether the pattern is good or bad.

It only describes the nature of the documented decision process.

---

### Pattern Matching

A trade may:

- match no documented patterns;
- partially match one pattern;
- strongly match one pattern;
- partially match multiple patterns.

The evaluator should identify every meaningful match.

Not every pattern needs to be reported.

Only patterns that materially contribute to understanding the trade should appear in the final report.

---

### Pattern Similarity

A matching Decision Pattern Profile indicates similarity.

It does not prove that the player intentionally followed that pattern.

Likewise, the absence of a matching profile does not imply irrational play or malicious intent.

Decision Pattern Profiles provide possible explanations.

They do not establish facts about player intent.

---

### Independence From Competitive Evaluation

Decision Pattern Profiles must never influence the competitive classification.

The evaluator should first determine the competitive impact of the trade using objective evidence.

Only after completing the competitive evaluation should the evaluator compare the trade against the documented Decision Pattern Profiles.

The competitive classification must never change because of a Decision Pattern match.

---

### Extensibility

New Decision Pattern Profiles may be added over time without changing the evaluator.

The evaluator should analyze every provided profile using the same reasoning process.

Undocumented patterns should never be invented.

Only documented Decision Pattern Profiles may be considered during the explanation phase.

## Relationships Between Input Sections

The input model is composed of independent but interconnected sections.

Each section has a unique responsibility.

Whenever multiple sections describe the same concept, they should complement each other rather than duplicate information.

The evaluator should understand how these sections relate to one another before beginning the evaluation.

---

### Board State

The Board State represents the factual state of the Monopoly game.

It is the primary source of truth for the current game.

Whenever another section references the current game, it should reference the Board State rather than redefining the same information.

---

### Trade Information

Trade Information describes only the exchange being evaluated.

It should never redefine the complete Board State.

Instead, it references players and assets already described by the Board State.

---

### Game Configuration

Game Configuration defines the rules under which the current game operates.

It affects the interpretation of every other input section.

Whenever Game Configuration explicitly defines a rule or value, it overrides the evaluator's default Monopoly knowledge.

---

### Static Analysis Control

Static Analysis Control governs only how Static Algorithm Evidence is obtained and consumed.

It never describes the game, the trade, or the players.

It must never influence the Competitive Classification beyond determining which static evidence is available to the evaluator.

---

### Static Algorithm Evidence

Static Algorithm Evidence analyzes the current Board State.

It should never replace or modify factual information.

Instead, it provides deterministic interpretations and calculations derived from the Board State.

It may be supplied in the input by deterministic software, or generated by the Judge itself under the LLM Static Fallback rules defined by the Judge Specification, when explicitly authorized by Static Analysis Control.

Both origins use the same canonical evidence structure.

---

### Player Profiles

Player Profiles summarize historical player behavior.

They describe the player rather than the current game.

Player Profiles provide context.

They must never replace factual evidence contained in the current Board State.

---

### Decision Pattern Profiles

Decision Pattern Profiles describe documented Monopoly decision patterns.

They are completely independent from the current game.

They describe how certain types of Monopoly decisions typically appear.

The evaluator compares the observed trade against these documented patterns only after completing the competitive evaluation.

---

### Overall Relationship

The evaluator should understand the logical flow of information.

Metadata identifies the evaluation.

Board State describes the current game.

Trade Information describes what changes.

Game Configuration defines how the game operates.

Static Analysis Control defines how Static Algorithm Evidence is obtained.

Static Algorithm Evidence provides deterministic analysis.

Player Profiles provide historical context.

Decision Pattern Profiles provide possible explanations.

Together, these sections provide the complete body of evidence required for the evaluation.

No single section should be treated as the absolute authority.

The evaluator should consider every available source of evidence according to the reasoning process defined in the Judge Specification.

## Input Quality Guidelines

The quality of the evaluator's conclusions depends directly on the quality of the provided input.

More complete, consistent, and accurate input produces more reliable evaluations.

The evaluator should never compensate for poor input quality by inventing missing information.

---

### Completeness

Whenever possible, provide complete information.

Complete input allows the evaluator to fully reconstruct the competitive situation.

Incomplete information increases uncertainty and should reduce confidence accordingly.

---

### Consistency

Information provided by different input sections should be internally consistent.

For example:

- property ownership should match across the Board State and Trade Information;
- player identifiers should remain identical throughout the input;
- property identifiers should be reused consistently;
- Game Configuration should not contradict the Board State.

Whenever inconsistencies are detected, the evaluator should identify them before continuing the evaluation.

---

### Traceability

Every important conclusion should be traceable back to one or more input sections.

Whenever possible, derived calculations should reference the original data used to produce them.

This allows both the evaluator and future reviewers to verify the reasoning process.

---

### Normalization

The same concept should always be represented in the same way.

Examples include:

- player identifiers;
- property identifiers;
- asset identifiers;
- monetary values;
- property groups;
- board positions.

Consistent representation reduces ambiguity and improves evaluation quality.

---

### Independence

Each input section should have a single responsibility.

Avoid duplicating the same information across multiple sections unless duplication is necessary to improve clarity or traceability.

Whenever duplication exists, one source should be considered the factual source of truth, while the other should only reference or derive from it.

---

### Optional Sections

Some input sections are optional.

Optional sections provide additional context but should never become mandatory for producing a valid evaluation.

The evaluator should produce the best possible evaluation using the information that is available.

Missing optional sections should reduce contextual understanding, not prevent evaluation.

---

### Extensibility

The input model should allow new evidence sources to be introduced without changing the meaning of existing sections.

Additional sections should complement the existing evidence rather than replacing it.

The evaluator should treat every new documented evidence source according to the reasoning principles defined in the Judge Specification.