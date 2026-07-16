# Changelog

All notable changes to the Monopoly Trade Evaluation System repository are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

---

---

## [1.2.1]

### Fixed

- Corrected the `1.2.0` CHANGELOG so it accurately describes the Git delta between the `1.1.0` and `1.2.0` tags.
- Reworded Static Algorithm Evidence entries from the LLM Judge and fallback-consumer perspective.
- Removed or consolidated entries that described previously released `1.1.0` Static Evaluator functionality, internal development iterations, or pre-release implementation experiments.
- Corrected Keep a Changelog category placement and duplicate release-note entries.

### Changed

- Synchronized README release-history descriptions and current-version references with the corrected `1.2.0` release narrative.
- Bumped repository and package version metadata to 1.2.1.

---

## [1.2.0]

Version 1.2.0 added the independent Python LLM Judge implementation (`LlmEvaluation`), the platform infrastructure required to execute and validate it, Cursor provider integration, and LLM-focused tests and documentation. The deterministic Static Evaluator released in 1.1.0 was not reimplemented; shared test utilities were refactored only to support both modules.

### Added

- Independent `LlmEvaluation` vertical slice under `src/python/src/Monopoly/LlmEvaluation/` mirroring StaticEvaluation CQRS and hexagonal patterns.
- Platform-agnostic `LlmClient` port with `LlmRequest` instruction paths, attachment paths, task prompts, and provider-neutral `LlmResponse` handling.
- `EvaluateTradeWithJudgeService` orchestrating all documented Static Analysis modes: supplied evidence, LLM Static Fallback, competitive-only evaluation, and disable-static-analysis paths.
- Deterministic pre-LLM pipeline: mode resolution, fallback eligibility, supplied-evidence classification, specification bundle assembly, and runtime plan materialization.
- Strict Judge response parsing, schema validation, runtime-mode consistency validation, structured validation diagnostics, and one controlled repair attempt.
- Judge-side validation of supplied and fallback-generated Static Algorithm Evidence, including reference-graph integrity checks before fallback evidence may be reported as `COMPLETE`.
- Specification-file delivery: `LlmPromptAssembler`, delivery manifests, filesystem specification repository, and complete `docs/llm_evaluator/` attachment on every execution plus `docs/static_evaluator/` when LLM Static Fallback is resolved.
- `CursorLlmClient` adapter (opt-in via `cursor-sdk` extra), Cursor transport envelope normalization (`inline_json`, `file_reference`), workspace-bounded file retrieval, transport diagnostics, and stub adapters for Claude, Gemini, Grok, and OpenAI.
- Judge execution artifacts via `JudgeArtifactRecorder` / `DefaultJudgeArtifactRecorder`, including initial and repair validation traces and sanitized provider transport diagnostics.
- Shared infrastructure for LLM operations: `ArtifactStore`, repository `.env` loading (`EnvironmentLoader`), and `.env.example` for Cursor integration configuration.
- Bootstrap registration of `EvaluateTradeWithJudgeQuery` on the shared `QueryBus` with `createEvaluateTradeWithJudgeHandler()` and public `repoRoot()`.
- LLM platform documentation under `docs/llm_platform/` including the file attachment standard and Cursor SDK, transport, and file-reference contracts.
- LLM Judge entry prompt at `docs/llm_evaluator/00_initial_prompt.md`.
- LLM Judge unit tests, functional Query Bus tests, architecture isolation guards, shared runtime scenario registry, fixtures under `test/python/fixtures/llm_evaluation/`, and opt-in Cursor integration tests across nine runtime-mode scenarios.

### Changed

- Extended `bootstrap.py` from Static Evaluator wiring to shared composition root for both evaluation modules.
- Updated Judge specifications for API delivery workflow, operating modes, mandatory JSON output, repair triggers, and fallback evidence reference integrity (`01_judge.md`, `04_static_algorithm_specification.md`, `05_output_specification.md`, `06_output_schema.md`).
- Extended root and Python READMEs to document the LLM Judge module, provider boundaries, test layout, and Cursor integration.
- Refactored shared Static Evaluator test utilities and assertions to support both modules without changing deterministic evaluator runtime behavior.
- Bumped repository and package version to 1.2.0.

---

## [1.1.0]

### Added

- Added the Python reference implementation of the deterministic Static Evaluator under `src/python/`.
- Added the Python application-service unit test suite and CQRS functional test suite under `test/python/`.
- Added canonical JSON-backed test scenarios, fixture loading, and named scenario input functions.

### Changed

- Reorganized all specification documentation under `docs/`.
- Added the `src/python/` and `test/python/` project structure.
- Updated the root README as the architectural entry point and added this Python implementation guide.
- Clarified that CQRS is the current internal application-dispatch mechanism and that the evaluator remains independent of external delivery protocols.
- Standardized committed test scenarios as complete JSON inputs loaded through named scenario functions.
- Reorganized tests to mirror the application service (`evaluate_trade_service/`) and CQRS entry point (`evaluate_trade_query/`).

#### Input model

- Clarified Transfer semantics: cash value from `amount`, property identity from `asset_id`; property transfers use `amount = 0`.
- Synchronized input specification and schema with conditional Transfer validation rules.
- Required complete classic-board representation in committed classic fixtures (28 purchasable properties, explicit unowned properties).

#### Strategic Value and development

- Clarified Mortgage Capacity to include all eligible unmortgaged, undeveloped property categories (streets, railroads, utilities).
- Clarified candidate-group exclusion in Available Construction Budget and Dangerous Monopoly Availability.
- Separated authoritative `input_values` from derived `intermediate_values` in development-related evidence.

#### Trade Ratio and classification

- Introduced `MAX_TRADE_RATIO = 5.0` cap; raw ratio preserved in evidence, published ratio capped and rounded.
- Documented `highest_strategic_value`, `lowest_strategic_value`, `division_denominator`, `raw_trade_ratio`, `maximum_trade_ratio`, and `published_trade_ratio` in the evidence contract.
- Clarified Step 1 transfer consumption (never multiply property value by `amount`).

#### Blocking and Railroad rules

- Clarified that property owners are excluded from blocked-player counts.
- Corrected multi-player blocking semantics for two-player games.
- Replaced blocked-board railroad terminology with `low_development` / `high_development` context based on developed monopoly count; evidence exposes the board-context predicate.

#### Risk Coverage

- Clarified Available Risk Resources beyond player cash (mortgage capacity, building liquidation).
- Clarified exposure methodology, tier breakdown, signed risk scoring, labels, and warnings in evidence.
- Largest Threat evidence includes landing and repair exposure operands.

#### Evidence contract

- Required before/after/delta calculations with reproducible operands.
- Clarified source labels and input-reference alignment with actual value sources.
- Completed dependency traceability via `dependent_calculation_ids` throughout the evidence graph.
- Clarified final-conclusion references, Trade Initiator adjustment reporting, and empty-field semantics.
- All material complete calculations require formula or procedure; enum values serialize to canonical JSON strings at the public boundary.

### Fixed

- Corrected Trade Ratio handling when one participant's Strategic Value is zero; documented maximum published ratio.
- Corrected Mortgage Capacity and scoped construction-budget calculations.
- Corrected candidate-group development simulations so a group cannot finance its own development through its own mortgage capacity.
- Corrected blocking calculations so property owners are not counted as blocked opponents.
- Corrected multi-player blocking bonuses in two-player games.
- Corrected Railroad context selection and evidence traceability.
- Corrected Static Algorithm Evidence completeness, dependency references, and final-conclusion linkage.
- Added the documented `PARTIAL` evidence behavior for calculations with usable but incomplete results.
- Corrected and verified the `STRATEGIC_RAILROAD_GIVEAWAY` rule with a valid Mostly Blocked Board scenario.
- Corrected scenario names and expectations that did not match their documented behavior.
- Corrected the Trade Ratio assertion helper to use canonical evidence keys (`raw_trade_ratio`, `published_trade_ratio`).
- Fixed Risk Coverage tier ratio comparisons that prevented `SURVIVAL_RISK_MODERATE` and `SURVIVAL_RISK_LOW` from being reachable.

### Testing

- Added specification-driven application-service tests covering major algorithm components, scenario behavior, and the complete evidence output contract (including field-level coverage with an enforced coverage registry).
- Added CQRS functional tests for committed scenario inputs through the Query Bus.
- Expanded specification-driven coverage for all Risk Labels, deterministic output, JSON serialization, dependency traceability, and high-value semantic evidence fields.

### Compatibility

- Specification changes are additive where possible; Trade Ratio cap narrows the published ratio range without changing classification vocabulary.
- `EvaluationInputMapper` accepts both `asset_type` (canonical) and `transfer_type` (legacy).
- Specification identities and algorithm/risk-reference versions remain unchanged.

---

## [1.0.0]

### Added

- Added the initial specification-only architecture for the Monopoly Trade Evaluation System.
- Added the deterministic Static Evaluator specification and Risk Reference under `static_evaluator/`.
- Added the LLM Judge specification under `llm_evaluator/`.
- Added canonical input, Static Algorithm Evidence, and Judge output specifications and schemas.
- Added the Strategy Knowledge Base.
- Added the conceptual Player Profile Evaluator documentation.
