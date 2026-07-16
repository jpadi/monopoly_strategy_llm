# Changelog

All notable changes to the Monopoly Trade Evaluation System repository are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

---

---

## [1.2.0]

### Added

- Added the independent `LlmEvaluation` vertical slice under `src/python/src/Monopoly/LlmEvaluation/` mirroring StaticEvaluation CQRS/hexagonal patterns.
- Added platform-agnostic `LlmClient` port: `LlmRequest` carries `instructionFilePaths`, `attachmentFilePaths`, and `taskPrompt`; each client loads paths and delivers file content (inline headers or native upload).
- Added `JudgeArtifactRecorder` domain port with `DefaultJudgeArtifactRecorder` infrastructure adapter for execution artifact recording.
- Added `CursorLlmClient` adapter (opt-in via `cursor-sdk` extra) and stub adapters for Claude, Gemini, Grok, and OpenAI.
- Added deterministic pre-LLM pipeline: mode resolution, evidence validation, fallback eligibility, bundle building, and one repair attempt.
- Added structured validation diagnostics (`JudgeValidationErrorRecord`) with machine-readable paths and codes for fallback evidence reference defects.
- Added repair-flow artifacts: `initial_validation_errors.json`, `repair_request_summary.json`, `repair_response.txt`, `repair_parse_error.json`, and `repair_validation_errors.json`.
- Added `LlmPromptAssembler` and `SpecificationManifestBuilder` for client-side prompt assembly and delivery manifests.
- Added LLM Judge unit, functional Query Bus, module isolation, and opt-in Cursor integration tests (nine runtime-mode scenarios).
- Added shared Judge runtime scenario registry at `test/python/fixtures/llm_evaluation/judge_scenario_registry.py`.
- Added `test/python/fixtures/llm_evaluation/` fixtures and `.env.example` for Cursor integration.
- Added dedicated Cursor platform documentation under `docs/llm_platform/cursor/` (SDK contract, transport envelope schema, response normalization).
- Added Cursor response transport envelope (`inline_json`, `file_reference`) with workspace-bounded file retrieval.
- Added Cursor transport parser, normalizer, diagnostics, and architecture isolation guards.
- Added Cursor transport unit tests covering envelope validation, file retrieval, security rules, legacy prose compatibility, workspace lifecycle, and repair transport contract.
- Documented bounded `direct_judge_output` compatibility behavior for provider responses that omit the transport envelope but contain all seven canonical Judge sections.

### Fixed

- Corrected the LLM static fallback output contract to use canonical Static Algorithm Evidence field names, enums, metadata (`specification_dependencies`), statistics (`calculation_count`), subject structure, and downstream `dependent_calculation_ids` references.
- Added `GeneratedStaticAlgorithmEvidenceValidator` so malformed or legacy fallback evidence is rejected before `execution_status` can be reported as `COMPLETE`.
- Aligned `SuppliedEvidenceValidator` with the canonical evidence schema validator and material-calculation checks from `01_judge.md`.
- Guaranteed delivery of every `docs/llm_evaluator/` specification on every Judge execution, including `02_input_specification.md` in non-fallback modes; added complete `docs/static_evaluator/` delivery when execution resolves to `LLM_STATIC_FALLBACK`.
- Synchronized the request delivery manifest with instruction and attachment paths (including platform instruction files).
- Fixed live fallback repair reliability: repair requests include the complete invalid output, structured validation errors, strict JSON-only instructions, and the full specification bundle; repair failures raise `JudgeRepairFailureError` with initial and repair diagnostics preserved.
- Extended initial parse failures and validation failures to a single structured repair attempt; repair traces now always record `initialValidationErrors` (including parse failures).
- Added automatic repository `.env` loading for bootstrap and pytest so Cursor integration tests detect `CURSOR_API_KEY` from the repository root `.env` file.
- Fixed Cursor large-response recovery: structured transport envelope and authorized workspace file reads replace hardcoded sidecar path detection; SDK artifact download when the referenced path is listed by `list_artifacts()`, otherwise authorized local workspace retrieval.
- Fixed duplicated content in `.env.example`.
- Fixed artifact cleanup failures on non-empty nested integration artifact trees.
- Fixed Cursor file-reference validation: reject cross-platform absolute paths, null bytes, broken symlinks, path traversal, symlink escapes, empty files, malformed JSON, and multiple JSON values.
- Reject unknown Cursor transport-envelope and `file_reference` fields.
- Extended integration diagnostics with transport normalization fields (`response_type`, retrieval method, bytes recovered, legacy recovery flag).
- Restored the lost `#### metadata` heading in `04_static_algorithm_specification.md` intermediate-calculation documentation.
- Updated `00_initial_prompt.md` repair trigger wording to cover schema validation and non-JSON responses.
- Enforced rejection of undocumented top-level Judge output keys per `06_output_schema.md`.
- Removed architecture leak: `EvaluateTradeWithJudgeService` no longer imports Infrastructure artifact writers directly.
- Extended module isolation guard to block all `Infrastructure` imports from Domain and Application layers.
- Wired integration delivery-evidence assertions into Cursor integration helpers.
- Corrected README coverage descriptions: Static Evaluator **136** evidence fields vs Judge **40** schema section fields across seven top-level sections.

### Changed

- Extended `bootstrap.py` with `createEvaluateTradeWithJudgeHandler()`, public `repoRoot()`, and Judge query registration on shared `QueryBus`.
- Bumped package version to 1.2.0.
- Specification bundles discover all `docs/llm_evaluator/` markdown files for every mode; add all `docs/static_evaluator/` markdown files when `bundleRequired` is true for LLM Static Fallback.
- Documented delivery manifest authority and Python preflight resolution in `00_initial_prompt.md`.
- Strengthened `06_output_schema.md` Mandatory Response Format (JSON-only, required sections, no file redirects, no omitted large evidence).
- Trimmed `JudgePromptBuilder` task guidance to spec-referenced execution checkpoints only.
- Reorganized `LlmEvaluation` tests to mirror production architecture under `test/python/**/LlmEvaluation/`.
- Extended Judge request artifacts with delivered path inventories and content hashes (no credentials).
- Consolidated duplicate Judge scenario registries into one shared module.
- Commented out unwired `.env.example` keys (`CURSOR_ASSESSOR_MODEL`, `LLM_REQUEST_TIMEOUT_SECONDS`); documented deferred `SemanticResponseAssessor`.
- Cursor provider calls now append a Cursor-specific transport instruction and preserve the authorized execution workspace until transport normalization completes; each initial and repair call uses a distinct workspace.
- Cursor repair responses follow the same transport contract as initial responses.
- README and Python README now document Cursor transport boundaries, workspace lifecycle, and accurate SDK retrieval precedence under `docs/llm_platform/cursor/`.
- Clarified `CURSOR_JUDGE_MODEL` as integration-test configuration; production model selection uses `llm_execution.model`.

### Removed

- Removed unused local-workspace delivery helpers (`SpecificationBundleDeliverer`, `ZipSpecificationBundler`, `ValidateJudgeResponseService`).
- Removed obsolete flat Cursor documentation (`docs/llm_platform/cursor_client_notes.md`) in favor of `docs/llm_platform/cursor/`.
- Removed hardcoded project-root and `/tmp` sidecar recovery (`CursorJudgeOutputSidecar`).

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
