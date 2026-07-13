# Monopoly Trade Evaluation System

## Overview

The Monopoly Trade Evaluation System is a research project that defines two complementary approaches for evaluating Monopoly trades.

The project intentionally separates **deterministic analysis** from **strategic interpretation**.

This separation allows deterministic software, Large Language Models, or hybrid systems to produce transparent, explainable and auditable trade evaluations.

The project is implementation independent.

No programming language, Monopoly engine or AI framework is required.

Instead, the repository provides formal specifications describing the required inputs, outputs, algorithms and strategic knowledge.

---

# Project Structure

```text
.
├── static_evaluator
│   ├── risk_reference.md
│   └── static_algorithm_specification.md
│
├── llm_evaluator
│   ├── 01_judge.md
│   ├── 02_input_specification.md
│   ├── 03_input_schema.md
│   ├── 04_static_algorithm_specification.md
│   ├── 05_output_specification.md
│   ├── 06_output_schema.md
│   └── 07_strategy_knowledge_base.md
│
└── player_profile_evaluator
    └── README.md
```

The repository is intentionally divided into two independent specification components:

- **Static Evaluator**
- **LLM Evaluator**

A third component, the **Player Profile Evaluator**, is currently conceptual and is described later in this document.

Both evaluators may be used independently or combined into a hybrid evaluation pipeline.

---

# Static Evaluator

The Static Evaluator performs deterministic analysis.

Its responsibility is to measure the objective competitive consequences produced by a Monopoly trade.

Typical calculations include:

- monopoly creation;
- monopoly loss;
- liquidity;
- mortgage capacity;
- development simulation;
- railroad evaluation;
- blocking analysis;
- house control;
- rent exposure;
- repair exposure;
- immediate risk analysis;
- deterministic labels;
- deterministic warnings;
- deterministic scores.

The Static Evaluator does **not** determine player intent.

It only produces deterministic evidence.

The implementation is completely described by:

```text
static_evaluator/static_algorithm_specification.md
```

Reference values used by the algorithm are contained inside:

```text
static_evaluator/risk_reference.md
```

The evidence produced by the Static Evaluator shall conform to the Static Algorithm Evidence Specification:

```text
llm_evaluator/04_static_algorithm_specification.md
```

The Static Evaluator may internally classify a trade as `REVIEW_RECOMMENDED`.

This classification is a deterministic internal flag.

It is intentionally distinct from the reasoned review recommendations produced by the Judge, which interpret deterministic evidence within its strategic context.

---

# LLM Evaluator

The LLM Evaluator performs strategic interpretation.

It consumes:

- Monopoly game state;
- trade information;
- optional Static Analysis Control instructions;
- optional Static Algorithm Evidence.

Its responsibility is to determine:

- the Competitive Classification;
- the Competitive Evaluation;
- the Supporting Evidence;
- the Decision Pattern Analysis, including detected strategies;
- the Confidence Assessment;
- the Final Summary.

The LLM Evaluator never determines player intent.

It never evaluates fairness, ethics, or sportsmanship.

These exclusions are defined by the Judge Specification (`llm_evaluator/01_judge.md`).

Unlike the Static Evaluator, the LLM Evaluator reasons using Monopoly strategy rather than deterministic calculations.

---

# Operating Modes

The system supports three operating modes.

The mode used by an evaluation is controlled explicitly by the `static_analysis_control` input section, described below.

## Normal Hybrid Mode

```text
Game State
    ↓
Static Evaluator
    ↓
Static Algorithm Evidence
    ↓
LLM Judge
    ↓
Final Competitive Evaluation
```

This is the preferred mode.

Deterministic software executes the Static Algorithm and supplies the resulting Static Algorithm Evidence to the Judge.

The Static Evaluator produces objective evidence.

The Judge interprets that evidence using strategic knowledge.

This architecture maximizes:

- determinism;
- explainability;
- reproducibility;
- transparency.

Valid supplied evidence always has precedence: the Judge consumes it and does not recalculate the complete Static Algorithm.

---

## LLM Static Fallback Mode

```text
Game State
+
Static Algorithm Specification
+
Risk Reference
+
Explicit Input Authorization
    ↓
LLM Judge executes Static Algorithm
    ↓
Judge-generated Static Algorithm Evidence
    ↓
Competitive Evaluation
    ↓
Final Output containing generated evidence
```

When no usable Static Algorithm Evidence is supplied and the input explicitly authorizes it, the Judge executes the Static Algorithm Specification itself and generates the same canonical Static Algorithm Evidence that deterministic software would normally provide.

Key properties of this mode:

- **Explicit input authorization is required.** Fallback never activates merely because the specification files are present. The input must authorize it through `static_analysis_control` (`mode = allow_llm_fallback`, or `mode = auto` with `fallback_allowed = true`).
- **The specification and its dependencies are positively identified.** The Static Algorithm Specification and the Risk Reference expose stable Specification Identity metadata (`specification_type`, `specification_id`, `specification_version`). Fallback executes only when the required identities are found and the versions are compatible.
- **Generated evidence is returned, not hidden.** The complete generated Static Algorithm Evidence is returned in the Judge output (`static_analysis_result.generated_static_algorithm_evidence`). A prose summary is never an acceptable substitute.
- **Fallback follows the same evidence contract as deterministic software.** The generated evidence uses the same canonical structure, intermediate calculations, statuses, and traceability rules defined by the Static Algorithm Evidence Specification.
- **Deterministic software remains preferred.** Fallback is a controlled substitute, not a replacement for the Static Evaluator.

Fallback limitations:

- increased token usage;
- greater arithmetic-error risk than deterministic software;
- slower execution;
- stronger dependency on complete input, because the Judge cannot query the platform for missing values;
- mandatory exposure of all intermediate calculations, which increases output size.

The complete fallback rules — evidence validation, activation conditions, the mandatory execution procedure, and the separation between static execution and Judge reasoning — are defined by the Judge Specification (`llm_evaluator/01_judge.md`).

---

## LLM Evaluation Without Static Analysis

```text
Game State
    ↓
LLM Judge
    ↓
Competitive Evaluation without Static Algorithm Evidence
```

This mode occurs when:

- the input declares `mode = disable_static_analysis`; or
- no usable Static Algorithm Evidence is supplied and fallback is not authorized (including the default configuration); or
- fallback is authorized but cannot execute (for example, an incompatible specification version).

The Judge performs the Competitive Evaluation using the remaining evidence, reports the missing static analysis as a limitation, and may reduce confidence accordingly.

---

## Static Analysis Input Control

The `static_analysis_control` input section declares how Static Algorithm Evidence is handled:

```json
{
  "static_analysis_control": {
    "mode": "auto",
    "fallback_allowed": true,
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
}
```

The supported modes are:

- `auto` — use valid supplied evidence; otherwise execute fallback only when `fallback_allowed = true` and the required specifications are available and compatible; otherwise continue without static evidence and report the limitation;
- `require_provided_evidence` — use only supplied evidence; never execute fallback;
- `allow_llm_fallback` — use valid supplied evidence; otherwise execute fallback when the required specifications are available and compatible;
- `disable_static_analysis` — consume no static evidence and execute no fallback.

When the section is absent, the default is:

```json
{
  "mode": "auto",
  "fallback_allowed": false
}
```

This default is backward compatible: supplied evidence is consumed as before, and the Judge never executes the Static Algorithm without explicit authorization.

The corresponding output section, `static_analysis_result`, reports the requested mode, the runtime execution mode (`STATIC_EVIDENCE_PROVIDED`, `LLM_STATIC_FALLBACK`, or `NO_STATIC_ANALYSIS`), the evidence provenance, the algorithm and dependency versions, the execution status, and any generated evidence.

---

## Component Independence

Every combination remains valid:

- the Static Evaluator may operate independently, without the LLM Evaluator — suitable for automated moderation, replay analysis, statistical analysis, and trade scoring;
- the Judge may consume supplied Static Algorithm Evidence (Normal Hybrid Mode);
- the Judge may execute the Static Algorithm itself when explicitly authorized (LLM Static Fallback Mode);
- the Judge may operate without any static analysis.

---

# Static Algorithm Specification

The project contains two complementary documents describing Static Algorithms:

- `static_evaluator/static_algorithm_specification.md` defines a concrete deterministic algorithm, including execution order, formulas, scoring, and pseudocode;
- `llm_evaluator/04_static_algorithm_specification.md` (the Static Algorithm Evidence Specification) defines the evidence format that every Static Algorithm must produce for the Judge.

The Static Algorithm Specification intentionally defines **behavior**, not implementation.

It specifies:

- execution order;
- deterministic calculations;
- formulas;
- labels;
- warnings;
- scoring;
- pseudocode;
- deterministic rules.

The specification is implementation independent.

It is intended for:

- software engineers implementing the algorithm;
- Large Language Models generating an implementation;
- the LLM Judge executing the algorithm directly under LLM Static Fallback Mode, when explicitly authorized by the input.

A code-generation LLM should be capable of implementing the algorithm when provided with:

- the Static Algorithm Specification;
- an existing Monopoly codebase.

No assumptions are made regarding:

- programming language;
- architecture;
- project organization.

---

# Judge

The Judge is the highest-level reasoning component.

Its responsibility is **not** to calculate Monopoly mechanics.

Instead, it interprets deterministic evidence within its strategic context.

The Judge determines:

- detected strategies;
- strategic consistency;
- competitive consequences;
- review recommendations;
- final evaluation.

Strategies documented in the Strategy Knowledge Base are provided to the Judge as Decision Pattern Profiles, using the mapping defined in `llm_evaluator/07_strategy_knowledge_base.md`.

Whenever Static Algorithm Evidence is available, the Judge should consume it.

Whenever deterministic evidence is unavailable and the input explicitly authorizes it, the Judge executes the Static Algorithm itself under LLM Static Fallback Mode and generates the same canonical evidence before continuing with the evaluation.

The Judge never executes the Static Algorithm without that explicit authorization.

---

# Strategy Knowledge Base

The Strategy Knowledge Base documents consolidated Monopoly strategy.

It is **not** an implementation guide.

It defines:

- recognized strategies;
- strategic objectives;
- observable indicators;
- expected benefits;
- accepted risks;
- counter strategies;
- strategy relationships.

The Judge uses this document to determine which strategic concepts are represented by the evaluated trade.

Strategy Knowledge Base entries are delivered to the Judge as Decision Pattern Profiles.

The mapping between strategy definitions and Decision Pattern Profiles is defined inside the Strategy Knowledge Base itself.

---

# Risk Reference

The Risk Reference is an active dependency of the Static Evaluator, not standalone documentation.

It provides two separable things:

- the normative exposure methodology — development normalization, worst-case landing selection, and the Total Exposure rule (landing plus repair);
- the classic-default exposure tables — rent matrices, repair tables, and reference values for the standard Monopoly board, used when the Board State and Game Configuration supply no authoritative values.

The Static Evaluator's Risk Coverage calculation (Step 9 of the Static Algorithm Specification) consumes this methodology directly: it derives the worst currently collectible exposure and compares it against the player's immediately accessible financial resources on each side of the trade.

The result contributes positively or negatively to the deterministic score — negative when the player cannot financially absorb the exposure, positive when the player can — and the score strength grows with the size of the deficit or the remaining surplus.

Every calculation, including the exposure source tables used, is returned as deterministic evidence.

LLM Static Fallback executes the same Risk Reference methodology and produces the same risk evidence items as deterministic software.

---

# Conceptual Models and Schemas

The project intentionally separates conceptual documentation from structural schemas.

The input model and the output model each pair a conceptual specification with a corresponding schema:

- Input Specification (`llm_evaluator/02_input_specification.md`) ↔ Input Schema (`llm_evaluator/03_input_schema.md`);
- Output Specification (`llm_evaluator/05_output_specification.md`) ↔ Output Schema (`llm_evaluator/06_output_schema.md`).

Documents describing reasoning, knowledge, or algorithms — the Judge Specification, the Strategy Knowledge Base, the Static Algorithm Specifications, and the Risk Reference — intentionally have no schema.

The conceptual document defines:

- semantics;
- responsibilities;
- interpretation;
- business rules.

The schema defines:

- structure;
- required fields;
- validation rules;
- data types.

This separation keeps the documentation readable while allowing strict validation.

---

# Synchronization Requirement

Conceptual specifications and schemas shall always remain synchronized.

Whenever a conceptual specification changes:

- its corresponding schema shall also be updated.

Whenever a schema changes:

- its conceptual specification shall also be updated.

Neither document should evolve independently.

Keeping both synchronized guarantees that:

- implementations remain compatible;
- generated code remains valid;
- LLMs receive consistent documentation;
- validation schemas accurately represent the conceptual model.

---

# Design Philosophy

The project follows several fundamental principles.

- Deterministic calculations should be explainable.
- Strategic reasoning should always be evidence-driven.
- Every important conclusion should be reproducible.
- Specifications should remain implementation independent.
- AI reasoning should complement deterministic algorithms whenever possible.
- Components should remain modular and independently reusable.

---

# Explainability

Every component of the Monopoly Trade Evaluation System should prioritize explainability.

Whenever practical, conclusions should include the evidence that produced them.

The objective is not merely to generate correct evaluations.

The objective is to generate evaluations that can be understood, reproduced and audited.

---

# Deterministic First Philosophy

Whenever deterministic calculations are available, they should always be preferred over probabilistic reasoning.

Artificial Intelligence should primarily interpret deterministic evidence rather than replace it.

This philosophy improves:

- reproducibility;
- transparency;
- consistency;
- auditability.

---

# Modular Evolution

Every evaluator should evolve independently.

Future evaluators should be added as independent components rather than extending existing ones whenever practical.

This approach minimizes coupling and allows different implementations to coexist.

---

# Research-Driven Development

The project is intended to evolve through research.

New strategies, metrics, algorithms and evaluators should be introduced only after sufficient validation.

Research documents should precede implementation whenever practical.

The repository intentionally separates research from implementation specifications.

---

# Canonical Definitions

Every concept should have a single canonical definition.

For example:

- Railroad Engine
- Complete Board Blocking
- Dynamic Liquidity Reserve

should each be formally defined only once within the project.

Other components should reference those definitions rather than duplicating them.

This minimizes inconsistencies and simplifies future maintenance.

---

# Version Compatibility

Every component of the Monopoly Trade Evaluation System evolves independently.

Every specification document declares its own version.

Implementations should explicitly document the version of every specification they implement.

Components implementing incompatible versions should not assume full interoperability.

Whenever possible, version mismatches should be reported.

---

# Future Extensions

The project has been intentionally designed to support future extensions without major architectural changes.

Possible future additions include:

- probability evaluators;
- simulation engines;
- player behavior models;
- reinforcement learning evaluators;
- tournament-specific rule sets;
- platform-specific evaluators.

The current architecture is intended to support these additions while preserving compatibility with the existing specifications.

---

# Future Component: Player Profile Evaluator

The project architecture intentionally anticipates a third evaluation component:

```text
player_profile_evaluator/
└── README.md
```

Unlike the Static Evaluator and the LLM Evaluator, this component is currently conceptual.

Its purpose is to analyze player behavior across multiple games in order to build long-term player profiles.

These profiles are **not** intended to replace board-state analysis.

Instead, they provide additional contextual information that may help explain recurring decision patterns.

Examples include:

- preferred negotiation style;
- liquidity discipline;
- risk tolerance;
- blocking preference;
- monopoly preference;
- financing behavior;
- railroad preference;
- tendency to overpay;
- tendency to reject trades;
- strategic consistency.

The Player Profile Evaluator is expected to produce a Player Profile that may optionally be supplied as additional input to the Judge.

---

# Complete System Architecture

```text
                         Monopoly Game
                               │
         ┌─────────────────────┴─────────────────────┐
         │                                           │
         ▼                                           ▼
 Static Evaluator                    Player Profile Evaluator
         │                                           │
         ▼                                           ▼
 Static Algorithm Evidence              Historical Player Profile
         │                                           │
         └─────────────────────┬─────────────────────┘
                               ▼
                           LLM Judge
                               │
                               ▼
                 Final Competitive Evaluation
```

The Static Evaluator analyzes the current game and produces deterministic evidence.

The Player Profile Evaluator analyzes historical games and produces long-term behavioral profiles.

The Judge combines both sources of information to perform the final competitive evaluation.

Deterministic evidence should always be considered the primary source of truth.

Historical Player Profiles provide additional context but should never override deterministic evidence generated from the current game.

For example, if the current trade clearly preserves Complete Board Blocking, the Judge should recognize that strategy regardless of whether the player's historical profile usually favors aggressive monopoly development.

---

# Future Work

The Player Profile Evaluator is intentionally left unspecified in the current version of the project.

Only a conceptual README is currently planned.

Future versions may define:

- conceptual specification;
- input specification;
- input schema;
- output specification;
- output schema;
- behavioral metrics;
- statistical models;
- confidence calculations;
- player similarity models;
- long-term strategy detection;
- player archetype classification.

The current repository therefore includes only a conceptual overview describing the intended purpose of this future component.