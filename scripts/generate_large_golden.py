#!/usr/bin/env python3
"""Generate large canonical JSON golden files for SDIF benchmarks.

The generated files are deterministic and intentionally JSON-first. SDIF, YAML,
TOON, and other formats must be derived from these canonical JSON sources during
benchmark execution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def write_fixture(output_dir: Path, name: str, data: dict[str, Any]) -> None:
    fixture_dir = output_dir / name
    fixture_dir.mkdir(parents=True, exist_ok=True)

    target = fixture_dir / "equivalent.json"
    target.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def make_large_plan(multiplier: int) -> dict[str, Any]:
    phases = []

    for phase_index in range(1, 8 * multiplier + 1):
        milestones = []

        for milestone_index in range(1, 8 + 1):
            tasks = []

            for task_index in range(1, 12 + 1):
                task_id = f"PLN-{phase_index:02d}-{milestone_index:02d}-{task_index:03d}"

                tasks.append(
                    {
                        "id": task_id,
                        "title": f"Implement governed planning task {task_id}",
                        "status": ["pending", "in_progress", "blocked", "done"][
                            (phase_index + milestone_index + task_index) % 4
                        ],
                        "owner": f"team-{(task_index % 5) + 1}",
                        "priority": ["P0", "P1", "P2", "P3"][task_index % 4],
                        "estimate_days": (task_index % 9) + 1,
                        "dependencies": [
                            f"PLN-{max(1, phase_index - 1):02d}-{milestone_index:02d}-{max(1, task_index - 1):03d}",
                            f"ARCH-{phase_index:02d}-{milestone_index:02d}",
                        ],
                        "acceptance_criteria": [
                            "The change is covered by deterministic tests.",
                            "The implementation preserves existing public contracts.",
                            "The benchmark output is reproducible from canonical JSON.",
                            "The generated SDIF output can be parsed without semantic loss.",
                        ],
                        "risk": {
                            "level": ["low", "medium", "high"][task_index % 3],
                            "description": (
                                "Potential drift between generated benchmark data and "
                                "hand-maintained fixtures if canonical JSON is bypassed."
                            ),
                            "mitigation": "Keep JSON as the only semantic source of truth.",
                        },
                    }
                )

            milestones.append(
                {
                    "id": f"MS-{phase_index:02d}-{milestone_index:02d}",
                    "title": f"Milestone {milestone_index} for phase {phase_index}",
                    "objective": (
                        "Validate that large operational planning documents remain compact, "
                        "readable, and lossless when converted to SDIF."
                    ),
                    "tasks": tasks,
                }
            )

        phases.append(
            {
                "id": f"PHASE-{phase_index:02d}",
                "title": f"Large benchmark phase {phase_index}",
                "summary": (
                    "This phase models a realistic multi-team implementation plan with "
                    "dependencies, risk tracking, acceptance criteria, and status metadata."
                ),
                "milestones": milestones,
            }
        )

    return {
        "document_type": "large-plan",
        "version": "1.0.0",
        "metadata": {
            "generated": True,
            "multiplier": multiplier,
            "purpose": "Stress-test token efficiency for large planning documents.",
        },
        "phases": phases,
    }


def make_large_registry(multiplier: int) -> dict[str, Any]:
    modules = []

    for module_index in range(1, 18 * multiplier + 1):
        components = []

        for component_index in range(1, 10 + 1):
            capabilities = []

            for capability_index in range(1, 8 + 1):
                capabilities.append(
                    {
                        "id": f"CAP-{module_index:02d}-{component_index:02d}-{capability_index:02d}",
                        "name": f"capability_{module_index}_{component_index}_{capability_index}",
                        "kind": ["read", "write", "execute", "govern"][capability_index % 4],
                        "authority_required": capability_index % 3 == 0,
                        "stability": ["experimental", "stable", "deprecated"][
                            capability_index % 3
                        ],
                        "inputs": [
                            "subject_id",
                            "trace_id",
                            "authority_context",
                            "payload",
                        ],
                        "outputs": [
                            "decision",
                            "evidence_ref",
                            "diagnostics",
                        ],
                    }
                )

            components.append(
                {
                    "id": f"CMP-{module_index:02d}-{component_index:02d}",
                    "name": f"component_{module_index}_{component_index}",
                    "boundary": ["kernel", "runtime", "adapter", "observability"][
                        component_index % 4
                    ],
                    "description": (
                        "Synthetic registry component used to benchmark repeated "
                        "structured metadata with nested capability declarations."
                    ),
                    "capabilities": capabilities,
                }
            )

        modules.append(
            {
                "id": f"MOD-{module_index:02d}",
                "name": f"module_{module_index}",
                "namespace": f"benchmark.module_{module_index}",
                "components": components,
            }
        )

    return {
        "document_type": "large-registry",
        "version": "1.0.0",
        "metadata": {
            "generated": True,
            "multiplier": multiplier,
            "purpose": "Stress-test compact representation of registries and capabilities.",
        },
        "modules": modules,
    }


def make_large_schema_catalog(multiplier: int) -> dict[str, Any]:
    entities = []

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
        fields = []

        for field_index in range(1, 28 + 1):
            field_type = field_types[field_index % len(field_types)]

            fields.append(
                {
                    "name": f"field_{field_index:02d}",
                    "label": f"Field {field_index}",
                    "type": field_type,
                    "required": field_index % 4 != 0,
                    "unique": field_index in {1, 2},
                    "default": None if field_index % 5 else f"default-{field_index}",
                    "description": (
                        "Synthetic schema field with validation, UI metadata, "
                        "visibility rules, and indexing hints."
                    ),
                    "validation": {
                        "min": 0 if field_type in {"integer", "decimal", "money"} else None,
                        "max": 100000 if field_type in {"integer", "decimal", "money"} else None,
                        "pattern": "^[a-zA-Z0-9_-]+$" if field_type == "string" else None,
                    },
                    "ui": {
                        "widget": widgets[field_index % len(widgets)],
                        "group": f"group_{(field_index % 6) + 1}",
                        "visible": field_index % 7 != 0,
                        "readonly": field_index % 11 == 0,
                    },
                }
            )

        relations = [
            {
                "name": "owner",
                "type": "belongsTo",
                "target": "user",
                "required": True,
                "on_delete": "restrict",
            },
            {
                "name": "children",
                "type": "hasMany",
                "target": f"entity_{max(1, entity_index - 1):03d}",
                "required": False,
                "on_delete": "cascade",
            },
            {
                "name": "audit_entries",
                "type": "hasMany",
                "target": "audit_entry",
                "required": False,
                "on_delete": "restrict",
            },
        ]

        rules = [
            {
                "id": f"RULE-{entity_index:03d}-{rule_index:02d}",
                "name": f"rule_{rule_index}",
                "when": f"field_{rule_index:02d} != null",
                "then": "record_validation_evidence",
                "severity": ["info", "warning", "error"][rule_index % 3],
            }
            for rule_index in range(1, 7)
        ]

        entities.append(
            {
                "name": f"entity_{entity_index:03d}",
                "title": f"Entity {entity_index}",
                "description": (
                    "Large generated entity definition used to validate compactness "
                    "for schema-heavy documents with many repeated field definitions."
                ),
                "fields": fields,
                "relations": relations,
                "rules": rules,
                "permissions": {
                    "create": ["admin", "operator"],
                    "read": ["admin", "operator", "viewer"],
                    "update": ["admin", "operator"],
                    "delete": ["admin"],
                },
            }
        )

    return {
        "document_type": "large-schema-catalog",
        "version": "1.0.0",
        "metadata": {
            "generated": True,
            "multiplier": multiplier,
            "purpose": "Stress-test schema-heavy JSON structures against SDIF encoding.",
        },
        "entities": entities,
    }


def make_large_validation_report(multiplier: int) -> dict[str, Any]:
    suites = []

    for suite_index in range(1, 14 * multiplier + 1):
        cases = []

        for case_index in range(1, 40 + 1):
            case_id = f"CASE-{suite_index:02d}-{case_index:03d}"

            cases.append(
                {
                    "id": case_id,
                    "name": f"validation_case_{suite_index}_{case_index}",
                    "status": ["passed", "failed", "skipped", "warning"][
                        (suite_index + case_index) % 4
                    ],
                    "duration_ms": 15 + ((suite_index * case_index) % 850),
                    "assertions": 3 + (case_index % 9),
                    "evidence": {
                        "trace_id": f"trace-{suite_index:02d}-{case_index:03d}",
                        "artifact": f"reports/validation/{suite_index:02d}/{case_id}.json",
                        "sha256": f"{suite_index:02d}{case_index:03d}" * 12,
                    },
                    "diagnostics": [
                        {
                            "code": f"DIAG-{diagnostic_index}",
                            "message": (
                                "Synthetic diagnostic entry used to benchmark repeated "
                                "validation output with evidence references."
                            ),
                            "severity": ["debug", "info", "warning", "error"][
                                diagnostic_index % 4
                            ],
                        }
                        for diagnostic_index in range(1, 5)
                    ],
                }
            )

        suites.append(
            {
                "id": f"SUITE-{suite_index:02d}",
                "name": f"validation_suite_{suite_index}",
                "profile": ["smoke", "workspace", "governance", "release"][
                    suite_index % 4
                ],
                "summary": {
                    "passed": sum(1 for case in cases if case["status"] == "passed"),
                    "failed": sum(1 for case in cases if case["status"] == "failed"),
                    "skipped": sum(1 for case in cases if case["status"] == "skipped"),
                    "warnings": sum(1 for case in cases if case["status"] == "warning"),
                },
                "cases": cases,
            }
        )

    return {
        "document_type": "large-validation-report",
        "version": "1.0.0",
        "metadata": {
            "generated": True,
            "multiplier": multiplier,
            "purpose": "Stress-test large validation reports with nested evidence records.",
        },
        "suites": suites,
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