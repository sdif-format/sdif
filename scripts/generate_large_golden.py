#!/usr/bin/env python3
"""Generate large canonical JSON golden files for SDIF benchmarks.

The generated fixtures are intentionally SDIF-representable.

Important constraint:
- Arrays of objects are encoded as SDIF tables.
- SDIF table cells must remain scalar in the current MVP.
- Therefore, complex structures are represented as normalized top-level tables
  linked by IDs instead of nested arrays/objects inside table rows.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


JsonObject = dict[str, Any]


def write_fixture(output_dir: Path, name: str, data: JsonObject) -> None:
    fixture_dir = output_dir / name
    fixture_dir.mkdir(parents=True, exist_ok=True)

    target = fixture_dir / "equivalent.json"
    target.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def make_large_plan(multiplier: int) -> JsonObject:
    phases: list[JsonObject] = []
    milestones: list[JsonObject] = []
    tasks: list[JsonObject] = []
    task_dependencies: list[JsonObject] = []
    acceptance_criteria: list[JsonObject] = []
    risks: list[JsonObject] = []

    for phase_index in range(1, 8 * multiplier + 1):
        phase_id = f"PHASE-{phase_index:03d}"

        phases.append(
            {
                "id": phase_id,
                "title": f"Large benchmark phase {phase_index}",
                "status": ["planned", "active", "blocked", "closed"][phase_index % 4],
                "owner": f"team-{(phase_index % 5) + 1}",
                "summary": (
                    "Synthetic phase used to benchmark large planning documents "
                    "with normalized milestone and task tables."
                ),
            }
        )

        for milestone_index in range(1, 9):
            milestone_id = f"MS-{phase_index:03d}-{milestone_index:02d}"

            milestones.append(
                {
                    "id": milestone_id,
                    "phase_id": phase_id,
                    "title": f"Milestone {milestone_index} for phase {phase_index}",
                    "status": ["pending", "in_progress", "done"][milestone_index % 3],
                    "gate": f"gate-{phase_index:03d}-{milestone_index:02d}",
                    "evidence": f"reports/plan/{phase_id}/{milestone_id}.md",
                }
            )

            for task_index in range(1, 13):
                task_id = f"TASK-{phase_index:03d}-{milestone_index:02d}-{task_index:03d}"

                tasks.append(
                    {
                        "id": task_id,
                        "milestone_id": milestone_id,
                        "title": f"Implement governed planning task {task_id}",
                        "status": ["pending", "in_progress", "blocked", "done"][
                            (phase_index + milestone_index + task_index) % 4
                        ],
                        "owner": f"team-{(task_index % 5) + 1}",
                        "priority": ["P0", "P1", "P2", "P3"][task_index % 4],
                        "estimate_days": (task_index % 9) + 1,
                    }
                )

                task_dependencies.append(
                    {
                        "task_id": task_id,
                        "depends_on": (
                            f"TASK-{phase_index:03d}-{milestone_index:02d}-{max(1, task_index - 1):03d}"
                        ),
                        "kind": "task",
                    }
                )
                task_dependencies.append(
                    {
                        "task_id": task_id,
                        "depends_on": f"ARCH-{phase_index:03d}-{milestone_index:02d}",
                        "kind": "architecture",
                    }
                )

                for criterion_index in range(1, 5):
                    acceptance_criteria.append(
                        {
                            "task_id": task_id,
                            "criterion_index": criterion_index,
                            "criterion": [
                                "The change is covered by deterministic tests.",
                                "The implementation preserves public contracts.",
                                "The benchmark output is reproducible from canonical JSON.",
                                "The generated SDIF output parses without semantic loss.",
                            ][criterion_index - 1],
                        }
                    )

                risks.append(
                    {
                        "task_id": task_id,
                        "level": ["low", "medium", "high"][task_index % 3],
                        "description": (
                            "Potential drift between generated benchmark data and "
                            "hand-maintained fixtures if canonical JSON is bypassed."
                        ),
                        "mitigation": "Keep JSON as the only semantic source of truth.",
                    }
                )

    return {
        "document_type": "large-plan",
        "version": "1.0.0",
        "generated": True,
        "multiplier": multiplier,
        "purpose": "Stress-test token efficiency for large planning documents.",
        "phases": phases,
        "milestones": milestones,
        "tasks": tasks,
        "task_dependencies": task_dependencies,
        "acceptance_criteria": acceptance_criteria,
        "risks": risks,
    }


def make_large_registry(multiplier: int) -> JsonObject:
    modules: list[JsonObject] = []
    components: list[JsonObject] = []
    capabilities: list[JsonObject] = []
    capability_inputs: list[JsonObject] = []
    capability_outputs: list[JsonObject] = []

    for module_index in range(1, 18 * multiplier + 1):
        module_id = f"MOD-{module_index:03d}"

        modules.append(
            {
                "id": module_id,
                "name": f"module_{module_index}",
                "namespace": f"benchmark.module_{module_index}",
                "stability": ["experimental", "stable", "deprecated"][module_index % 3],
            }
        )

        for component_index in range(1, 11):
            component_id = f"CMP-{module_index:03d}-{component_index:02d}"

            components.append(
                {
                    "id": component_id,
                    "module_id": module_id,
                    "name": f"component_{module_index}_{component_index}",
                    "boundary": ["kernel", "runtime", "adapter", "observability"][
                        component_index % 4
                    ],
                    "description": (
                        "Synthetic registry component used to benchmark repeated "
                        "structured metadata."
                    ),
                }
            )

            for capability_index in range(1, 9):
                capability_id = (
                    f"CAP-{module_index:03d}-{component_index:02d}-{capability_index:02d}"
                )

                capabilities.append(
                    {
                        "id": capability_id,
                        "component_id": component_id,
                        "name": f"capability_{module_index}_{component_index}_{capability_index}",
                        "kind": ["read", "write", "execute", "govern"][capability_index % 4],
                        "authority_required": capability_index % 3 == 0,
                        "stability": ["experimental", "stable", "deprecated"][
                            capability_index % 3
                        ],
                    }
                )

                for input_name in ["subject_id", "trace_id", "authority_context", "payload"]:
                    capability_inputs.append(
                        {
                            "capability_id": capability_id,
                            "name": input_name,
                            "required": input_name != "payload",
                        }
                    )

                for output_name in ["decision", "evidence_ref", "diagnostics"]:
                    capability_outputs.append(
                        {
                            "capability_id": capability_id,
                            "name": output_name,
                        }
                    )

    return {
        "document_type": "large-registry",
        "version": "1.0.0",
        "generated": True,
        "multiplier": multiplier,
        "purpose": "Stress-test compact representation of registries and capabilities.",
        "modules": modules,
        "components": components,
        "capabilities": capabilities,
        "capability_inputs": capability_inputs,
        "capability_outputs": capability_outputs,
    }


def make_large_schema_catalog(multiplier: int) -> JsonObject:
    entities: list[JsonObject] = []
    fields: list[JsonObject] = []
    field_validations: list[JsonObject] = []
    field_ui: list[JsonObject] = []
    relations: list[JsonObject] = []
    rules: list[JsonObject] = []
    permissions: list[JsonObject] = []

    field_types = [
        "string",
        "text",
        "integer",
        "decimal",
        "boolean",
        "date",
        "datetime",
        "uuid",
        "enum",
        "money",
    ]

    widgets = [
        "text",
        "textarea",
        "number",
        "checkbox",
        "date",
        "datetime",
        "select",
        "currency",
    ]

    for entity_index in range(1, 36 * multiplier + 1):
        entity_id = f"ENT-{entity_index:03d}"
        entity_name = f"entity_{entity_index:03d}"

        entities.append(
            {
                "id": entity_id,
                "name": entity_name,
                "title": f"Entity {entity_index}",
                "description": (
                    "Large generated entity definition used to validate compactness "
                    "for schema-heavy documents."
                ),
            }
        )

        for field_index in range(1, 29):
            field_id = f"FLD-{entity_index:03d}-{field_index:02d}"
            field_type = field_types[field_index % len(field_types)]

            fields.append(
                {
                    "id": field_id,
                    "entity_id": entity_id,
                    "name": f"field_{field_index:02d}",
                    "label": f"Field {field_index}",
                    "type": field_type,
                    "required": field_index % 4 != 0,
                    "unique": field_index in {1, 2},
                    "default": "null" if field_index % 5 else f"default-{field_index}",
                    "description": (
                        "Synthetic schema field with validation and UI metadata."
                    ),
                }
            )

            field_validations.append(
                {
                    "field_id": field_id,
                    "min": 0 if field_type in {"integer", "decimal", "money"} else "null",
                    "max": 100000 if field_type in {"integer", "decimal", "money"} else "null",
                    "pattern": "^[a-zA-Z0-9_-]+$" if field_type == "string" else "null",
                }
            )

            field_ui.append(
                {
                    "field_id": field_id,
                    "widget": widgets[field_index % len(widgets)],
                    "group": f"group_{(field_index % 6) + 1}",
                    "visible": field_index % 7 != 0,
                    "readonly": field_index % 11 == 0,
                }
            )

        for relation_name, relation_type, target in [
            ("owner", "belongsTo", "user"),
            ("children", "hasMany", f"entity_{max(1, entity_index - 1):03d}"),
            ("audit_entries", "hasMany", "audit_entry"),
        ]:
            relations.append(
                {
                    "entity_id": entity_id,
                    "name": relation_name,
                    "type": relation_type,
                    "target": target,
                    "required": relation_name == "owner",
                    "on_delete": "restrict" if relation_name != "children" else "cascade",
                }
            )

        for rule_index in range(1, 7):
            rules.append(
                {
                    "id": f"RULE-{entity_index:03d}-{rule_index:02d}",
                    "entity_id": entity_id,
                    "name": f"rule_{rule_index}",
                    "when": f"field_{rule_index:02d} != null",
                    "then": "record_validation_evidence",
                    "severity": ["info", "warning", "error"][rule_index % 3],
                }
            )

        for action, role in [
            ("create", "admin"),
            ("create", "operator"),
            ("read", "admin"),
            ("read", "operator"),
            ("read", "viewer"),
            ("update", "admin"),
            ("update", "operator"),
            ("delete", "admin"),
        ]:
            permissions.append(
                {
                    "entity_id": entity_id,
                    "action": action,
                    "role": role,
                }
            )

    return {
        "document_type": "large-schema-catalog",
        "version": "1.0.0",
        "generated": True,
        "multiplier": multiplier,
        "purpose": "Stress-test schema-heavy JSON structures against SDIF encoding.",
        "entities": entities,
        "fields": fields,
        "field_validations": field_validations,
        "field_ui": field_ui,
        "relations": relations,
        "rules": rules,
        "permissions": permissions,
    }


def make_large_validation_report(multiplier: int) -> JsonObject:
    suites: list[JsonObject] = []
    cases: list[JsonObject] = []
    evidence: list[JsonObject] = []
    diagnostics: list[JsonObject] = []

    for suite_index in range(1, 14 * multiplier + 1):
        suite_id = f"SUITE-{suite_index:03d}"
        passed = 0
        failed = 0
        skipped = 0
        warnings = 0

        for case_index in range(1, 41):
            case_id = f"CASE-{suite_index:03d}-{case_index:03d}"
            status = ["passed", "failed", "skipped", "warning"][
                (suite_index + case_index) % 4
            ]

            if status == "passed":
                passed += 1
            elif status == "failed":
                failed += 1
            elif status == "skipped":
                skipped += 1
            elif status == "warning":
                warnings += 1

            cases.append(
                {
                    "id": case_id,
                    "suite_id": suite_id,
                    "name": f"validation_case_{suite_index}_{case_index}",
                    "status": status,
                    "duration_ms": 15 + ((suite_index * case_index) % 850),
                    "assertions": 3 + (case_index % 9),
                }
            )

            evidence.append(
                {
                    "case_id": case_id,
                    "trace_id": f"trace-{suite_index:03d}-{case_index:03d}",
                    "artifact": f"reports/validation/{suite_index:03d}/{case_id}.json",
                    "sha256": f"{suite_index:03d}{case_index:03d}" * 10,
                }
            )

            for diagnostic_index in range(1, 5):
                diagnostics.append(
                    {
                        "case_id": case_id,
                        "code": f"DIAG-{diagnostic_index}",
                        "message": (
                            "Synthetic diagnostic entry used to benchmark repeated "
                            "validation output with evidence references."
                        ),
                        "severity": ["debug", "info", "warning", "error"][
                            diagnostic_index % 4
                        ],
                    }
                )

        suites.append(
            {
                "id": suite_id,
                "name": f"validation_suite_{suite_index}",
                "profile": ["smoke", "workspace", "governance", "release"][
                    suite_index % 4
                ],
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "warnings": warnings,
            }
        )

    return {
        "document_type": "large-validation-report",
        "version": "1.0.0",
        "generated": True,
        "multiplier": multiplier,
        "purpose": "Stress-test large validation reports with evidence records.",
        "suites": suites,
        "cases": cases,
        "evidence": evidence,
        "diagnostics": diagnostics,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate large canonical JSON fixtures for SDIF benchmarks.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("examples/golden"),
        help="Directory where generated golden fixtures will be written.",
    )
    parser.add_argument(
        "--multiplier",
        type=int,
        default=1,
        help="Size multiplier for generated benchmark fixtures.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.multiplier < 1:
        raise SystemExit("--multiplier must be greater than or equal to 1")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    fixtures = {
        "large-plan": make_large_plan(args.multiplier),
        "large-registry": make_large_registry(args.multiplier),
        "large-schema-catalog": make_large_schema_catalog(args.multiplier),
        "large-validation-report": make_large_validation_report(args.multiplier),
    }

    for name, data in fixtures.items():
        write_fixture(args.output_dir, name, data)

    print(f"Generated {len(fixtures)} large benchmark fixtures in {args.output_dir}")
    print(f"Multiplier: {args.multiplier}")


if __name__ == "__main__":
    main()