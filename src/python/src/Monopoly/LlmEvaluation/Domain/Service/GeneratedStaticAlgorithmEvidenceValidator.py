"""Validate LLM-generated Static Algorithm Evidence against the canonical schema."""

from __future__ import annotations

from typing import Any

from Monopoly.LlmEvaluation.Domain.Model.JudgeEnums import (
    CANONICAL_ALGORITHM_ID,
    CANONICAL_ALGORITHM_VERSION,
)
from Monopoly.LlmEvaluation.Domain.Model.JudgeValidationError import JudgeValidationErrorRecord
from Monopoly.LlmEvaluation.Domain.Service.JudgeValidationErrorFactory import (
    duplicateCalculationId,
    selfDependency,
    unknownDependentCalculationId,
    unknownFinalConclusionReference,
)
from Monopoly.LlmEvaluation.Domain.Service.StaticAlgorithmEvidenceSchema import (
    CALCULATION_ITEM_ALLOWED_KEYS,
    CALCULATION_ITEM_REQUIRED_KEYS,
    CANONICAL_ALGORITHM_NAME,
    CANONICAL_PURPOSE,
    EVIDENCE_ENVELOPE_KEYS,
    FINAL_CONCLUSIONS_KEYS,
    METADATA_KEYS,
    REGISTERED_CALCULATION_TYPES,
    SPECIFICATION_DEPENDENCY_KEYS,
    STATISTICS_KEYS,
    SUBJECT_KEYS,
    VALID_AUTOMATIC_FLAGS,
    VALID_FINAL_CLASSIFICATIONS,
    VALID_RISK_LABELS,
    VALID_RISK_WARNINGS,
    VALID_SIDES,
    VALID_STATUSES,
    VALID_UNITS,
)


class GeneratedStaticAlgorithmEvidenceValidator:
    """Schema-only validation for Judge fallback evidence objects."""

    def __init__(self) -> None:
        self._lastStructuredErrors: tuple[JudgeValidationErrorRecord, ...] = ()

    @property
    def lastStructuredErrors(self) -> tuple[JudgeValidationErrorRecord, ...]:
        return self._lastStructuredErrors

    def validate(self, evidence: dict[str, Any], *, path: str = "generated_static_algorithm_evidence") -> list[str]:
        structured: list[JudgeValidationErrorRecord] = []
        errors: list[str] = []

        if not isinstance(evidence, dict):
            return [f"{path} must be an object"]

        unknownEnvelope = set(evidence.keys()) - EVIDENCE_ENVELOPE_KEYS
        if unknownEnvelope:
            errors.append(f"{path}: unknown envelope fields: {sorted(unknownEnvelope)}")

        for key in EVIDENCE_ENVELOPE_KEYS:
            if key not in evidence:
                errors.append(f"{path}: missing required field '{key}'")

        if errors:
            return errors

        errors.extend(self._validateEnvelopeIdentity(evidence, path))
        errors.extend(self._validateCalculations(evidence, path))
        errors.extend(self._validateFinalConclusions(evidence.get("final_conclusions"), f"{path}.final_conclusions"))
        errors.extend(self._validateMetadata(evidence.get("metadata"), f"{path}.metadata"))
        errors.extend(self._validateStatistics(evidence.get("statistics"), f"{path}.statistics"))
        errors.extend(self._validateDependencyGraph(evidence, path, structuredErrors=structured))
        errors.extend(self._validateConclusionReferences(evidence, path, structuredErrors=structured))
        self._lastStructuredErrors = tuple(structured)
        return errors

    def validateForCompleteExecution(
        self,
        evidence: dict[str, Any],
        *,
        path: str = "generated_static_algorithm_evidence",
    ) -> list[str]:
        errors: list[str] = []
        calcs = evidence.get("intermediate_calculations")
        if not isinstance(calcs, list) or len(calcs) == 0:
            errors.append(f"{path}: COMPLETE execution requires non-empty intermediate_calculations")

        finalConclusions = evidence.get("final_conclusions")
        if not isinstance(finalConclusions, dict):
            errors.append(f"{path}: COMPLETE execution requires final_conclusions object")
            return errors

        for required in ("trade_ratio", "classification", "classification_calculation_id"):
            if required not in finalConclusions:
                errors.append(f"{path}.final_conclusions: missing '{required}' for COMPLETE execution")
        return errors

    def _validateEnvelopeIdentity(self, evidence: dict[str, Any], path: str) -> list[str]:
        errors: list[str] = []
        if evidence.get("algorithm_id") != CANONICAL_ALGORITHM_ID:
            errors.append(f"{path}.algorithm_id must be {CANONICAL_ALGORITHM_ID}")
        if evidence.get("algorithm_name") != CANONICAL_ALGORITHM_NAME:
            errors.append(f"{path}.algorithm_name must be {CANONICAL_ALGORITHM_NAME!r}")
        if evidence.get("algorithm_version") != CANONICAL_ALGORITHM_VERSION:
            errors.append(f"{path}.algorithm_version must be {CANONICAL_ALGORITHM_VERSION}")
        if evidence.get("purpose") != CANONICAL_PURPOSE:
            errors.append(f"{path}.purpose must be {CANONICAL_PURPOSE!r}")
        if not isinstance(evidence.get("id"), str) or not evidence["id"]:
            errors.append(f"{path}.id must be a non-empty string")
        return errors

    def _validateCalculations(self, evidence: dict[str, Any], path: str) -> list[str]:
        errors: list[str] = []
        calcs = evidence.get("intermediate_calculations")
        if not isinstance(calcs, list):
            return [f"{path}.intermediate_calculations must be an array"]
        if len(calcs) == 0:
            errors.append(f"{path}.intermediate_calculations must not be empty")

        for index, item in enumerate(calcs):
            itemPath = f"{path}.intermediate_calculations[{index}]"
            errors.extend(self._validateCalculationItem(item, itemPath))
        return errors

    def _validateCalculationItem(self, item: Any, path: str) -> list[str]:
        errors: list[str] = []
        if not isinstance(item, dict):
            return [f"{path} must be an object"]

        unknown = set(item.keys()) - CALCULATION_ITEM_ALLOWED_KEYS
        if unknown:
            errors.append(f"{path}: unknown fields: {sorted(unknown)}")

        for key in CALCULATION_ITEM_REQUIRED_KEYS:
            if key not in item:
                errors.append(f"{path}: missing required field '{key}'")

        if errors:
            return errors

        if not isinstance(item["id"], str) or not item["id"]:
            errors.append(f"{path}.id must be a non-empty string")

        calcType = item["calculation_type"]
        if calcType not in REGISTERED_CALCULATION_TYPES:
            errors.append(f"{path}.calculation_type invalid: {calcType!r}")

        if item["status"] not in VALID_STATUSES:
            errors.append(f"{path}.status invalid: {item['status']!r}")

        if item["side"] not in VALID_SIDES:
            errors.append(f"{path}.side invalid: {item['side']!r}")

        if not isinstance(item["description"], str):
            errors.append(f"{path}.description must be string")

        if not isinstance(item["input_references"], list) or any(
            not isinstance(ref, str) for ref in item["input_references"]
        ):
            errors.append(f"{path}.input_references must be an array of strings")

        for objectField in ("input_values", "sources", "intermediate_values"):
            if not isinstance(item[objectField], dict):
                errors.append(f"{path}.{objectField} must be an object")

        for arrayField in ("limitations", "missing_inputs"):
            if not isinstance(item[arrayField], list) or any(not isinstance(entry, str) for entry in item[arrayField]):
                errors.append(f"{path}.{arrayField} must be an array of strings")

        if "formula" in item and item["formula"] is not None and not isinstance(item["formula"], str):
            errors.append(f"{path}.formula must be string or null")
        if "procedure" in item and item["procedure"] is not None and not isinstance(item["procedure"], str):
            errors.append(f"{path}.procedure must be string or null")

        if "unit" in item and item["unit"] is not None and item["unit"] not in VALID_UNITS:
            errors.append(f"{path}.unit invalid: {item['unit']!r}")

        if "dependent_calculation_ids" in item:
            deps = item["dependent_calculation_ids"]
            if not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps):
                errors.append(f"{path}.dependent_calculation_ids must be an array of strings")

        if "metadata" in item and not isinstance(item["metadata"], dict):
            errors.append(f"{path}.metadata must be an object")

        errors.extend(self._validateSubject(item.get("subject"), f"{path}.subject"))
        errors.extend(self._validateStatusRules(item, path))
        return errors

    def _validateSubject(self, subject: Any, path: str) -> list[str]:
        errors: list[str] = []
        if not isinstance(subject, dict):
            return [f"{path} must be an object"]

        unknown = set(subject.keys()) - SUBJECT_KEYS
        if unknown:
            errors.append(f"{path}: unknown fields: {sorted(unknown)}")

        for key in SUBJECT_KEYS:
            if key not in subject:
                errors.append(f"{path}: missing required field '{key}'")

        if errors:
            return errors

        for arrayKey in ("player_ids", "property_ids", "group_ids", "transfer_ids"):
            value = subject[arrayKey]
            if not isinstance(value, list) or any(not isinstance(entry, str) for entry in value):
                errors.append(f"{path}.{arrayKey} must be an array of strings")

        tradeId = subject["trade_id"]
        if tradeId is not None and not isinstance(tradeId, str):
            errors.append(f"{path}.trade_id must be string or null")
        return errors

    def _validateStatusRules(self, item: dict[str, Any], path: str) -> list[str]:
        errors: list[str] = []
        status = item["status"]

        if status == "COMPLETE":
            if item["result"] is None:
                errors.append(f"{path}: COMPLETE calculations must have non-null result")
            if item["missing_inputs"]:
                errors.append(f"{path}: COMPLETE calculations must have empty missing_inputs")
            formula = item.get("formula")
            procedure = item.get("procedure")
            if not formula and not procedure:
                errors.append(f"{path}: COMPLETE calculations require formula or procedure")

        elif status in ("PARTIAL", "UNAVAILABLE"):
            if not item["missing_inputs"] and not item["limitations"]:
                errors.append(f"{path}: {status} calculations must explain missing_inputs or limitations")

        elif status == "ERROR":
            if not item["limitations"]:
                errors.append(f"{path}: ERROR calculations must identify error in limitations")

        return errors

    def _validateFinalConclusions(self, conclusions: Any, path: str) -> list[str]:
        errors: list[str] = []
        if not isinstance(conclusions, dict):
            return [f"{path} must be an object"]

        unknown = set(conclusions.keys()) - FINAL_CONCLUSIONS_KEYS
        if unknown:
            errors.append(f"{path}: unknown fields: {sorted(unknown)}")

        if "classification" in conclusions:
            classification = conclusions["classification"]
            if classification is not None and classification not in VALID_FINAL_CLASSIFICATIONS:
                errors.append(f"{path}.classification invalid: {classification!r}")

        if "classification_calculation_id" in conclusions:
            calcId = conclusions["classification_calculation_id"]
            if calcId is not None and not isinstance(calcId, str):
                errors.append(f"{path}.classification_calculation_id must be string or null")

        if "trade_ratio" in conclusions:
            errors.extend(self._validateConclusionObject(conclusions["trade_ratio"], f"{path}.trade_ratio"))

        if "flags" in conclusions:
            flags = conclusions["flags"]
            if not isinstance(flags, dict):
                errors.append(f"{path}.flags must be an object")
            else:
                values = flags.get("values")
                if not isinstance(values, list):
                    errors.append(f"{path}.flags.values must be an array")
                elif any(flag not in VALID_AUTOMATIC_FLAGS for flag in values):
                    errors.append(f"{path}.flags.values contains invalid flag")
                calcId = flags.get("calculation_id")
                if calcId is not None and not isinstance(calcId, str):
                    errors.append(f"{path}.flags.calculation_id must be string")

        if "risk_labels" in conclusions:
            errors.extend(self._validateRiskLabels(conclusions["risk_labels"], f"{path}.risk_labels"))

        if "risk_warnings" in conclusions:
            errors.extend(self._validateRiskWarnings(conclusions["risk_warnings"], f"{path}.risk_warnings"))

        if "strategic_value" in conclusions:
            sv = conclusions["strategic_value"]
            if not isinstance(sv, dict):
                errors.append(f"{path}.strategic_value must be an object")
            else:
                for playerId, entry in sv.items():
                    if not isinstance(playerId, str):
                        errors.append(f"{path}.strategic_value keys must be strings")
                    if not isinstance(entry, dict):
                        errors.append(f"{path}.strategic_value[{playerId}] must be object")
                    else:
                        if "value" not in entry or not isinstance(entry["value"], (int, float)):
                            errors.append(f"{path}.strategic_value[{playerId}].value must be number")
                        if "calculation_id" not in entry or not isinstance(entry["calculation_id"], str):
                            errors.append(f"{path}.strategic_value[{playerId}].calculation_id must be string")

        if "limitations" in conclusions:
            limitations = conclusions["limitations"]
            if not isinstance(limitations, list) or any(not isinstance(entry, str) for entry in limitations):
                errors.append(f"{path}.limitations must be an array of strings")

        return errors

    def _validateConclusionObject(self, value: Any, path: str) -> list[str]:
        errors: list[str] = []
        if not isinstance(value, dict):
            return [f"{path} must be an object"]
        if "value" not in value or not isinstance(value["value"], (int, float)):
            errors.append(f"{path}.value must be number")
        if "calculation_id" not in value or not isinstance(value["calculation_id"], str):
            errors.append(f"{path}.calculation_id must be string")
        return errors

    def _validateRiskLabels(self, riskLabels: Any, path: str) -> list[str]:
        errors: list[str] = []
        if not isinstance(riskLabels, dict):
            return [f"{path} must be an object"]

        for playerId, entry in riskLabels.items():
            if not isinstance(playerId, str):
                errors.append(f"{path} keys must be strings")
            if not isinstance(entry, dict):
                errors.append(f"{path}[{playerId}] must be object")
                continue
            for sideKey in ("before", "after"):
                if sideKey in entry:
                    label = entry[sideKey]
                    if label not in VALID_RISK_LABELS:
                        errors.append(f"{path}[{playerId}].{sideKey} invalid risk label: {label!r}")
            for idKey in ("before_calculation_id", "after_calculation_id"):
                if idKey in entry and not isinstance(entry[idKey], str):
                    errors.append(f"{path}[{playerId}].{idKey} must be string")
        return errors

    def _validateRiskWarnings(self, riskWarnings: Any, path: str) -> list[str]:
        errors: list[str] = []
        if not isinstance(riskWarnings, dict):
            return [f"{path} must be an object"]
        values = riskWarnings.get("values")
        if not isinstance(values, list):
            errors.append(f"{path}.values must be an array")
        elif any(warning not in VALID_RISK_WARNINGS for warning in values):
            errors.append(f"{path}.values contains invalid risk warning")
        calcIds = riskWarnings.get("calculation_ids")
        if calcIds is not None:
            if not isinstance(calcIds, list) or any(not isinstance(calcId, str) for calcId in calcIds):
                errors.append(f"{path}.calculation_ids must be an array of strings")
        return errors

    def _validateMetadata(self, metadata: Any, path: str) -> list[str]:
        errors: list[str] = []
        if not isinstance(metadata, dict):
            return [f"{path} must be an object"]

        unknown = set(metadata.keys()) - METADATA_KEYS
        if unknown:
            errors.append(
                f"{path}: unknown fields: {sorted(unknown)} (use specification_dependencies, not dependency_versions)"
            )

        if "implementation_overrides" not in metadata:
            errors.append(f"{path}: missing implementation_overrides")
        elif not isinstance(metadata["implementation_overrides"], list):
            errors.append(f"{path}.implementation_overrides must be an array")

        if "specification_dependencies" not in metadata:
            errors.append(f"{path}: missing specification_dependencies")
        elif not isinstance(metadata["specification_dependencies"], list):
            errors.append(f"{path}.specification_dependencies must be an array")
        else:
            for index, dep in enumerate(metadata["specification_dependencies"]):
                depPath = f"{path}.specification_dependencies[{index}]"
                if not isinstance(dep, dict):
                    errors.append(f"{depPath} must be an object")
                    continue
                unknownDep = set(dep.keys()) - SPECIFICATION_DEPENDENCY_KEYS
                if unknownDep:
                    errors.append(f"{depPath}: unknown fields: {sorted(unknownDep)}")
                for key in SPECIFICATION_DEPENDENCY_KEYS:
                    if key not in dep or not isinstance(dep[key], str):
                        errors.append(f"{depPath}.{key} must be a string")
        return errors

    def _validateStatistics(self, statistics: Any, path: str) -> list[str]:
        errors: list[str] = []
        if not isinstance(statistics, dict):
            return [f"{path} must be an object"]

        unknown = set(statistics.keys()) - STATISTICS_KEYS
        if unknown:
            errors.append(f"{path}: unknown fields: {sorted(unknown)} (use calculation_count)")

        if "calculation_count" not in statistics:
            errors.append(f"{path}: missing calculation_count")
        elif not isinstance(statistics["calculation_count"], int):
            errors.append(f"{path}.calculation_count must be an integer")
        return errors

    def _validateDependencyGraph(
        self,
        evidence: dict[str, Any],
        path: str,
        *,
        structuredErrors: list[JudgeValidationErrorRecord],
    ) -> list[str]:
        errors: list[str] = []
        calcs = evidence.get("intermediate_calculations", [])
        if not isinstance(calcs, list):
            return errors

        allIds = {calc["id"] for calc in calcs if isinstance(calc, dict) and isinstance(calc.get("id"), str)}
        idCounts: dict[str, int] = {}
        for calc in calcs:
            if isinstance(calc, dict) and isinstance(calc.get("id"), str):
                calcId = calc["id"]
                idCounts[calcId] = idCounts.get(calcId, 0) + 1

        for calcId, count in idCounts.items():
            if count > 1:
                itemPath = f"{path}.intermediate_calculations"
                record = duplicateCalculationId(path=itemPath, calculationId=calcId)
                structuredErrors.append(record)
                errors.append(record.message)

        for index, calc in enumerate(calcs):
            if not isinstance(calc, dict):
                continue
            calcId = calc.get("id")
            deps = calc.get("dependent_calculation_ids", [])
            if not isinstance(deps, list):
                continue
            itemPath = f"{path}.intermediate_calculations[{index}].dependent_calculation_ids"
            for depIndex, depId in enumerate(deps):
                if depId not in allIds:
                    depPath = f"{itemPath}[{depIndex}]"
                    record = unknownDependentCalculationId(path=depPath, calculationId=str(depId))
                    structuredErrors.append(record)
                    errors.append(
                        f"{path}.intermediate_calculations[{index}].dependent_calculation_ids "
                        f"references unknown id {depId!r}"
                    )
                if depId == calcId:
                    record = selfDependency(path=itemPath, calculationId=str(calcId))
                    structuredErrors.append(record)
                    errors.append(f"{path}.intermediate_calculations[{index}] has self-dependency")
        return errors

    def _validateConclusionReferences(
        self,
        evidence: dict[str, Any],
        path: str,
        *,
        structuredErrors: list[JudgeValidationErrorRecord],
    ) -> list[str]:
        errors: list[str] = []
        calcs = evidence.get("intermediate_calculations", [])
        if not isinstance(calcs, list):
            return errors
        allIds = {calc["id"] for calc in calcs if isinstance(calc, dict) and isinstance(calc.get("id"), str)}

        conclusions = evidence.get("final_conclusions")
        if not isinstance(conclusions, dict):
            return errors

        referencedIds: list[str] = []
        tradeRatio = conclusions.get("trade_ratio")
        if isinstance(tradeRatio, dict) and isinstance(tradeRatio.get("calculation_id"), str):
            referencedIds.append(tradeRatio["calculation_id"])

        flags = conclusions.get("flags")
        if isinstance(flags, dict) and isinstance(flags.get("calculation_id"), str):
            referencedIds.append(flags["calculation_id"])

        classificationCalcId = conclusions.get("classification_calculation_id")
        if isinstance(classificationCalcId, str):
            referencedIds.append(classificationCalcId)

        strategicValue = conclusions.get("strategic_value")
        if isinstance(strategicValue, dict):
            for entry in strategicValue.values():
                if isinstance(entry, dict) and isinstance(entry.get("calculation_id"), str):
                    referencedIds.append(entry["calculation_id"])

        riskLabels = conclusions.get("risk_labels")
        if isinstance(riskLabels, dict):
            for entry in riskLabels.values():
                if isinstance(entry, dict):
                    for key in ("before_calculation_id", "after_calculation_id"):
                        if isinstance(entry.get(key), str):
                            referencedIds.append(entry[key])

        riskWarnings = conclusions.get("risk_warnings")
        if isinstance(riskWarnings, dict):
            for calcId in riskWarnings.get("calculation_ids", []):
                if isinstance(calcId, str):
                    referencedIds.append(calcId)

        for calcId in referencedIds:
            if calcId not in allIds:
                record = unknownFinalConclusionReference(
                    path=f"{path}.final_conclusions",
                    calculationId=calcId,
                )
                structuredErrors.append(record)
                errors.append(f"{path}.final_conclusions references unknown calculation id {calcId!r}")
        return errors
