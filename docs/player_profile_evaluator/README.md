# Player Profile Evaluator

## Overview

The Player Profile Evaluator is a future component of the Monopoly Trade Evaluation System.

Unlike the Static Evaluator and the LLM Judge, this component does **not** evaluate a single Monopoly trade.

Instead, it analyzes a player's historical games in order to construct a long-term behavioral profile.

The objective is to summarize how a player typically approaches Monopoly over many games.

The resulting Player Profile may optionally be provided to the Judge as contextual evidence during trade evaluation.

The Player Profile Evaluator is intentionally independent from the current game.

Its output represents historical behavior rather than current competitive evidence.

---

# Position Within The Architecture

```text
                         Monopoly Games
                                │
                     Historical Game Database
                                │
                                ▼
                  Player Profile Evaluator
                                │
                                ▼
                        Player Profiles
                                │
                                ▼
                           LLM Judge
                                ▲
                                │
                 Static Algorithm Evidence
                                ▲
                                │
                      Static Evaluator
                                ▲
                                │
                         Current Game
```

The three evaluators have different responsibilities.

The Static Evaluator analyzes the current game.

The Player Profile Evaluator analyzes historical games.

The Judge combines both sources of information to produce the final competitive evaluation.

---

# Purpose

The objective of the Player Profile Evaluator is to answer questions such as:

- How does this player usually negotiate?
- How conservative is this player?
- How much liquidity does this player usually preserve?
- Does this player frequently prioritize blocking?
- Does this player usually construct Railroad Engines?
- Does this player often mortgage aggressively?
- Does this player frequently overpay for strategic assets?
- Does this player usually delay monopoly activation?
- How consistently does this player follow similar strategic principles?

The evaluator should describe recurring tendencies rather than isolated decisions.

---

# Philosophy

The Player Profile Evaluator does not determine whether a player is correct.

It only summarizes how the player has historically made decisions.

A Player Profile should never contain:

- trade recommendations;
- strategic rankings;
- competitive classifications;
- predictions;
- moderation decisions.

Instead, it should provide descriptive behavioral information.

---

# Relationship With The Judge

The Judge may optionally receive one Player Profile for every active player.

Player Profiles provide historical context.

They never replace the Board State.

They never replace Static Algorithm Evidence.

They never override deterministic evidence generated from the current game.

For example:

A player may historically prefer Railroad Engines.

However, if the current trade objectively creates a stronger Orange Monopoly, the Judge should evaluate the trade based on the current board rather than the player's historical preferences.

Historical behavior provides context.

The current game provides evidence.

---

# Expected Inputs

Although not yet formally specified, the future Player Profile Evaluator is expected to receive information such as:

- complete historical games;
- historical Board States;
- historical trades;
- historical Static Algorithm Evidence;
- historical Judge evaluations;
- final game outcomes;
- game metadata;
- platform information.

Unlike the Judge, the Player Profile Evaluator analyzes multiple games rather than one isolated position.

---

# Expected Outputs

The future evaluator is expected to generate a Player Profile describing long-term behavioral tendencies.

Examples include:

- liquidity preference;
- blocking preference;
- monopoly preference;
- railroad preference;
- financing discipline;
- development timing;
- mortgage behavior;
- negotiation style;
- risk tolerance;
- strategic consistency;
- preferred game phase;
- endgame tendencies.

Whenever possible, every conclusion should be supported by measurable historical evidence.

---

# Expected Metrics

Future versions may calculate metrics such as:

- games analyzed;
- win rate;
- average finishing position;
- average liquidity;
- average monopoly count;
- average railroad ownership;
- average houses built;
- average hotels built;
- average mortgage usage;
- average trade frequency;
- average cash reserve;
- average risk exposure;
- average blocking score.

The evaluator should prioritize objective statistics over subjective interpretation.

---

# Expected Behavioral Analysis

Future versions may detect recurring behavioral patterns.

Examples include:

- Liquidity First
- Aggressive Expansion
- Strategic Overpayment
- Railroad Specialist
- Blocking Specialist
- Conservative Financier
- Monopoly Builder
- Survival Player
- Adaptive Player
- Highly Consistent Player

These patterns describe historical tendencies.

They do not imply that the player will behave the same way in every future game.

---

# Confidence

Every Player Profile should include an estimate of its reliability.

Confidence should depend on factors such as:

- number of games analyzed;
- consistency of observed behavior;
- completeness of historical data;
- agreement between observed metrics.

Confidence measures the reliability of the profile.

It does not measure player skill.

---

# Future Documentation

The current version intentionally provides only a conceptual overview.

Future versions of this component may include:

```text
01_profile_evaluator.md

02_input_specification.md

03_input_schema.md

04_output_specification.md

05_output_schema.md

06_behavior_knowledge_base.md

07_profile_generation_algorithm.md
```

The structure intentionally mirrors the separation between conceptual specifications and schemas already used by the LLM Evaluator, although the exact document numbering may differ.

This consistency allows every component of the Monopoly Trade Evaluation System to evolve independently while maintaining a common design philosophy.

---

# Design Principles

The Player Profile Evaluator should follow the same core principles as every other component of the project.

- Historical evidence should be preferred over intuition.
- Every conclusion should be reproducible.
- Behavioral tendencies should be supported by measurable statistics whenever possible.
- The evaluator should describe players rather than judge them.
- Historical behavior should never override deterministic evidence from the current game.
- The generated Player Profile should remain implementation independent.

---

# Relationship With The Static Evaluator

The Player Profile Evaluator should not duplicate the work of the Static Evaluator.

Instead, it should consume deterministic evidence already produced by Static Evaluators whenever available.

The Static Evaluator analyzes one game.

The Player Profile Evaluator analyzes many games.

Whenever possible, Player Profiles should be generated from deterministic evidence rather than directly from raw game states.

This approach improves:

- consistency;
- explainability;
- reproducibility;
- implementation independence.

---

# Relationship With The Strategy Knowledge Base

The Player Profile Evaluator should reuse the same Strategy Knowledge Base used by the Judge.

Strategies should never be defined independently.

Instead, the evaluator should detect how frequently each documented strategy appears across the player's historical games.

This ensures that:

- strategy definitions remain centralized;
- historical analysis remains consistent with trade evaluation;
- future strategy improvements automatically benefit every component.

---

# Future Player Archetypes

Future versions of the Player Profile Evaluator may classify players into high-level archetypes.

Examples include:

- Conservative Investor
- Aggressive Developer
- Railroad Specialist
- Monopoly Builder
- Negotiation Specialist
- Liquidity First Player
- Adaptive Strategist

Player Archetypes should summarize recurring tendencies.

They should never replace the underlying behavioral metrics.

Archetypes are intended to improve explainability rather than increase evaluation accuracy.

---

# Continuous Profile Evolution

Player Profiles are expected to evolve over time.

Every newly analyzed game may strengthen, weaken, or modify previously observed behavioral tendencies.

The evaluator should therefore generate profiles that continuously evolve as additional historical data becomes available.

Older observations should remain available for traceability whenever practical.

Player Profiles should represent the player's current long-term tendencies rather than permanently preserving outdated behavior.

---

# Relationship With Decision Pattern Profiles

Player Profiles and Decision Pattern Profiles describe different concepts.

Player Profiles describe an individual player.

Decision Pattern Profiles describe a documented Monopoly decision pattern that may be exhibited by many different players.

A Player Profile may indicate that a player frequently exhibits certain documented Decision Patterns.

However, Decision Pattern Profiles remain independent from any individual player.

This separation allows new Decision Patterns to be introduced without modifying existing Player Profiles.

Current Game
      │
      ▼
Static Evaluator
      │
      ▼
Static Evidence
      │
      ├──────────────┐
      ▼              ▼
LLM Judge     Historical Database
                     │
                     ▼
          Player Profile Evaluator
                     │
                     ▼
             Updated Player Profile

---

# Project-Wide Principles

Project-wide principles — Explainability, Deterministic First Philosophy, Modular Evolution, Research-Driven Development, Canonical Definitions, and Version Compatibility — are defined once in the root `README.md`.

The Player Profile Evaluator follows every one of those principles.