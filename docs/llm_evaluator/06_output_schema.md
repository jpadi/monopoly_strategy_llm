# Monopoly Trade Evaluation Output Schema

Version: 1.0

## Purpose

This document defines the JSON serialization of the conceptual output model described in:

**05_output_specification.md**

The Output Specification is the authoritative source for the meaning of every concept described by this schema.

This document introduces no additional semantics.

Its purpose is solely to define the JSON representation of the evaluator's output.

---

## Mandatory Response Format

Every Judge response MUST satisfy all of the following rules:

- The response MUST be exactly **one JSON object**.
- The response MUST NOT contain prose, Markdown, code fences, summaries, or file references outside that JSON object.
- The response MUST NOT redirect the host to read output from a filesystem path or external resource.
- The response MUST include **every required top-level section** defined by this schema.
- Every required field defined by this schema MUST be present with a valid value, or explicit `null` only where this schema permits null.
- Undocumented additional top-level keys are forbidden.
- Invalid enum values invalidate the response.
- Missing required fields invalidate the response.
- Omitting required evidence because it is large invalidates the response.

When LLM Static Fallback executes, the response MUST include complete `generated_static_algorithm_evidence` that satisfies `04_static_algorithm_specification.md`. A prose summary MUST NOT replace canonical evidence.

---

## Top-Level Structure

The output MUST be a single JSON object with the following top-level sections.

```json
{
  "competitive_classification": {},
  "competitive_evaluation": {},
  "supporting_evidence": {},
  "static_analysis_result": {},
  "decision_pattern_analysis": {},
  "confidence_assessment": {},
  "final_summary": {}
}
```

---

## Required Sections

The following sections are **always required**.

```text
competitive_classification

competitive_evaluation

supporting_evidence

static_analysis_result

decision_pattern_analysis

confidence_assessment

final_summary
```

Every evaluation MUST produce all sections.

Individual sections MAY contain empty collections when no relevant information exists.

The overall output structure MUST remain consistent for every evaluation.

## Competitive Classification

This section serializes the conceptual Competitive Classification defined in:

**05_output_specification.md**

No additional semantics are introduced by this schema.

---

### JSON Structure

```json
{
  "classification": "",
  "score": null,
  "confidence": null,
  "metadata": {}
}
```

---

### Field Definitions

#### classification

Serialized representation of the Competitive Classification.

The valid values are defined by the Output Specification:

- `competitively_sound`
- `slightly_unbalanced`
- `significantly_unbalanced`
- `severely_unbalanced`

---

#### score

Optional numerical representation of the Competitive Classification.

This field is optional because some implementations may use discrete classifications while others may additionally expose a numerical score.

The scale and direction of the score are implementation-defined and must be documented inside this section's `metadata`.

Scores produced by different implementations are not comparable.

The score must always remain consistent with the ordering of the discrete classification values.

---

#### confidence

Optional confidence associated specifically with the Competitive Classification.

This value is independent from the overall Confidence Assessment section.

If omitted, the evaluator's overall Confidence Assessment should be considered authoritative.

---

#### metadata

Optional implementation-specific information.

Unknown metadata fields should be ignored by consumers.

## Competitive Evaluation

This section serializes the conceptual Competitive Evaluation defined in:

**05_output_specification.md**

No additional semantics are introduced by this schema.

---

### JSON Structure

```json
{
  "summary": "",
  "immediate_effects": [],
  "long_term_effects": [],
  "affected_players": [],
  "key_findings": [],
  "metadata": {}
}
```

---

### Field Definitions

#### summary

Concise competitive evaluation summarizing the overall reasoning.

---

#### immediate_effects

Collection of immediate competitive consequences identified during the evaluation.

Examples include:

- monopoly completed;
- monopoly broken;
- liquidity increased;
- liquidity decreased;
- immediate development opportunity;
- increased bankruptcy risk.

---

#### long_term_effects

Collection of long-term competitive consequences.

Examples include:

- stronger endgame position;
- improved negotiation leverage;
- increased board control;
- future development potential;
- long-term blocking advantage.

---

#### affected_players

List of players whose competitive position was materially affected by the trade.

Each entry should reference a valid Player identifier.

---

#### key_findings

Collection of the evaluator's most important competitive findings.

Each finding should represent a single significant competitive observation.

---

#### metadata

Optional implementation-specific information.

Unknown metadata fields should be ignored by consumers.

## Supporting Evidence

This section serializes the conceptual Supporting Evidence defined in:

**05_output_specification.md**

No additional semantics are introduced by this schema.

---

### JSON Structure

```json
{
  "board_state_evidence": [],
  "trade_information_evidence": [],
  "game_configuration_evidence": [],
  "static_algorithm_evidence": [],
  "metadata": {}
}
```

---

### Field Definitions

#### board_state_evidence

Collection of Board State elements that materially contributed to the evaluation.

Each item should reference one or more objects from the Board State.

---

#### trade_information_evidence

Collection of Trade Information elements that materially contributed to the evaluation.

Each item should reference one or more Trade objects or Transfers.

---

#### game_configuration_evidence

Collection of Game Configuration elements that materially influenced the evaluation.

Only relevant configuration values should be included.

---

#### static_algorithm_evidence

Collection of Static Algorithm Evidence items that materially contributed to the evaluation.

Each item should reference the corresponding Static Algorithm Evidence object.

---

#### metadata

Optional implementation-specific information.

Unknown metadata fields should be ignored by consumers.

## Static Analysis Result

This section serializes the conceptual Static Analysis Result defined in:

**05_output_specification.md**

No additional semantics are introduced by this schema.

---

### JSON Structure

```json
{
  "requested_mode": "",
  "execution_mode": "",
  "evidence_source": null,
  "algorithm_id": null,
  "algorithm_version": null,
  "dependency_versions": {},
  "execution_status": "",
  "fallback_attempted": false,
  "fallback_reason": null,
  "competitive_evaluation_used_static_evidence": false,
  "generated_static_algorithm_evidence": [],
  "limitations": [],
  "errors": [],
  "metadata": {}
}
```

---

### Field Definitions

#### requested_mode

The Static Analysis Control mode after default resolution.

Exactly one of:

- `auto`
- `require_provided_evidence`
- `allow_llm_fallback`
- `disable_static_analysis`

When the input omitted `static_analysis_control`, this field is `auto`.

---

#### execution_mode

The resolved runtime execution mode, as defined by the Judge Specification.

Exactly one of:

- `STATIC_EVIDENCE_PROVIDED`
- `LLM_STATIC_FALLBACK`
- `NO_STATIC_ANALYSIS`

When the value is `NO_STATIC_ANALYSIS`, the reason must be reported in `limitations`.

---

#### evidence_source

Provenance of the Static Algorithm Evidence consumed by the evaluation.

Exactly one of:

- `SUPPLIED_STATIC_SOFTWARE`
- `LLM_FALLBACK_GENERATED`
- `null` when `execution_mode` is `NO_STATIC_ANALYSIS`.

---

#### algorithm_id

Stable identifier of the Static Algorithm whose evidence was consumed or generated (for the canonical algorithm: `monopoly_static_algorithm`).

`null` when `execution_mode` is `NO_STATIC_ANALYSIS`.

---

#### algorithm_version

Version of the Static Algorithm whose evidence was consumed or generated.

`null` when `execution_mode` is `NO_STATIC_ANALYSIS`.

---

#### dependency_versions

Object mapping each mandatory dependency identifier to the version used.

Example:

```json
{
  "monopoly_risk_reference": "1.0"
}
```

Empty when `execution_mode` is `NO_STATIC_ANALYSIS`.

---

#### execution_status

Exactly one of:

- `COMPLETE`
- `PARTIAL`
- `UNAVAILABLE`
- `ERROR`
- `NOT_REQUESTED`

The value semantics are defined by the Output Specification.

---

#### fallback_attempted

Boolean indicating whether LLM Static Fallback execution was attempted.

---

#### fallback_reason

Reason fallback was attempted.

Use `NO_USABLE_SUPPLIED_EVIDENCE` when fallback was attempted.

`null` when fallback was not attempted.

---

#### competitive_evaluation_used_static_evidence

Boolean indicating whether the Competitive Evaluation actually used Static Algorithm Evidence as supporting evidence.

---

#### generated_static_algorithm_evidence

Collection of the complete Static Algorithm Evidence objects generated by the Judge under LLM Static Fallback.

Every element uses the canonical Static Algorithm Evidence structure defined by the Static Algorithm Evidence Specification (`04_static_algorithm_specification.md`) and serialized by the Input Schema (`03_input_schema.md`), including `algorithm_id`, `algorithm_name`, `algorithm_version`, the canonical Intermediate Calculation Items, and `final_conclusions`.

Empty when `execution_mode` is not `LLM_STATIC_FALLBACK`.

Returning a prose summary instead of the complete generated evidence is forbidden.

Implementations should validate generated evidence against the canonical Static Algorithm Evidence contract before accepting `execution_status = COMPLETE`.

---

#### limitations

Collection of material limitations affecting the static analysis.

Examples include:

- no usable supplied evidence with fallback not authorized;
- incompatible algorithm or dependency version;
- partially usable supplied evidence;
- calculations recorded as `PARTIAL` or `UNAVAILABLE` during fallback.

This field may be empty.

---

#### errors

Collection of errors encountered during evidence validation or fallback execution.

Mandatory when `execution_status` is `ERROR`.

This field may be empty.

---

#### metadata

Optional implementation-specific information.

Unknown metadata fields should be ignored by consumers.

## Decision Pattern Analysis

This section serializes the conceptual Decision Pattern Analysis defined in:

**05_output_specification.md**

No additional semantics are introduced by this schema.

---

### JSON Structure

```json
{
  "matched_patterns": [],
  "unmatched_patterns": [],
  "summary": "",
  "metadata": {}
}
```

---

### Field Definitions

#### matched_patterns

Collection of Decision Pattern Profiles that meaningfully matched the evaluated trade.

Each item uses the following minimal structure:

```json
{
  "pattern_id": "",
  "summary": ""
}
```

`pattern_id` references the identifier of a Decision Pattern Profile provided in the input.

`summary` describes the observed similarities and any contradicting evidence.

Implementations may add optional fields.

Unknown fields should be ignored by consumers.

---

#### unmatched_patterns

Optional collection of Decision Pattern Profiles that were evaluated but did not meaningfully match the trade.

Each item uses the same structure as `matched_patterns`.

This field is intended primarily for debugging, auditing, or research purposes.

Implementations may omit this field if reporting unmatched patterns provides little practical value.

---

#### summary

Concise summary describing the overall outcome of the Decision Pattern Analysis.

This summary should remain consistent with the complete analysis.

---

#### metadata

Optional implementation-specific information.

Unknown metadata fields should be ignored by consumers.

## Confidence Assessment

This section serializes the conceptual Confidence Assessment defined in:

**05_output_specification.md**

No additional semantics are introduced by this schema.

---

### JSON Structure

```json
{
  "overall_confidence": "",
  "confidence_factors": [],
  "limitations": [],
  "metadata": {}
}
```

---

### Field Definitions

#### overall_confidence

Serialized representation of the overall Confidence Assessment.

The valid values are defined by the Output Specification:

- `high`
- `medium`
- `low`

---

#### confidence_factors

Collection of the primary factors that contributed to the overall confidence.

Examples include:

- complete Board State;
- complete Trade Information;
- consistent Static Algorithm Evidence;
- missing information;
- conflicting evidence.

Only the most significant factors should be included.

---

#### limitations

Collection of limitations that reduced the evaluator's confidence.

Examples include:

- incomplete Board State;
- missing Game Configuration;
- unavailable Static Algorithm Evidence;
- conflicting deterministic calculations;
- incomplete Trade Information;
- insufficient contextual information.

This field may be empty when no significant limitations exist.

---

#### metadata

Optional implementation-specific information.

Unknown metadata fields should be ignored by consumers.

## Final Summary

This section serializes the conceptual Final Summary defined in:

**05_output_specification.md**

No additional semantics are introduced by this schema.

---

### JSON Structure

```json
{
  "summary": "",
  "highlights": [],
  "metadata": {}
}
```

---

### Field Definitions

#### summary

Concise human-readable summary of the complete evaluation.

The summary should remain fully consistent with all previous output sections.

It should not introduce new conclusions or interpretations.

---

#### highlights

Collection of the most important findings included in the Final Summary.

Examples include:

- Competitive Classification;
- primary competitive reasons;
- most relevant Supporting Evidence;
- meaningful Decision Pattern matches;
- overall Confidence Assessment.

The highlights should summarize the evaluation rather than replace the complete report.

---

#### metadata

Optional implementation-specific information.

Unknown metadata fields should be ignored by consumers.

---

### Design Principles

The Final Summary should remain consistent with every previous output section.

It should provide a concise overview of the evaluation.

It should never introduce:

- new evidence;
- new conclusions;
- new interpretations;
- modifications to the Competitive Classification.

The Final Summary represents the final serialized section of the evaluator's output.