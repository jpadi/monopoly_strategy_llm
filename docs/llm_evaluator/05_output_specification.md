# Monopoly Trade Evaluation Output Specification

Version: 1.0

## Purpose

This document defines the conceptual output model produced by the Monopoly Trade Evaluation System.

Its purpose is to describe what the evaluator must return after reviewing a Monopoly trade.

This document defines the meaning of each output section.

It does not define the JSON structure.

The JSON structure is defined separately in the Output Schema document (`06_output_schema.md`).

The Output Specification and Output Schema must use the same concepts, the same section names, and the same terminology.

The evaluator's output must clearly separate:

- competitive classification;
- competitive evaluation;
- supporting evidence;
- static analysis result;
- decision pattern analysis;
- confidence assessment;
- final summary.

The complete output is composed of the following logical sections:

1. Competitive Classification

2. Competitive Evaluation

3. Supporting Evidence

4. Static Analysis Result

5. Decision Pattern Analysis

6. Confidence Assessment

7. Final Summary

Every section is described independently below.

## Competitive Classification

The Competitive Classification represents the evaluator's primary conclusion.

It is the objective assessment of the competitive impact of the trade.

Every trade evaluation must produce exactly one Competitive Classification.

The Competitive Classification is determined exclusively during the Competitive Evaluation phase.

Once determined, it must never be modified by Decision Pattern Analysis or any later stage of the evaluation.

---

### Purpose

The purpose of the Competitive Classification is to summarize the evaluator's overall competitive judgement.

It answers a single question:

> **How does this trade affect the competitive position of every player involved and the overall competitive balance of the game?**

The Competitive Classification is the primary result of the evaluation.

All remaining output sections exist to explain or support this conclusion.

---

### Classification Values

Every evaluation must produce exactly one of the following classification values.

- **Competitively Sound** — every participating player receives a reasonable competitive benefit relative to what they give, or the trade maintains the overall competitive balance of the game.
- **Slightly Unbalanced** — the trade produces a moderate competitive imbalance, but a plausible competitive justification exists for every participant.
- **Significantly Unbalanced** — the trade produces a clear competitive imbalance, and the disadvantaged player receives only a weak competitive justification.
- **Severely Unbalanced** — the trade produces an extreme, one-sided competitive impact, and the disadvantaged player receives no meaningful competitive compensation.

These values classify the competitive impact of the trade.

They never describe player intent, fairness, ethics, or sportsmanship.

The corresponding serialized values are defined by the Output Schema.

---

### Optional Score And Classification Confidence

Implementations may additionally expose an optional numerical score alongside the discrete classification value.

The score is an implementation-specific refinement.

It must always remain consistent with the discrete classification value.

Implementations may also attach an optional confidence value specifically to the Competitive Classification.

When omitted, the overall Confidence Assessment is authoritative.

---

### Evidence Used

The Competitive Classification should be determined using objective evidence.

Examples include:

- Board State;
- Trade Information;
- Game Configuration;
- Static Algorithm Evidence.

Player Profiles and Decision Pattern Profiles should never determine the Competitive Classification.

They may help explain the trade after the classification has been completed.

---

### Objectivity

The Competitive Classification should evaluate only the competitive consequences of the trade.

It should never evaluate:

- player intent;
- fairness;
- ethics;
- sportsmanship;
- moderation concerns.

The evaluator should remain completely objective.

---

### Stability

The Competitive Classification should remain stable.

Additional explanations or contextual information should never change the classification once it has been determined.

Only new objective evidence should be capable of changing the Competitive Classification.

---

### Interpretability

The Competitive Classification should be understandable without reading the complete report.

It should provide a concise summary of the evaluator's overall competitive judgement.

The detailed reasoning supporting the classification belongs to the remaining output sections.

## Competitive Evaluation

The Competitive Evaluation contains the evaluator's complete competitive analysis of the trade.

Its purpose is to explain why the Competitive Classification was assigned.

Every important conclusion should be supported by objective evidence.

The Competitive Evaluation should remain independent from Decision Pattern Analysis.

---

### Purpose

The purpose of the Competitive Evaluation is to describe the competitive consequences of the trade.

It should explain how the trade changes the game.

Rather than simply stating whether the trade is good or bad, the evaluator should explain the reasoning that produced the Competitive Classification.

---

### Scope

The Competitive Evaluation should analyze both the immediate and long-term competitive effects of the trade.

Examples include:

- changes in player strength;
- liquidity changes;
- monopoly creation;
- monopoly destruction;
- blocking opportunities;
- development opportunities;
- house supply control;
- hotel supply control;
- bankruptcy risk;
- negotiation leverage;
- changes in competitive balance.

The evaluator is not limited to these examples.

Any competitive consequence supported by the evidence may be included.

---

### Objectivity

The Competitive Evaluation should be based only on objective evidence.

Possible evidence includes:

- Board State;
- Trade Information;
- Game Configuration;
- Static Algorithm Evidence.

Player Profiles and Decision Pattern Profiles should not influence the competitive evaluation.

They belong to later sections of the report.

---

### Multiple Players

The Competitive Evaluation should consider the impact on every active player.

The evaluation should never focus exclusively on the players participating in the trade.

A trade between two players may significantly affect every remaining player.

The evaluator should explain any important indirect competitive consequences.

---

### Immediate And Long-Term Effects

Some trades produce immediate advantages.

Others sacrifice short-term value to improve long-term winning chances.

The Competitive Evaluation should explain both perspectives whenever relevant.

---

### Transparency

Every significant conclusion should be traceable to supporting evidence.

Whenever possible, explain:

- what changed;
- why it matters competitively;
- which evidence supports the conclusion.

The reasoning should be clear enough that another evaluator could understand how the Competitive Classification was reached.

---

### Independence

The Competitive Evaluation should never be modified after Decision Pattern Analysis.

Decision Pattern Analysis exists to explain possible reasoning behind the trade.

It must never change the competitive evaluation itself.

## Supporting Evidence

The Supporting Evidence section identifies the evidence that materially influenced the Competitive Classification.

Its purpose is to make the evaluation transparent and auditable.

Rather than repeating every available input, this section should identify only the evidence that significantly affected the evaluator's conclusions.

---

### Purpose

The purpose of Supporting Evidence is to explain which facts were most influential during the evaluation.

Every important competitive conclusion should be traceable to one or more supporting pieces of evidence.

This allows reviewers to understand not only the evaluator's conclusions, but also the factual basis used to reach them.

---

### Evidence Sources

Supporting Evidence may reference information from any objective input source.

Examples include:

- Board State;
- Trade Information;
- Game Configuration;
- Static Algorithm Evidence.

Supporting Evidence should never reference Decision Pattern Profiles as objective evidence.

Decision Pattern Profiles belong exclusively to the explanation phase.

---

### Evidence Selection

Not every available fact needs to appear in Supporting Evidence.

Only evidence that materially contributed to the Competitive Classification should be included.

Minor facts that did not affect the evaluation should normally be omitted.

---

### Traceability

Every important conclusion contained in the Competitive Evaluation should be traceable to one or more supporting evidence items.

Whenever possible, Supporting Evidence should reference the exact object or calculation that supports the conclusion.

Examples include:

- Player identifiers;
- Property identifiers;
- Trade transfers;
- Static Algorithm calculations;
- Game Configuration rules.

This improves transparency and simplifies future reviews.

---

### Objectivity

Supporting Evidence should contain factual information only.

It should never contain:

- strategic interpretations;
- recommendations;
- speculation;
- player intent;
- Decision Pattern matches.

Interpretation belongs to the Competitive Evaluation.

Supporting Evidence exists only to document the facts used during the evaluation.

---

### Completeness

Supporting Evidence should include every major fact that significantly influenced the evaluator's decision.

The evaluator should avoid overwhelming the report with unnecessary details.

The objective is to provide enough evidence for another evaluator to independently understand and verify the Competitive Classification.

## Static Analysis Result

The Static Analysis Result reports how Static Algorithm Evidence was handled during the evaluation.

It is the execution report of the Static Analysis Resolution defined by the Judge Specification (`01_judge.md`).

Every evaluation must produce exactly one Static Analysis Result, even when no static analysis was performed.

This section reports facts about the evaluation process.

It never contains strategic interpretation, and it never modifies the Competitive Classification.

---

### Purpose

The purpose of the Static Analysis Result is to make the origin of every deterministic calculation transparent and auditable.

A reviewer must be able to determine:

- which static-analysis mode the input requested;
- which runtime execution mode was actually resolved;
- whether the deterministic evidence was supplied by software or generated by the Judge;
- which algorithm and dependency versions were involved;
- whether the Competitive Evaluation actually used static evidence;
- which limitations and errors affected the static analysis.

---

### Requested Mode And Execution Mode

The Static Analysis Result reports both:

- the **requested mode** — the Static Analysis Control mode after default resolution (`auto`, `require_provided_evidence`, `allow_llm_fallback`, or `disable_static_analysis`);
- the **runtime execution mode** — exactly one of `STATIC_EVIDENCE_PROVIDED`, `LLM_STATIC_FALLBACK`, or `NO_STATIC_ANALYSIS`, as defined by the Judge Specification.

When the runtime execution mode is `NO_STATIC_ANALYSIS`, the reason must be reported.

---

### Evidence Provenance

When Static Algorithm Evidence was consumed, the Static Analysis Result identifies its provenance:

- `SUPPLIED_STATIC_SOFTWARE` — the evidence was supplied in the input;
- `LLM_FALLBACK_GENERATED` — the evidence was generated by the Judge under LLM Static Fallback.

Valid supplied evidence always has precedence over fallback-generated evidence and is never silently replaced.

---

### Algorithm And Dependency Identity

When static analysis was performed, the Static Analysis Result identifies:

- the algorithm identifier and version;
- the identifier and version of every mandatory dependency used.

These values are matched against the Specification Identity metadata of the corresponding documents and against the Static Analysis Control declarations.

---

### Execution Status

The Static Analysis Result reports exactly one execution status:

- `COMPLETE` — usable evidence was consumed, or fallback executed every mandatory calculation successfully;
- `PARTIAL` — partially usable supplied evidence was consumed, or fallback completed with some calculations partial or unavailable;
- `UNAVAILABLE` — static analysis was wanted but no usable evidence existed and fallback could not execute;
- `ERROR` — fallback execution failed because the supplied input was inconsistent, invalid, or could not be processed;
- `NOT_REQUESTED` — the mode was `disable_static_analysis`.

The evaluation may continue after `PARTIAL`, `UNAVAILABLE`, or `ERROR` when the remaining evidence is sufficient.

Material limitations must be disclosed, and the Confidence Assessment must reflect them.

---

### Fallback Reporting

The Static Analysis Result reports whether fallback was attempted and, when attempted, why.

When fallback executed, the complete generated Static Algorithm Evidence must be returned inside the Static Analysis Result.

The generated evidence uses the same canonical structure defined by the Static Algorithm Evidence Specification (`04_static_algorithm_specification.md`).

Returning only a prose summary of the generated calculations is forbidden.

---

### Objectivity

The Static Analysis Result contains factual execution information only.

It never contains:

- strategic interpretations;
- recommendations;
- speculation;
- player intent;
- Decision Pattern matches.

## Decision Pattern Analysis

The Decision Pattern Analysis section attempts to explain why a player may have reasonably accepted or proposed the evaluated trade.

This analysis is performed only after the Competitive Classification and Competitive Evaluation have been completed.

Decision Pattern Analysis provides possible explanations.

It never changes the Competitive Classification.

---

### Purpose

The purpose of Decision Pattern Analysis is to compare the observed trade against the documented Decision Pattern Profiles provided as input.

The evaluator should determine whether the trade resembles one or more documented decision patterns.

The analysis helps explain the player's possible reasoning.

It does not determine whether the player made a correct or incorrect decision.

---

### Pattern Matching

The evaluator should compare the observed trade against every available Decision Pattern Profile.

Possible outcomes include:

- no matching patterns;
- one matching pattern;
- multiple matching patterns.

Only meaningful matches should be reported.

Patterns with insignificant similarity should normally be omitted.

Implementations may optionally report the patterns that were evaluated but did not meaningfully match the trade.

Unmatched patterns are intended for auditing, debugging, or research purposes.

---

### Similarity Assessment

A Decision Pattern match indicates that the observed trade resembles a documented pattern.

A match does not prove that the player intentionally followed that pattern.

Likewise, the absence of a match does not imply irrational play or malicious intent.

Decision Pattern Analysis identifies similarities.

It does not establish facts about player motivation.

---

### Multiple Matches

A trade may reasonably resemble multiple Decision Pattern Profiles.

Different aspects of the trade may correspond to different documented patterns.

When multiple meaningful matches exist, the evaluator should explain how each pattern contributes to understanding the trade.

---

### Independence

Decision Pattern Analysis is independent from the Competitive Evaluation.

The Competitive Classification must already be finalized before Decision Pattern Analysis begins.

Decision Pattern Analysis must never modify:

- the Competitive Classification;
- the Competitive Evaluation;
- the Supporting Evidence.

Its purpose is limited to providing additional context.

---

### Transparency

For every reported Decision Pattern match, the evaluator should explain:

- which documented pattern matched;
- which observed decisions support the match;
- which evidence supports the similarity;
- any important differences between the observed trade and the documented pattern.

The evaluator should avoid overstating similarities.

Partial matches should be clearly identified as partial.

---

### Objectivity

Decision Pattern Analysis should remain objective.

The evaluator should never conclude that a player intentionally followed a documented Decision Pattern.

Likewise, the evaluator should never conclude that a player acted maliciously simply because a trade resembles a documented non-competitive pattern.

Decision Pattern Analysis provides possible explanations.

It never establishes player intent.

## Confidence Assessment

The Confidence Assessment represents the evaluator's estimate of the reliability of the complete evaluation.

It reflects the quality, completeness, consistency, and reliability of the available evidence.

Confidence does not measure the quality of the trade.

Confidence does not measure player skill.

Confidence does not measure player intent.

Confidence measures only the evaluator's confidence in the correctness of its own conclusions.

---

### Purpose

The purpose of the Confidence Assessment is to communicate how reliable the overall evaluation is.

It allows reviewers to distinguish between:

- strong conclusions supported by complete evidence;
- reasonable conclusions supported by incomplete evidence;
- uncertain conclusions requiring additional information.

Confidence should always refer to the evaluation itself, never to the players.

---

### Sources of Confidence

Confidence should be influenced by factors such as:

- completeness of the Board State;
- completeness of the Trade Information;
- clarity of the Game Configuration;
- quality of Static Algorithm Evidence;
- consistency between multiple evidence sources;
- internal consistency of the available data;
- amount of missing information;
- amount of conflicting information.

The evaluator may consider additional factors whenever they materially affect evaluation reliability.

---

### High Confidence

High Confidence should be assigned when:

- the available evidence is complete;
- the evidence is internally consistent;
- the competitive consequences are well supported;
- alternative interpretations are unlikely to change the Competitive Classification.

---

### Medium Confidence

Medium Confidence should be assigned when:

- minor information is missing;
- some evidence is incomplete;
- multiple reasonable interpretations remain possible;
- additional evidence could reasonably strengthen or weaken the evaluation.

The Competitive Classification should still be considered reliable.

---

### Low Confidence

Low Confidence should be assigned when:

- important evidence is unavailable;
- critical parts of the Board State are missing;
- important contradictions exist between evidence sources;
- the Competitive Classification depends on assumptions that cannot be verified.

The evaluator should clearly explain which missing or conflicting evidence reduced confidence.

---

### Independence

Confidence should be evaluated independently from the Competitive Classification.

A trade may receive:

- a strong Competitive Classification with Low Confidence;
- a weak Competitive Classification with High Confidence.

The evaluator should never increase confidence simply because a trade appears obvious.

Likewise, unusual trades should not automatically reduce confidence.

Confidence must always reflect the quality of the available evidence.

---

### Transparency

Whenever Confidence is not High, the evaluator should explain the primary reasons.

Examples include:

- incomplete Board State;
- missing Game Configuration;
- unavailable Static Algorithm Evidence;
- conflicting deterministic calculations;
- incomplete Trade Information;
- insufficient contextual information.

Reviewers should be able to understand exactly why confidence was reduced.

## Final Summary

The Final Summary provides a concise overview of the complete evaluation.

Its purpose is to communicate the evaluator's overall conclusions in a format that can be quickly understood by reviewers.

The Final Summary should summarize the complete evaluation.

It should never introduce new conclusions that were not already established in previous sections.

---

### Purpose

The purpose of the Final Summary is to provide a clear and concise overview of the evaluation.

A reader should be able to understand the overall result without reading the complete report.

The Final Summary is intended for human readers.

---

### Contents

The Final Summary should briefly summarize:

- the Competitive Classification;
- the most important competitive reasons supporting the classification;
- the most relevant Supporting Evidence;
- any meaningful Decision Pattern matches;
- the overall Confidence Assessment.

Only the most important findings should be included.

---

### Consistency

The Final Summary should remain fully consistent with every previous section.

It should never:

- modify the Competitive Classification;
- introduce new evidence;
- introduce new interpretations;
- contradict the Competitive Evaluation;
- contradict the Supporting Evidence;
- contradict the Decision Pattern Analysis.

The Final Summary summarizes the evaluation.

It does not extend it.

---

### Clarity

The Final Summary should be concise, objective, and easy to understand.

Avoid unnecessary technical details.

The objective is to communicate the evaluator's overall conclusion as clearly as possible.

---

### Independence

The Final Summary is the final section of the report.

It should be understandable on its own.

A reviewer reading only the Final Summary should still understand:

- the overall Competitive Classification;
- why that classification was assigned;
- the evaluator's overall Confidence Assessment.