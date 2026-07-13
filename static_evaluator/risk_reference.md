# Monopoly Risk Reference

Version: 1.0

---

# Specification Identity

This document exposes the following stable identity metadata:

```text
specification_type = RISK_REFERENCE
specification_id = monopoly_risk_reference
specification_version = 1.0
```

`specification_version` always equals the document version declared above.

This document is a mandatory dependency of the Static Algorithm Specification (`static_algorithm_specification.md`, `monopoly_static_algorithm`).

This metadata is used for fallback discovery and version validation: `static_analysis_control.required_dependencies` entries in the input schema are matched against `specification_id` and `specification_version`.

A version is compatible when it equals the required version.

---

# Purpose

This document provides conservative financial reference tables for evaluating the risk of voluntarily opening an opponent monopoly.

Its purpose is to estimate the maximum short-term financial exposure created by a trade.

The document is intended as a quick reference.

It does not predict the probability of landings.

It estimates the financial consequences if those landings occur.

This document defines two separable things:

1. the **normative calculation methodology** — the normalization rules, worst-case landing rules, repair addition rules, and deterministic procedures;
2. **canonical Classic Monopoly default values** — the numeric tables, which are the precomputed results of that methodology for the standard Monopoly board.

Whenever authoritative rent values are supplied by the Board State (`rent_table`) or by Game Configuration, those values take precedence over the classic defaults; exposure is then recomputed by applying the same methodology to the supplied rents. The numeric tables remain the canonical defaults and reference implementations for the standard board.

---

# Conservative Philosophy

Every table in this document follows a conservative approach.

Whenever multiple interpretations are possible, the highest financial risk is assumed.

This intentionally overestimates risk rather than underestimating it.

Conservatism is bounded by facts: the worst case is chosen among **currently collectible** outcomes of the supplied board state. It never invents future actions.

The objective is to avoid opening monopolies that cannot be financially survived.

---

# Scope

The tables estimate only immediate financial exposure.

They do not consider:

- future bankruptcies;
- inherited monopolies;
- future negotiations;
- probability of movement;
- expected value calculations;
- player behavior.

Only direct financial exposure is evaluated.

---

# Risk Matrix Rules

The following rules apply to every table in this document.

## Development Classification

A monopoly is always classified according to the highest developed property.

Example:

3-2-2 → Level 3

The actual distribution of houses is ignored.

Only the highest developed property determines the development level.

This general rule is normative for any street-group size: determine the highest development level among the properties in the group, then classify the complete group at that level for risk-reference purposes.

The two-property and three-property tables below are enumerated examples of the general rule, not limitations. Exposure for custom groups is derived by applying the same methodology to the supplied rent values.

---

## Mortgaged Properties

A mortgaged property contributes no rent while it remains mortgaged.

This is a fact of the supplied board state, not a penalty.

Exposure calculations never grant opponents hypothetical unmortgaging, construction, sales, negotiations, or any other future actions. Only what is currently true and collectible in the supplied board state is evaluated.

Railroad and utility ownership-count rent tiers may include mortgaged group members when the configured rules define them that way (classic default: they do). The landed-on railroad or utility must itself be unmortgaged to collect rent.

Group rent bonuses require only the landed-on property to be unmortgaged, unless the Game Configuration states otherwise.

---

Three-property monopolies

| Actual Development | Evaluated As |
|--------------------|--------------|
| 0-0-0 | 0-0-0 |
| 1-0-0 | 1-1-1 |
| 1-1-0 | 1-1-1 |
| 1-1-1 | 1-1-1 |
| 2-0-0 | 2-2-2 |
| 2-1-0 | 2-2-2 |
| 2-1-1 | 2-2-2 |
| 2-2-0 | 2-2-2 |
| 2-2-1 | 2-2-2 |
| 2-2-2 | 2-2-2 |
| 3-0-0 | 3-3-3 |
| 3-1-0 | 3-3-3 |
| 3-1-1 | 3-3-3 |
| 3-2-0 | 3-3-3 |
| 3-2-1 | 3-3-3 |
| 3-2-2 | 3-3-3 |
| 3-3-0 | 3-3-3 |
| 3-3-1 | 3-3-3 |
| 3-3-2 | 3-3-3 |
| 3-3-3 | 3-3-3 |
| Any group containing a 4 | 4-4-4 |

---

Two-property monopolies

| Actual Development | Evaluated As |
|--------------------|--------------|
| 0-0 | 0-0 |
| 1-0 | 1-1 |
| 1-1 | 1-1 |
| 2-0 | 2-2 |
| 2-1 | 2-2 |
| 2-2 | 2-2 |
| 3-0 | 3-3 |
| 3-1 | 3-3 |
| 3-2 | 3-3 |
| 3-3 | 3-3 |
| Any group containing a 4 | 4-4 |

---

## Landing Cost

Every landing uses the highest possible rent within the opened monopoly.

The evaluator always assumes that every landing occurs on the most expensive property of the monopoly.

This represents the worst-case financial exposure.

---

## Repair Cards

Repair costs are evaluated independently.

Total Exposure =

Repair Cost

+

Landing Cost

---

## Number of Landings

Each risk matrix evaluates:

- 1 landing
- 2 landings
- 3 landings
- 4 landings
- 5 landings
- 6 landings

No probability assumptions are made.

Only cumulative financial exposure is calculated.

The Static Algorithm Specification scores only the single-landing scenario (the Largest Threat of Step 9); it surfaces the two- through six-landing values as additional exposure evidence, never summing them into the score.

---

# Repair Risk Reference

Repair costs are evaluated independently from monopoly exposure.

When estimating total financial risk, repair costs should always be added to the expected landing exposure.

---

## Repair Cards

The standard Monopoly game contains two repair cards.

### Chance

$25 per House

$100 per Hotel

### Community Chest

$40 per House

$115 per Hotel

The tables below provide the financial exposure for each repair card individually and for both cards combined.

---

## Repair Exposure Tables

### Houses

| Houses | Chance | Community Chest | Both Cards |
|--------:|-------:|----------------:|-----------:|
| 0 | $0 | $0 | $0 |
| 4 | $100 | $160 | $260 |
| 8 | $200 | $320 | $520 |
| 12 | $300 | $480 | $780 |
| 16 | $400 | $640 | $1,040 |
| 20 | $500 | $800 | $1,300 |
| 24 | $600 | $960 | $1,560 |
| 28 | $700 | $1,120 | $1,820 |
| 29 | $725 | $1,160 | $1,885 |
| 30 | $750 | $1,200 | $1,950 |
| 31 | $775 | $1,240 | $2,015 |
| 32 | $800 | $1,280 | $2,080 |

---

### Hotels

| Hotels | Chance | Community Chest | Both Cards |
|--------:|-------:|----------------:|-----------:|
| 0 | $0 | $0 | $0 |
| 1 | $100 | $115 | $215 |
| 2 | $200 | $230 | $430 |
| 3 | $300 | $345 | $645 |
| 4 | $400 | $460 | $860 |
| 5 | $500 | $575 | $1,075 |
| 6 | $600 | $690 | $1,290 |
| 7 | $700 | $805 | $1,505 |
| 8 | $800 | $920 | $1,720 |
| 9 | $900 | $1,035 | $1,935 |
| 10 | $1,000 | $1,150 | $2,150 |
| 11 | $1,100 | $1,265 | $2,365 |
| 12 | $1,200 | $1,380 | $2,580 |

---

## Total Exposure

**Total Exposure = Repair Cost + Landing Exposure**

---

## Interpretation

Repair exposure should always be evaluated together with monopoly landing exposure.

The combined value represents the maximum immediate financial exposure that should be considered when voluntarily opening an opponent monopoly.

---

# Brown Risk Matrix

Maximum-Rent Property: **Baltic Avenue**

| Development | Maximum Rent | 1 Landing | 2 Landings | 3 Landings | 4 Landings | 5 Landings | 6 Landings |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0-0 | $8 | $8 | $16 | $24 | $32 | $40 | $48 |
| 1-1 | $20 | $20 | $40 | $60 | $80 | $100 | $120 |
| 2-2 | $60 | $60 | $120 | $180 | $240 | $300 | $360 |
| 3-3 | $180 | $180 | $360 | $540 | $720 | $900 | $1,080 |
| 4-4 | $320 | $320 | $640 | $960 | $1,280 | $1,600 | $1,920 |
| Hotels | $450 | $450 | $900 | $1,350 | $1,800 | $2,250 | $2,700 |

---

# Light Blue Risk Matrix

Maximum-Rent Property: **Connecticut Avenue**

| Development | Maximum Rent | 1 Landing | 2 Landings | 3 Landings | 4 Landings | 5 Landings | 6 Landings |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0-0-0 | $12 | $12 | $24 | $36 | $48 | $60 | $72 |
| 1-1-1 | $60 | $60 | $120 | $180 | $240 | $300 | $360 |
| 2-2-2 | $180 | $180 | $360 | $540 | $720 | $900 | $1,080 |
| 3-3-3 | $500 | $500 | $1,000 | $1,500 | $2,000 | $2,500 | $3,000 |
| 4-4-4 | $700 | $700 | $1,400 | $2,100 | $2,800 | $3,500 | $4,200 |
| Hotels | $900 | $900 | $1,800 | $2,700 | $3,600 | $4,500 | $5,400 |

---

# Pink Risk Matrix

Maximum-Rent Property: **Virginia Avenue**

| Development | Maximum Rent | 1 Landing | 2 Landings | 3 Landings | 4 Landings | 5 Landings | 6 Landings |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0-0-0 | $28 | $28 | $56 | $84 | $112 | $140 | $168 |
| 1-1-1 | $140 | $140 | $280 | $420 | $560 | $700 | $840 |
| 2-2-2 | $400 | $400 | $800 | $1,200 | $1,600 | $2,000 | $2,400 |
| 3-3-3 | $850 | $850 | $1,700 | $2,550 | $3,400 | $4,250 | $5,100 |
| 4-4-4 | $1,025 | $1,025 | $2,050 | $3,075 | $4,100 | $5,125 | $6,150 |
| Hotels | $1,200 | $1,200 | $2,400 | $3,600 | $4,800 | $6,000 | $7,200 |

---

# Orange Risk Matrix

Maximum-Rent Property: **New York Avenue**

| Development | Maximum Rent | 1 Landing | 2 Landings | 3 Landings | 4 Landings | 5 Landings | 6 Landings |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0-0-0 | $32 | $32 | $64 | $96 | $128 | $160 | $192 |
| 1-1-1 | $80 | $80 | $160 | $240 | $320 | $400 | $480 |
| 2-2-2 | $220 | $220 | $440 | $660 | $880 | $1,100 | $1,320 |
| 3-3-3 | $600 | $600 | $1,200 | $1,800 | $2,400 | $3,000 | $3,600 |
| 4-4-4 | $800 | $800 | $1,600 | $2,400 | $3,200 | $4,000 | $4,800 |
| Hotels | $1,000 | $1,000 | $2,000 | $3,000 | $4,000 | $5,000 | $6,000 |

---

# Red Risk Matrix

Maximum-Rent Property: **Illinois Avenue**

| Development | Maximum Rent | 1 Landing | 2 Landings | 3 Landings | 4 Landings | 5 Landings | 6 Landings |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0-0-0 | $40 | $40 | $80 | $120 | $160 | $200 | $240 |
| 1-1-1 | $100 | $100 | $200 | $300 | $400 | $500 | $600 |
| 2-2-2 | $300 | $300 | $600 | $900 | $1,200 | $1,500 | $1,800 |
| 3-3-3 | $750 | $750 | $1,500 | $2,250 | $3,000 | $3,750 | $4,500 |
| 4-4-4 | $925 | $925 | $1,850 | $2,775 | $3,700 | $4,625 | $5,550 |
| Hotels | $1,100 | $1,100 | $2,200 | $3,300 | $4,400 | $5,500 | $6,600 |

---

# Yellow Risk Matrix

Maximum-Rent Property: **Marvin Gardens**

| Development | Maximum Rent | 1 Landing | 2 Landings | 3 Landings | 4 Landings | 5 Landings | 6 Landings |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0-0-0 | $48 | $48 | $96 | $144 | $192 | $240 | $288 |
| 1-1-1 | $120 | $120 | $240 | $360 | $480 | $600 | $720 |
| 2-2-2 | $360 | $360 | $720 | $1,080 | $1,440 | $1,800 | $2,160 |
| 3-3-3 | $850 | $850 | $1,700 | $2,550 | $3,400 | $4,250 | $5,100 |
| 4-4-4 | $1,025 | $1,025 | $2,050 | $3,075 | $4,100 | $5,125 | $6,150 |
| Hotels | $1,200 | $1,200 | $2,400 | $3,600 | $4,800 | $6,000 | $7,200 |

---

# Green Risk Matrix

Maximum-Rent Property: **Pennsylvania Avenue**

| Development | Maximum Rent | 1 Landing | 2 Landings | 3 Landings | 4 Landings | 5 Landings | 6 Landings |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0-0-0 | $56 | $56 | $112 | $168 | $224 | $280 | $336 |
| 1-1-1 | $150 | $150 | $300 | $450 | $600 | $750 | $900 |
| 2-2-2 | $450 | $450 | $900 | $1,350 | $1,800 | $2,250 | $2,700 |
| 3-3-3 | $1,000 | $1,000 | $2,000 | $3,000 | $4,000 | $5,000 | $6,000 |
| 4-4-4 | $1,200 | $1,200 | $2,400 | $3,600 | $4,800 | $6,000 | $7,200 |
| Hotels | $1,400 | $1,400 | $2,800 | $4,200 | $5,600 | $7,000 | $8,400 |

---

# Dark Blue Risk Matrix

Maximum-Rent Property: **Boardwalk**

| Development | Maximum Rent | 1 Landing | 2 Landings | 3 Landings | 4 Landings | 5 Landings | 6 Landings |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0-0 | $100 | $100 | $200 | $300 | $400 | $500 | $600 |
| 1-1 | $200 | $200 | $400 | $600 | $800 | $1,000 | $1,200 |
| 2-2 | $600 | $600 | $1,200 | $1,800 | $2,400 | $3,000 | $3,600 |
| 3-3 | $1,400 | $1,400 | $2,800 | $4,200 | $5,600 | $7,000 | $8,400 |
| 4-4 | $1,700 | $1,700 | $3,400 | $5,100 | $6,800 | $8,500 | $10,200 |
| Hotels | $2,000 | $2,000 | $4,000 | $6,000 | $8,000 | $10,000 | $12,000 |

---

# Railroad Risk Matrix

| Railroads Owned | Maximum Rent | 1 Landing | 2 Landings | 3 Landings | 4 Landings | 5 Landings | 6 Landings |
|----------------:|-------------:|----------:|-----------:|-----------:|-----------:|-----------:|-----------:|
| 1 | $25 | $25 | $50 | $75 | $100 | $125 | $150 |
| 2 | $50 | $50 | $100 | $150 | $200 | $250 | $300 |
| 3 | $100 | $100 | $200 | $300 | $400 | $500 | $600 |
| 4 | $200 | $200 | $400 | $600 | $800 | $1,000 | $1,200 |

---

# Utility Risk Matrix

Worst-case assumes a dice roll of 12.

| Utilities Owned | Maximum Rent | 1 Landing | 2 Landings | 3 Landings | 4 Landings | 5 Landings | 6 Landings |
|----------------:|-------------:|----------:|-----------:|-----------:|-----------:|-----------:|-----------:|
| 1 | $48 | $48 | $96 | $144 | $192 | $240 | $288 |
| 2 | $120 | $120 | $240 | $360 | $480 | $600 | $720 |

---

# Monopoly Development Cost

| Monopoly | Houses per Property | Total Houses | Hotels | Build Cost |
|-----------|-------------------:|-------------:|-------:|-----------:|
| Brown | 1-1 | 2 | 0 | $100 |
| Brown | 2-2 | 4 | 0 | $200 |
| Brown | 3-3 | 6 | 0 | $300 |
| Brown | 4-4 | 8 | 0 | $400 |
| Brown | Hotels | 0 | 2 | $500 |

| Monopoly | Houses per Property | Total Houses | Hotels | Build Cost |
|-----------|-------------------:|-------------:|-------:|-----------:|
| Light Blue | 1-1-1 | 3 | 0 | $150 |
| Light Blue | 2-2-2 | 6 | 0 | $300 |
| Light Blue | 3-3-3 | 9 | 0 | $450 |
| Light Blue | 4-4-4 | 12 | 0 | $600 |
| Light Blue | Hotels | 0 | 3 | $750 |

| Monopoly | Houses per Property | Total Houses | Hotels | Build Cost |
|-----------|-------------------:|-------------:|-------:|-----------:|
| Pink | 1-1-1 | 3 | 0 | $300 |
| Pink | 2-2-2 | 6 | 0 | $600 |
| Pink | 3-3-3 | 9 | 0 | $900 |
| Pink | 4-4-4 | 12 | 0 | $1,200 |
| Pink | Hotels | 0 | 3 | $1,500 |

| Monopoly | Houses per Property | Total Houses | Hotels | Build Cost |
|-----------|-------------------:|-------------:|-------:|-----------:|
| Orange | 1-1-1 | 3 | 0 | $300 |
| Orange | 2-2-2 | 6 | 0 | $600 |
| Orange | 3-3-3 | 9 | 0 | $900 |
| Orange | 4-4-4 | 12 | 0 | $1,200 |
| Orange | Hotels | 0 | 3 | $1,500 |

| Monopoly | Houses per Property | Total Houses | Hotels | Build Cost |
|-----------|-------------------:|-------------:|-------:|-----------:|
| Red | 1-1-1 | 3 | 0 | $450 |
| Red | 2-2-2 | 6 | 0 | $900 |
| Red | 3-3-3 | 9 | 0 | $1,350 |
| Red | 4-4-4 | 12 | 0 | $1,800 |
| Red | Hotels | 0 | 3 | $2,250 |

| Monopoly | Houses per Property | Total Houses | Hotels | Build Cost |
|-----------|-------------------:|-------------:|-------:|-----------:|
| Yellow | 1-1-1 | 3 | 0 | $450 |
| Yellow | 2-2-2 | 6 | 0 | $900 |
| Yellow | 3-3-3 | 9 | 0 | $1,350 |
| Yellow | 4-4-4 | 12 | 0 | $1,800 |
| Yellow | Hotels | 0 | 3 | $2,250 |

| Monopoly | Houses per Property | Total Houses | Hotels | Build Cost |
|-----------|-------------------:|-------------:|-------:|-----------:|
| Green | 1-1-1 | 3 | 0 | $600 |
| Green | 2-2-2 | 6 | 0 | $1,200 |
| Green | 3-3-3 | 9 | 0 | $1,800 |
| Green | 4-4-4 | 12 | 0 | $2,400 |
| Green | Hotels | 0 | 3 | $3,000 |

| Monopoly | Houses per Property | Total Houses | Hotels | Build Cost |
|-----------|-------------------:|-------------:|-------:|-----------:|
| Dark Blue | 1-1 | 2 | 0 | $400 |
| Dark Blue | 2-2 | 4 | 0 | $800 |
| Dark Blue | 3-3 | 6 | 0 | $1,200 |
| Dark Blue | 4-4 | 8 | 0 | $1,600 |
| Dark Blue | Hotels | 0 | 2 | $2,000 |

---

# House Consumption Reference

| Development | Houses Used | Hotels Used |
|--------------|-----------:|------------:|
| 0-0 | 0 | 0 |
| 1-1 | 2 | 0 |
| 2-2 | 4 | 0 |
| 3-3 | 6 | 0 |
| 4-4 | 8 | 0 |
| Hotels | 0 | 2 |

| Development | Houses Used | Hotels Used |
|--------------|-----------:|------------:|
| 0-0-0 | 0 | 0 |
| 1-1-1 | 3 | 0 |
| 2-2-2 | 6 | 0 |
| 3-3-3 | 9 | 0 |
| 4-4-4 | 12 | 0 |
| Hotels | 0 | 3 |

---