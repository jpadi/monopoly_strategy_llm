# Monopoly Trade Evaluation System

Research specifications and a Python reference implementation for evaluating Monopoly trades.

The project separates **deterministic analysis** from **strategic interpretation**. Deterministic software, Large Language Models, or hybrid systems can consume the same normative contracts to produce transparent, explainable, and auditable trade evaluations.

Specifications are implementation-independent. The repository also contains a Python reference implementation of the deterministic Static Evaluator under `src/python/`. Whenever implementation and specification disagree, the specification is authoritative.

---

## Current Release

**Current version: 1.1.0**

Version 1.1.0 reorganizes the repository and adds the Python reference implementation of the deterministic Static Evaluator together with its unit and functional test suites.

See [CHANGELOG.md](CHANGELOG.md) for the complete release history.

---

## Why This Project Exists

Monopoly trade evaluation requires two distinct capabilities:

1. **Deterministic measurement** — objective competitive consequences (monopoly changes, liquidity, development potential, risk exposure, deterministic flags).
2. **Strategic interpretation** — reasoning about competitive impact using Monopoly strategy knowledge.

Combining both in one opaque step produces results that are hard to audit or reproduce. This repository defines them as separate, composable components with explicit input and output contracts.

---

## Architecture Overview

```text
                         Monopoly Game
                               │
         ┌─────────────────────┴─────────────────────┐
         │                                           │
         ▼                                           ▼
 Static Evaluator                    Player Profile Evaluator
 (deterministic)                      (conceptual / future)
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

| Component | Status | Responsibility |
|-----------|--------|----------------|
| **Static Evaluator** | Specified; Python reference in `src/python/` | Deterministic calculations and Static Algorithm Evidence |
| **LLM Judge** | Specified only | Strategic interpretation, classification, and final evaluation |
| **Player Profile Evaluator** | Conceptual | Long-term behavioral profiles across games |

The Static Evaluator never determines player intent. The Judge never replaces deterministic evidence when valid evidence is supplied.

---

## Repository Structure

```text
.
├── README.md
├── CHANGELOG.md
├── docs/
│   ├── static_evaluator/          # Algorithm specification and Risk Reference
│   ├── llm_evaluator/             # Judge, I/O specs, evidence contract, strategy KB
│   └── player_profile_evaluator/  # Conceptual future component
├── src/
│   └── python/                    # Python reference implementation
└── test/
    └── python/                    # Unit, functional, and JSON fixture tests
```

| Path | Responsibility |
|------|----------------|
| `docs/` | Normative specifications: algorithms, evidence contracts, input/output models, strategic knowledge |
| `src/python/` | Python reference implementation of the Static Evaluator only |
| `test/python/` | Tests and canonical JSON fixtures for the Python implementation |

Classic Monopoly fixtures use the complete classic board (28 purchasable properties). Transfer semantics, fixture rules, and test organization are documented in [src/python/README.md](src/python/README.md).

---

## Static Evaluator

The Static Evaluator performs deterministic analysis: monopoly creation or loss, liquidity, mortgage capacity, development simulation, railroad and blocking evaluation, house control, rent and repair exposure, immediate risk, deterministic labels, warnings, and scores.

Normative sources:

- Algorithm: [docs/static_evaluator/static_algorithm_specification.md](docs/static_evaluator/static_algorithm_specification.md)
- Risk Reference: [docs/static_evaluator/risk_reference.md](docs/static_evaluator/risk_reference.md)
- Evidence contract: [docs/llm_evaluator/04_static_algorithm_specification.md](docs/llm_evaluator/04_static_algorithm_specification.md)

The evaluator may internally classify a trade as `REVIEW_RECOMMENDED`. That is a deterministic internal flag, distinct from the Judge's reasoned review recommendations.

---

## LLM Judge

The Judge consumes game state, trade information, optional Static Analysis Control instructions, and optional Static Algorithm Evidence. It produces the Competitive Classification, Competitive Evaluation, Supporting Evidence, Decision Pattern Analysis, Confidence Assessment, and Final Summary.

The Judge does not determine player intent, fairness, ethics, or sportsmanship. See [docs/llm_evaluator/01_judge.md](docs/llm_evaluator/01_judge.md).

Strategy concepts come from the [Strategy Knowledge Base](docs/llm_evaluator/07_strategy_knowledge_base.md), delivered to the Judge as Decision Pattern Profiles.

---

## Operating Modes

Evaluation mode is controlled by the `static_analysis_control` input section.

### Normal Hybrid Mode (preferred)

```text
Game State → Static Evaluator → Static Algorithm Evidence → LLM Judge → Final Evaluation
```

Valid supplied evidence always takes precedence. The Judge consumes it and does not recalculate the complete Static Algorithm.

### LLM Static Fallback Mode

When no usable evidence is supplied and the input explicitly authorizes fallback, the Judge executes the Static Algorithm itself and returns generated evidence in the output. Fallback requires explicit authorization, compatible specification identities, and follows the same evidence contract as deterministic software.

### Evaluation Without Static Analysis

When static analysis is disabled or unavailable without authorized fallback, the Judge evaluates using remaining evidence and reports the limitation.

Supported `static_analysis_control.mode` values: `auto`, `require_provided_evidence`, `allow_llm_fallback`, `disable_static_analysis`. When absent, the default is `{ "mode": "auto", "fallback_allowed": false }`.

Full rules are in [docs/llm_evaluator/01_judge.md](docs/llm_evaluator/01_judge.md).

---

## Python Reference Implementation

The Python implementation under [src/python/](src/python/) executes the deterministic Static Trade Imbalance Evaluator. It:

- receives canonical `metadata`, `game_configuration`, `board_state_before`, `trade`, and `board_state_after`;
- executes the static algorithm;
- returns complete Static Algorithm Evidence;
- does **not** execute Judge interpretation;
- is **protocol-independent** — suitable for embedding or wrapping with future HTTP, gRPC, messaging, or CLI adapters without changing the deterministic algorithm.

Architecture, CQRS flow, protocol independence, fixture model, testing strategy, and development commands are documented in **[src/python/README.md](src/python/README.md)**.

Quick start:

```bash
pip install -e "src/python[dev]"
pytest test/python/
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| [Input Specification](docs/llm_evaluator/02_input_specification.md) | Input semantics and business rules |
| [Input Schema](docs/llm_evaluator/03_input_schema.md) | Input structure and validation |
| [Static Algorithm Evidence Spec](docs/llm_evaluator/04_static_algorithm_specification.md) | Evidence output contract |
| [Output Specification](docs/llm_evaluator/05_output_specification.md) | Judge output semantics |
| [Output Schema](docs/llm_evaluator/06_output_schema.md) | Judge output structure |
| [Strategy Knowledge Base](docs/llm_evaluator/07_strategy_knowledge_base.md) | Recognized Monopoly strategies |
| [Player Profile Evaluator](docs/player_profile_evaluator/README.md) | Conceptual future component |

Conceptual specifications and schemas must remain synchronized. Neither should evolve independently.

---

## Testing Summary

The Python test suite validates the reference implementation against the specifications:

- **Application-service unit tests** through injected `EvaluateTradeService`.
- **Functional CQRS tests** through the configured `QueryBus` and `EvaluateTradeQuery`.
- **JSON-backed scenario inputs** with one primary behavioral expectation per scenario (via the scenario registry).
- **Focused output-field verification** with an enforced coverage registry (135 canonical fields).
- **Evidence structure checks** through scenario tests, calculation-family tests, and field-level assertions (envelope, dependencies, statuses, final conclusions).
- **No integration tests** — the implementation has no external integrations.

Details: [src/python/README.md#testing](src/python/README.md#testing).

---

## Design Principles

- **Deterministic first** — prefer reproducible calculations over probabilistic reasoning; AI interprets evidence rather than replacing it.
- **Explainability** — important conclusions should be traceable to evidence.
- **Modularity** — Static Evaluator, Judge, and future evaluators evolve independently.
- **Single canonical definitions** — each concept is defined once and referenced elsewhere.
- **Implementation independence** — specifications do not assume language, architecture, or platform.

---

## Reading Order

1. This README — project scope and architecture.
2. [Static Algorithm Specification](docs/static_evaluator/static_algorithm_specification.md) — deterministic algorithm behavior.
3. [Static Algorithm Evidence Specification](docs/llm_evaluator/04_static_algorithm_specification.md) — evidence output contract.
4. [Judge Specification](docs/llm_evaluator/01_judge.md) — strategic interpretation and operating modes.
5. [src/python/README.md](src/python/README.md) — reference implementation guide.

---

## Versioning

Repository version: **1.1.0**

Each specification document declares its own version. Implementations should document which specification versions they implement. See [CHANGELOG.md](CHANGELOG.md).
