"""Output-field verification tests.

This package contains focused unit tests for every canonical output field
in the Static Algorithm Evidence output. Each test verifies the actual meaning
of the field, not just its existence.

Registry:
- `output_field_inventory.py` — canonical field definitions from specifications
- `output_field_coverage.py` — structured mapping: field → scenario → test
- `OUTPUT_COVERAGE_MATRIX.md` — human-readable coverage matrix
- `output_field_assertion_handlers.py` — semantic assertion handlers per field
- `test_output_field_coverage_guard.py` — fails when any field lacks coverage

Test organization (one parametrized `test_output_field` per module, ids = field key):
- `test_evidence_envelope_fields.py` — envelope fields
- `test_calculation_item_common_fields.py` — common calculation item fields, status, side, sources
- `test_subject_fields.py` — subject collections
- `test_*_fields.py` — intermediate values and results per calculation family
- `test_final_conclusion_fields.py` — final conclusions
- `test_metadata_fields.py` / `test_statistics_fields.py` — evidence metadata and statistics
"""
