# Python Reference Implementation

Reference implementation of the deterministic Static Trade Imbalance Evaluator defined by the repository specifications.

The implementation executes only the Static Evaluator. It does not execute the Judge, infer player intent, perform moderation, or consume Strategy Knowledge or Player Profiles.

Normative documentation is authoritative. When implementation and specification disagree, the specification is correct.

**Repository version:** 1.1.0 — see [CHANGELOG](../../CHANGELOG.md).

---

## Normative Documentation

- [Root README](../../README.md)
- [Static Algorithm Specification](../../docs/static_evaluator/static_algorithm_specification.md)
- [Risk Reference](../../docs/static_evaluator/risk_reference.md)
- [Input Specification](../../docs/llm_evaluator/02_input_specification.md)
- [Input Schema](../../docs/llm_evaluator/03_input_schema.md)
- [Static Algorithm Evidence Specification](../../docs/llm_evaluator/04_static_algorithm_specification.md)

---

## Purpose and Boundary

The Python project receives canonical evaluation input and returns complete Static Algorithm Evidence.

**In scope:** deterministic static algorithm execution, evidence generation, input validation, JSON mapping.

**Out of scope:** LLM Judge interpretation, competitive classification reasoning, player profiles, external platform integration.

---

## Canonical Input

The application consumes the input schema defined under `docs/llm_evaluator/`:

| Section | Role |
|---------|------|
| `metadata` | Evaluation identity, game identity, platform, timestamps, schema version |
| `game_configuration` | Rules, defaults, and overrides |
| `board_state_before` | Players, properties, and game state before the trade |
| `trade` | Explicit trade declaration |
| `board_state_after` | Board state after the trade |

The trade is explicit through `trade.transfers`. Each transfer uses `id`, `from_player_id`, `to_player_id`, `asset_type`, `asset_id`, and `amount`.

| `asset_type` | `asset_id` | `amount` |
|---|---|---:|
| `cash` | null | greater than 0 |
| `property` | property ID | 0 |
| other non-quantitative asset | required | 0 |

Property identity comes from `asset_id`; `amount = 0` on property transfers is canonical, not a zero-quantity transfer. Cash and property transfers are validated at the application input boundary before evaluation.

See [Input Specification](../../docs/llm_evaluator/02_input_specification.md) and [Input Schema](../../docs/llm_evaluator/03_input_schema.md) for the full contract.

---

## Canonical Output

The application returns one **Static Algorithm Evidence** object:

| Top-level field | Role |
|-----------------|------|
| `id` | Stable evidence identifier |
| `algorithm_id`, `algorithm_name`, `algorithm_version`, `purpose` | Algorithm identity |
| `intermediate_calculations` | All material deterministic calculations |
| `final_conclusions` | Strategic values, trade ratio, flags, risk labels, warnings, classification |
| `metadata` | Evaluation provenance and specification dependencies |
| `statistics` | Calculation and conclusion counts |

Every material calculation required by the evidence contract is published as an Intermediate Calculation Item with status, side, subject, input traceability, sources, formula or procedure, intermediate values, result, limitations, missing inputs, and dependency links.

See [Static Algorithm Evidence Specification](../../docs/llm_evaluator/04_static_algorithm_specification.md) and [Static Algorithm Specification](../../docs/static_evaluator/static_algorithm_specification.md).

---

## Architecture

The implementation follows **Vertical Slicing**, **Domain-Driven Design**, **CQRS**, and **dependency inversion** with hexagonal dependency direction (application depends on domain abstractions; infrastructure adapts at the boundary). Code is organized around the `StaticEvaluation` capability with a small shared kernel for cross-cutting primitives.

### Layer Responsibilities

#### Application (`StaticEvaluation/Application/`)

- **`EvaluateTradeService`** — application service; validates input and orchestrates evaluation.
- **`EvaluateTradeQuery`** — frozen CQRS query DTO carrying `EvaluationInput`.
- **`EvaluateTradeQueryHandler`** — thin handler delegating to the service.
- Owns the use-case entry point; depends on the domain evaluator abstraction, not infrastructure details.

#### Domain (`StaticEvaluation/Domain/`)

- **`TradeEvaluator`** Protocol — evaluator abstraction (`EvaluationInput` → `StaticAlgorithmEvidence`).
- **`StaticTradeEvaluator`** — concrete 14-step deterministic implementation.
- **Value Objects** — `Money`, `PlayerId`, `PropertyId`, `GroupId` in `Shared/Domain/ValueObject/`.
- **Models** — `EvaluationInput`, `BoardContext`, evidence types, validation.
- **Algorithm steps** — `Steps/Step01BaseAssetValue.py` through `Step10to14Classification.py`.
- **`ClassicRiskReference`** — deterministic Monopoly reference values (rent, repair, development tables); pure domain logic with no external I/O.

Domain code has no filesystem, HTTP, database, or platform dependencies.

#### Infrastructure (`StaticEvaluation/Infrastructure/`)

- **`EvaluationInputMapper`** — maps canonical JSON/dict input to domain models.
- **`EvidenceSerializer`** — serializes domain evidence to canonical JSON/dict output.

Infrastructure handles canonical JSON/dict mapping at the application boundary; deterministic business rules live in Domain. External protocol adapters are not part of this layer today.

### Evaluator Flow

```text
EvaluationInput (canonical JSON)
    ↓
EvaluationInputMapper.fromDict()
    ↓
EvaluateTradeQuery
    ↓
EvaluateTradeService.execute()
    ↓
TradeEvaluator.evaluate()          ← Protocol
    ↓
StaticTradeEvaluator.evaluate()  ← concrete implementation
    ↓
StaticAlgorithmEvidence
    ↓
EvidenceSerializer.toDict()
```

The evaluator is abstracted so alternative implementations could be injected without changing application orchestration.

The domain and application layers do not import HTTP, CLI, messaging, or web-framework modules. The `QueryBus` lives in `Shared/Domain/Bus/` as an in-process dispatch mechanism only; it is not a network protocol.

---

## CQRS

The current trade-evaluation use case is exposed as a **CQRS Query** because evaluation is read-only: it produces Static Algorithm Evidence without changing application state.

**Currently implemented:**

```text
EvaluateTradeQuery
    → QueryBus.ask()
    → EvaluateTradeQueryHandler.handle()
    → EvaluateTradeService.execute()
    → TradeEvaluator.evaluate()          ← Protocol
    → StaticTradeEvaluator.evaluate()    ← concrete implementation
    → StaticAlgorithmEvidence
```

- **`EvaluateTradeQuery`** — frozen query DTO carrying canonical `EvaluationInput`.
- **`QueryBus`** — in-process dispatcher; one handler per query type (`Shared/Domain/Bus/QueryBus.py`).
- **`EvaluateTradeQueryHandler`** — thin adapter delegating to the application service.
- **`EvaluateTradeService`** — use-case orchestration; depends on `TradeEvaluator`, not on concrete infrastructure.

Functional tests exercise this path through `createQueryBus()` from `Monopoly/bootstrap.py`.

**Architecturally supported for future use:** the shared bus pattern can also accommodate **Commands** for state-changing use cases (for example, persisting an evaluation or publishing evidence to a queue). No Command type, Command Handler, or Command Bus exists in the repository today, and trade evaluation does not require one.

CQRS defines the **application use-case boundary**, not a transport protocol. The Query Bus is one way to invoke the use case inside a process; it is not the evaluator itself.

---

## Protocol Independence

The Python Static Evaluator is **not coupled** to CQRS, a CLI, HTTP, gRPC, message brokers, or any other delivery protocol.

CQRS is the **current internal application-dispatch mechanism**. Hexagonal architecture, DDD layering, dependency inversion, and the `TradeEvaluator` abstraction keep the deterministic algorithm independent from how a caller reaches the application.

### What stays independent

The evaluator and domain rules must remain independent from:

- HTTP, REST, or gRPC;
- message brokers, queues, or event streams;
- command-line parsing;
- framework request/response objects;
- platform SDKs;
- database transactions.

### Layer boundaries

| Layer | Responsibility | Must not know |
|-------|----------------|---------------|
| **Domain** (`StaticEvaluation/Domain/`) | Deterministic Monopoly rules, evidence model, `TradeEvaluator` abstraction, `StaticTradeEvaluator` | How a request arrived, HTTP vs Query Bus vs embedded call, process vs service vs job |
| **Application** (`StaticEvaluation/Application/`) | Use case: accept canonical `EvaluationInput`, invoke `TradeEvaluator`, return `StaticAlgorithmEvidence` | Transport-specific parsing, status codes, authentication, routing |
| **Infrastructure** (`StaticEvaluation/Infrastructure/`) | Canonical JSON mapping (`EvaluationInputMapper`, `EvidenceSerializer`) | Business rules (those live in Domain) |
| **Delivery (not implemented)** | Adapt an external protocol to the application boundary | Deterministic calculation logic |

A future delivery adapter — HTTP controller, gRPC handler, message consumer, CLI command, or platform SDK wrapper — belongs **outside** the domain. It maps protocol input to canonical application input, invokes the existing use case, and maps evidence (or validation errors) back to the protocol.

### HTTP / gRPC / messaging vs Query Bus

These are complementary, not mutually exclusive:

```text
HTTP / gRPC / messaging / CLI  =  external delivery mechanism
Query Bus / (future) Command Bus  =  internal use-case dispatch mechanism
```

Converting the application into a network service does **not** require removing CQRS. An HTTP adapter can dispatch the same `EvaluateTradeQuery` through the existing `QueryBus`. HTTP would be the delivery protocol; CQRS would remain the in-process dispatch model.

### Current invocation

```text
Test / caller
    → QueryBus.ask(EvaluateTradeQuery)
    → EvaluateTradeQueryHandler
    → EvaluateTradeService
    → TradeEvaluator / StaticTradeEvaluator
    → StaticAlgorithmEvidence
```

### Possible future HTTP deployment (not implemented)

```text
HTTP request
    → HTTP controller / request adapter        ← future delivery layer
    → EvaluationInputMapper.fromDict()         ← canonical input
    → EvaluateTradeQuery
    → QueryBus.ask()
    → EvaluateTradeQueryHandler
    → EvaluateTradeService
    → StaticTradeEvaluator
    → StaticAlgorithmEvidence
    → EvidenceSerializer.toDict()              ← canonical output
    → HTTP response mapper                     ← future delivery layer
```

No HTTP service, REST endpoint, gRPC interface, message broker, or microservice deployment exists in this repository. Adding one would require a new delivery adapter and composition configuration, **not** a rewrite of the deterministic algorithm.

The same pattern applies conceptually to gRPC services, queue workers, message consumers, CLI tools, and platform-specific SDKs: each adds an adapter around the existing application boundary.

### Direct application-service invocation

A delivery adapter may call `EvaluateTradeService.execute()` directly if future composition deliberately bypasses the bus. That remains valid as long as the adapter still maps to canonical `EvaluationInput` and does not embed transport logic in the domain.

The documented and tested public paths today are:

- **Functional tests** — `EvaluateTradeQuery` through `QueryBus` (`createQueryBus()`).
- **Unit tests** — `EvaluateTradeService` via the injected service fixture.

Future protocol adapters should normally invoke the same application boundary rather than calling `StaticTradeEvaluator` directly, so validation and orchestration stay centralized.

### Embedded library usage

The same implementation can run **inside another Python application** without any network layer:

```text
Host application
    → EvaluateTradeService (or QueryBus + EvaluateTradeQuery)
    → TradeEvaluator / StaticTradeEvaluator
    → StaticAlgorithmEvidence
```

Embedding does not bypass the canonical input/output contract or application-layer validation.

### Serialization responsibility

Domain evidence objects define **meaning**. `EvidenceSerializer.toDict()` produces **JSON-compatible** output suitable for external protocols, logs, or message payloads.

Delivery adapters own protocol-specific concerns: HTTP status codes and headers, gRPC status details, queue envelope formats, authentication, rate limiting, and mapping network errors. The evaluator does not own HTTP error handling.

### Validation responsibility

A future transport adapter should:

1. parse the protocol request;
2. map it to canonical evaluation input (for example via `EvaluationInputMapper`);
3. invoke `EvaluateTradeQuery` (or, if composed that way, `EvaluateTradeService.execute()`);
4. map application validation failures and degraded evidence statuses into protocol-specific responses.

Monopoly business rules and input validation remain canonical in Domain/Application. The HTTP (or other) layer must not duplicate or redefine them.

### Why future adapters are straightforward

Future delivery mechanisms are easier to add because:

- Domain code has no transport dependencies;
- `EvaluateTradeService` accepts canonical `EvaluationInput` and returns `StaticAlgorithmEvidence`;
- Output is JSON-compatible through `EvidenceSerializer`;
- `StaticTradeEvaluator` is accessed through the `TradeEvaluator` Protocol;
- `bootstrap.py` centralizes concrete composition;
- CQRS separates invocation from domain behavior;
- Tests already validate application behavior independently of transport.

This is not automatic: each new protocol needs its own adapter and wiring. The deterministic Static Algorithm itself should not need to change.

---

## Dependency Injection

Composition occurs in `Monopoly/bootstrap.py`:

```python
def createEvaluateTradeHandler() -> EvaluateTradeQueryHandler:
    evaluator = StaticTradeEvaluator()
    service = EvaluateTradeService(evaluator=evaluator)
    return EvaluateTradeQueryHandler(evaluateTradeService=service)

def createQueryBus() -> QueryBus:
    bus = QueryBus()
    bus.subscribe(EvaluateTradeQuery, createEvaluateTradeHandler().handle)
    return bus
```

- Handlers and services receive dependencies via constructor injection.
- Unit tests use the `evaluate_trade_service` fixture from `conftest.py`; they do not wire the graph manually.
- Functional tests use the configured `QueryBus`; they do not instantiate handlers or services directly.
- Future delivery adapters (HTTP, gRPC, messaging, CLI) would extend this composition root with additional handler registrations or service factories; the domain evaluator wiring would remain unchanged.

---

## Project Structure

```text
src/python/
├── README.md
├── pyproject.toml
└── src/Monopoly/
    ├── bootstrap.py                          # Composition root
    ├── Shared/Domain/
    │   ├── Bus/QueryBus.py
    │   └── ValueObject/                      # Money, PlayerId, PropertyId, GroupId
    └── StaticEvaluation/
        ├── Application/Query/EvaluateTrade/
        │   ├── EvaluateTradeQuery.py
        │   ├── EvaluateTradeQueryHandler.py
        │   └── EvaluateTradeService.py
        ├── Domain/Model/
        │   ├── TradeEvaluator.py             # Protocol
        │   ├── EvaluationInput.py
        │   ├── Algorithm/
        │   │   ├── StaticTradeEvaluator.py
        │   │   └── Steps/                    # Step01 … Step10to14
        │   ├── RiskReference/ClassicRiskReference.py
        │   └── Evidence/                     # EvidenceCollector, calculation items
        └── Infrastructure/Json/
            ├── EvaluationInputMapper.py
            └── EvidenceSerializer.py

test/python/
├── fixtures/
│   ├── fixtureLoader.py                      # Canonical JSON loader
│   ├── scenarioInputs.py                     # Named scenario loader functions
│   ├── boardBuilders.py                      # Authoring utilities (not scenario source of truth)
│   └── inputs/                               # Committed JSON scenarios
├── unit/
│   ├── static_evaluator/evaluate_trade_service/
│   │   ├── conftest.py                       # evaluate_trade_service fixture
│   │   ├── test_scenario_expectations.py     # One behavioral test per scenario
│   │   ├── test_scenario_registry.py         # Registry integrity
│   │   ├── test_trade_ratio.py               # Trade ratio family
│   │   ├── test_automatic_flags.py           # Automatic flag family
│   │   ├── test_final_classification.py      # Classification family
│   │   ├── assertions/                       # Shared evidence and scenario helpers
│   │   └── output_fields/                    # Field-level output coverage (135 fields)
│   └── test_utilities/
│       ├── evidence_contract.py              # Contract validation utilities
│       ├── dependency_graph.py               # Dependency graph utilities
│       └── fixture_loader/                   # Loader infrastructure tests
└── functional/
    └── static_evaluator/evaluate_trade_query/
        ├── conftest.py                       # query_bus fixture
        └── test_scenario_expectations.py     # CQRS scenario tests
```

Unit test directories mirror the application service under test. Multiple focused suites live under `evaluate_trade_service/`.

---

## JSON Scenario Fixtures

Committed scenarios follow a fixed architecture:

```text
complete JSON file (source of truth)
    → named loader function in scenarioInputs.py
    → loadScenarioInput() in fixtureLoader.py
    → unit test (EvaluateTradeService) or functional test (QueryBus)
```

Rules:

- JSON is the authoritative scenario data; loader functions document and load fixtures, they do not procedurally construct committed scenarios.
- Each named scenario has one loader function with a docstring describing expected behavior.
- Classic scenarios (`ruleset_name = classic_monopoly`) contain all 28 purchasable properties with explicit unowned entries.
- Valid fixtures are not silently normalized at load time.
- Invalid fixtures contain one intentional defect each.
- Expected behavior lives in the **scenario registry** (`assertions/scenario_registry.py`), not inside the input JSON.
- The registry maps each scenario to its primary expected classification, flags, risk labels, warnings, or validation/degraded result.

`boardBuilders.py` exists for fixture authoring only; it is not the source of truth for committed scenarios.

---

## Testing

### Unit Tests — Application Services Only

> Unit tests test application services only.

`EvaluateTradeService` is the unit under test. Domain behavior is verified indirectly through complete evidence output. Tests use the injected service fixture; they do not test domain classes, private methods, or calculation builders in isolation.

**Scenario expectations:** one JSON scenario → one loader function → one primary expected behavior (classification, flag, risk label, warning, or validation error). Implemented in `test_scenario_expectations.py`; expectations are declared in the scenario registry and checked independently against specifications.

**Calculation-family tests:** focused boundary verification in dedicated modules:

| Module | Focus |
|--------|-------|
| `test_trade_ratio.py` | Trade Ratio thresholds and cap behavior |
| `test_automatic_flags.py` | Automatic flag rules |
| `test_final_classification.py` | Final classification boundaries |

**Output-field coverage:** 136 canonical evidence fields mapped to focused unit tests via `output_fields/` (25 category modules). Registry: `output_field_coverage.py`; matrix: `OUTPUT_COVERAGE_MATRIX.md`; guard: `test_output_field_coverage_guard.py`. Each field is classified as **SEMANTIC** (independently derived expected value) or **STRUCTURAL** (type/presence invariant). Critical high-trust fields must be semantic. Covers envelope fields, calculation-item fields, every registered calculation type, all four statuses (`COMPLETE`, `PARTIAL`, `UNAVAILABLE`, `ERROR`), sides, subjects, input references, sources, intermediate values, results, dependencies, final conclusions, metadata, and statistics.

**Evidence contract tests:** `test_evidence_contract.py` enforces deterministic serialized output, JSON serialization, dependency-graph validity, and canonical Trade Ratio keys through the application service.

**Risk label boundaries:** `test_risk_label_boundaries.py` verifies all five Risk Labels (`SURVIVAL_RISK_CRITICAL` through `SURVIVAL_RISK_VERY_LOW`) and adjacent tier distinctions through committed scenarios.

**Registry and infrastructure tests:** `test_scenario_registry.py` (registry integrity, no orphan fixtures); `test_utilities/fixture_loader/` (loader validation and determinism).

**Support utilities:** `test_utilities/dependency_graph.py` provides reusable dependency validators; field-level and family tests verify the same semantics through service output.

Existing scenarios are reused across multiple field tests. New scenarios are added only when no existing input can meaningfully exercise a required field or status.

### Functional Tests — CQRS Through the Real Bus

> Functional tests exercise the public CQRS Query through the real Query Bus.

`test/python/functional/static_evaluator/evaluate_trade_query/test_scenario_expectations.py` dispatches `EvaluateTradeQuery` via `createQueryBus()`. Each scenario verifies one meaningful public result (classification, flags, or degraded/error behavior). Functional tests do not duplicate field-level assertions.

### No Integration Tests

There are currently no integration tests because there are no real external integrations or delivery adapters (no database, HTTP server, message broker, or production filesystem boundary). The in-process `QueryBus` and JSON fixture loader are not external integrations.

When an HTTP service, database, message broker, or other real boundary is added, integration tests (or functional delivery tests, depending on classification) can verify request/response mapping, routing, status codes, protocol serialization, and middleware for that concrete adapter. None of those tests exist today.

### Future delivery-layer tests (not implemented)

If a protocol adapter were added, its tests would sit **above** the current suites:

| Layer | What it verifies | Status |
|-------|------------------|--------|
| Unit | `EvaluateTradeService` and evidence contract | **Exists** |
| Functional (CQRS) | `EvaluateTradeQuery` through `QueryBus` | **Exists** |
| Delivery / integration | HTTP/gRPC/queue request mapping, routing, status codes, auth | **Not implemented** |

Delivery tests would not replace application-service or CQRS functional tests; they would assert that the adapter correctly bridges an external protocol to the existing use case.

### Behavioral Coverage

The suite exercises, among other areas:

- all Strategic Value components and their deltas;
- Trade Ratio boundaries and cap behavior;
- development capability (buildable and dangerous predicates);
- monopoly creation and loss;
- house control and denial;
- railroad counts and board-context multipliers;
- blocking topology and strategic opportunity;
- risk coverage labels, warnings, and tier breakdown (all five Risk Labels);
- automatic flags and initiator adjustment (all eight automatic flags);
- final classifications (all four classifications);
- `PARTIAL` calculation status when meaningful partial results exist;
- invalid transfer and board inputs;
- custom boards;
- evidence envelope, metadata, statistics, and final conclusions;
- calculation dependency links and final-conclusion traceability;
- deterministic output, JSON serialization, and dependency-graph validation enforced in CI.

Behavioral coverage matters more than test count.

---

## Usage

```python
from Monopoly.bootstrap import createQueryBus
from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeQuery import (
    EvaluateTradeQuery,
)
from Monopoly.StaticEvaluation.Infrastructure.Json.EvaluationInputMapper import (
    EvaluationInputMapper,
)
from Monopoly.StaticEvaluation.Infrastructure.Json.EvidenceSerializer import (
    EvidenceSerializer,
)

bus = createQueryBus()
evaluation_input = EvaluationInputMapper.fromDict(serialized_input)
evidence = bus.ask(EvaluateTradeQuery(evaluationInput=evaluation_input))
result = EvidenceSerializer.toDict(evidence)
```

---

## Development Commands

Run from the repository root after installing dependencies:

```bash
pip install -e "src/python[dev]"

# All tests
pytest test/python/

# Unit tests only
pytest test/python/unit/

# Functional tests only
pytest test/python/functional/

# Coverage (line and branch)
pytest test/python/ --cov=Monopoly --cov-branch --cov-report=term-missing

# Lint
ruff check src/python test/python

# Format
ruff format src/python test/python

# Format check (no modifications)
ruff format --check src/python test/python

# Static type checking
mypy src/python/src
```

Python version: **3.12** reference; **3.10+** supported.

---

## Versioning

| Concept | Value |
|---------|-------|
| Repository version | `1.1.0` |
| Python package version (`pyproject.toml`) | `1.1.0` |
| Static Algorithm specification version | `1.0` |
| Risk Reference specification version | `1.0` |
| Evidence `algorithm_version` in output | `1.0` |

Repository version, package version, and specification versions are distinct. See [CHANGELOG](../../CHANGELOG.md).
