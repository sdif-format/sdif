#!/usr/bin/env python3
"""Generate deterministic benchmark-oriented golden JSON fixtures.

The fixture shapes are intentionally SDIF-representable: large repeated records
are normalized into top-level scalar tables instead of arbitrary nested arrays in
row cells. ``equivalent.json`` remains the semantic source; run
``scripts/generate_golden_fixtures.py`` afterwards to derive SDIF artifacts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

JsonObject = dict[str, Any]

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOLDEN_DIR = ROOT / "examples" / "golden"
DEFAULT_GITHUB_OPENAPI = DEFAULT_GOLDEN_DIR / "github.openapi" / "github.openapi.json"


def cell_text(value: object, *, limit: int | None = None) -> str:
    text = str(value)
    text = " ".join(text.split())
    if limit is not None:
        return text[:limit]
    return text


def write_fixture(output_dir: Path, name: str, data: JsonObject) -> None:
    fixture_dir = output_dir / name
    fixture_dir.mkdir(parents=True, exist_ok=True)
    (fixture_dir / "equivalent.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _meta(document_type: str, size_class: str, profile: str) -> JsonObject:
    return {
        "document_type": document_type,
        "version": "1.0.0",
        "generated": True,
        "benchmark_size_class": size_class,
        "benchmark_profile": profile,
    }


def make_small_invoice() -> JsonObject:
    lines = [
        {
            "id": f"LINE-{index:03d}",
            "sku": f"SKU-{1000 + index}",
            "description": f"Implementation service line {index}",
            "quantity": 1 + (index % 4),
            "unit_price": 95 + (index * 7),
            "tax_code": ["standard", "reduced", "exempt"][index % 3],
        }
        for index in range(1, 18)
    ]
    payments = [
        {"id": "PAY-001", "method": "card", "amount": 1240, "status": "captured"},
        {"id": "PAY-002", "method": "transfer", "amount": 880, "status": "pending"},
    ]
    return {
        **_meta("small-invoice", "small", "tabular-finance"),
        "invoice_id": "INV-2026-0001",
        "currency": "EUR",
        "customer_id": "CUST-042",
        "issued_on": "2026-05-21",
        "lines": lines,
        "payments": payments,
    }


def make_small_incident() -> JsonObject:
    events = [
        {
            "id": f"EVT-{index:03d}",
            "minute": index * 3,
            "actor": ["monitor", "sre", "support", "deploy-bot"][index % 4],
            "severity": ["info", "warning", "critical"][index % 3],
            "message": f"Incident timeline event {index} with bounded narrative context.",
        }
        for index in range(1, 24)
    ]
    actions = [
        {
            "id": f"ACT-{index:03d}",
            "event_id": f"EVT-{index + 3:03d}",
            "owner": f"team-{(index % 4) + 1}",
            "status": ["open", "done", "verified"][index % 3],
        }
        for index in range(1, 10)
    ]
    return {
        **_meta("small-incident", "small", "mixed-narrative-tables"),
        "incident_id": "INC-2026-0521",
        "service": "payments-api",
        "impact": "partial-degradation",
        "summary": "Synthetic incident report with timeline and remediation actions.",
        "events": events,
        "actions": actions,
    }


def make_small_api_catalog() -> JsonObject:
    endpoints = [
        {
            "id": f"END-{index:03d}",
            "method": ["GET", "POST", "PATCH", "DELETE"][index % 4],
            "path": f"/v1/resources/{index}",
            "tag": ["accounts", "billing", "search", "admin"][index % 4],
            "auth": ["none", "user", "admin"][index % 3],
        }
        for index in range(1, 34)
    ]
    return {
        **_meta("small-api-catalog", "small", "api-endpoints"),
        "api_name": "compact-service-api",
        "base_url": "https://api.example.test",
        "endpoints": endpoints,
    }


def make_medium_invoice_batch() -> JsonObject:
    invoices: list[JsonObject] = []
    line_items: list[JsonObject] = []
    adjustments: list[JsonObject] = []
    for invoice_index in range(1, 140):
        invoice_id = f"INV-2026-{invoice_index:05d}"
        invoices.append(
            {
                "id": invoice_id,
                "customer_id": f"CUST-{(invoice_index % 37) + 1:04d}",
                "currency": ["EUR", "USD", "GBP"][invoice_index % 3],
                "status": ["draft", "sent", "paid", "void"][invoice_index % 4],
                "issued_on": f"2026-05-{(invoice_index % 28) + 1:02d}",
            }
        )
        for line_index in range(1, 6):
            line_items.append(
                {
                    "invoice_id": invoice_id,
                    "line_no": line_index,
                    "sku": f"SKU-{invoice_index:04d}-{line_index:02d}",
                    "quantity": 1 + ((invoice_index + line_index) % 8),
                    "unit_price": 19 + ((invoice_index * line_index) % 300),
                    "description": "Recurring subscription and services benchmark line item.",
                }
            )
        adjustments.append(
            {
                "invoice_id": invoice_id,
                "kind": ["discount", "credit", "rounding"][invoice_index % 3],
                "amount": (invoice_index % 15) - 7,
            }
        )
    return {
        **_meta("medium-invoice-batch", "medium", "relational-tabular"),
        "purpose": "Medium-size finance workload with parent-child tables.",
        "invoices": invoices,
        "line_items": line_items,
        "adjustments": adjustments,
    }


def make_medium_observability_run() -> JsonObject:
    services: list[JsonObject] = []
    spans: list[JsonObject] = []
    metrics: list[JsonObject] = []
    logs: list[JsonObject] = []
    for service_index in range(1, 22):
        service_id = f"SVC-{service_index:03d}"
        services.append(
            {
                "id": service_id,
                "name": f"service-{service_index}",
                "runtime": ["python", "rust", "node", "go"][service_index % 4],
                "owner": f"team-{(service_index % 6) + 1}",
            }
        )
        for span_index in range(1, 24):
            span_id = f"SPAN-{service_index:03d}-{span_index:03d}"
            spans.append(
                {
                    "id": span_id,
                    "service_id": service_id,
                    "operation": f"operation_{span_index % 9}",
                    "duration_ms": 3 + ((service_index * span_index) % 950),
                    "status": ["ok", "error", "timeout"][span_index % 3],
                }
            )
            metrics.append(
                {
                    "span_id": span_id,
                    "name": ["latency", "cpu", "allocations", "queue_depth"][span_index % 4],
                    "value": service_index * span_index,
                    "unit": ["ms", "percent", "count", "items"][span_index % 4],
                }
            )
            if span_index % 2 == 0:
                logs.append(
                    {
                        "span_id": span_id,
                        "level": ["debug", "info", "warning", "error"][span_index % 4],
                        "message": "Bounded observability log message for benchmark token analysis.",
                    }
                )
    return {
        **_meta("medium-observability-run", "medium", "observability"),
        "run_id": "OBS-2026-05-21",
        "services": services,
        "spans": spans,
        "metrics": metrics,
        "logs": logs,
    }


def make_medium_policy_catalog() -> JsonObject:
    policies: list[JsonObject] = []
    rules: list[JsonObject] = []
    bindings: list[JsonObject] = []
    for policy_index in range(1, 95):
        policy_id = f"POL-{policy_index:04d}"
        policies.append(
            {
                "id": policy_id,
                "name": f"policy_{policy_index:04d}",
                "domain": ["security", "billing", "privacy", "operations"][policy_index % 4],
                "mode": ["enforce", "audit", "disabled"][policy_index % 3],
            }
        )
        for rule_index in range(1, 7):
            rules.append(
                {
                    "id": f"RULE-{policy_index:04d}-{rule_index:02d}",
                    "policy_id": policy_id,
                    "effect": ["allow", "deny", "review"][rule_index % 3],
                    "condition": f"resource.tag_{rule_index} == principal.scope_{rule_index}",
                    "severity": ["low", "medium", "high"][rule_index % 3],
                }
            )
        for role in ("admin", "operator", "viewer"):
            bindings.append(
                {"policy_id": policy_id, "role": role, "scope": f"scope-{policy_index % 12}"}
            )
    return {
        **_meta("medium-policy-catalog", "medium", "rules-policy"),
        "policies": policies,
        "rules": rules,
        "bindings": bindings,
    }


def make_medium_product_catalog() -> JsonObject:
    products: list[JsonObject] = []
    prices: list[JsonObject] = []
    attributes: list[JsonObject] = []
    inventory: list[JsonObject] = []
    for product_index in range(1, 180):
        product_id = f"PROD-{product_index:05d}"
        products.append(
            {
                "id": product_id,
                "name": f"Benchmark Product {product_index}",
                "category": ["hardware", "software", "service", "bundle"][product_index % 4],
                "status": ["active", "draft", "archived"][product_index % 3],
            }
        )
        for currency in ("EUR", "USD", "GBP"):
            prices.append(
                {
                    "product_id": product_id,
                    "currency": currency,
                    "amount": 10 + ((product_index * len(currency)) % 500),
                }
            )
        for attr_index in range(1, 5):
            attributes.append(
                {
                    "product_id": product_id,
                    "name": f"attribute_{attr_index}",
                    "value": f"value_{product_index}_{attr_index}",
                }
            )
        inventory.append(
            {
                "product_id": product_id,
                "warehouse": f"WH-{(product_index % 9) + 1}",
                "available": product_index * 3,
                "reserved": product_index % 17,
            }
        )
    return {
        **_meta("medium-product-catalog", "medium", "catalog-commerce"),
        "products": products,
        "prices": prices,
        "attributes": attributes,
        "inventory": inventory,
    }


def make_large_audit_trail() -> JsonObject:
    actors: list[JsonObject] = []
    sessions: list[JsonObject] = []
    events: list[JsonObject] = []
    evidence: list[JsonObject] = []
    for actor_index in range(1, 70):
        actor_id = f"ACTOR-{actor_index:04d}"
        actors.append(
            {
                "id": actor_id,
                "kind": ["user", "service", "integration"][actor_index % 3],
                "name": f"actor_{actor_index:04d}",
                "risk_tier": ["low", "medium", "high"][actor_index % 3],
            }
        )
        for session_index in range(1, 6):
            session_id = f"SESS-{actor_index:04d}-{session_index:02d}"
            sessions.append(
                {
                    "id": session_id,
                    "actor_id": actor_id,
                    "started_at": f"2026-05-{(session_index % 28) + 1:02d}T{session_index:02d}:00:00Z",
                    "source_ip": f"192.0.2.{(actor_index + session_index) % 255}",
                }
            )
            for event_index in range(1, 16):
                event_id = f"AUD-{actor_index:04d}-{session_index:02d}-{event_index:03d}"
                events.append(
                    {
                        "id": event_id,
                        "session_id": session_id,
                        "action": ["read", "write", "delete", "approve", "export"][event_index % 5],
                        "resource": f"resource/{actor_index}/{session_index}/{event_index}",
                        "decision": ["allow", "deny", "review"][event_index % 3],
                        "reason": "Synthetic audit event with stable evidence reference.",
                    }
                )
                evidence.append(
                    {
                        "event_id": event_id,
                        "artifact": f"audit/{actor_index:04d}/{session_index:02d}/{event_index:03d}.json",
                        "sha256": f"{actor_index:04d}{session_index:02d}{event_index:03d}" * 7,
                    }
                )
    return {
        **_meta("large-audit-trail", "large", "security-audit"),
        "actors": actors,
        "sessions": sessions,
        "events": events,
        "evidence": evidence,
    }


def make_large_support_export() -> JsonObject:
    tickets: list[JsonObject] = []
    messages: list[JsonObject] = []
    labels: list[JsonObject] = []
    sla_events: list[JsonObject] = []
    for ticket_index in range(1, 520):
        ticket_id = f"TCK-{ticket_index:06d}"
        tickets.append(
            {
                "id": ticket_id,
                "requester": f"user-{ticket_index % 130:04d}",
                "status": ["new", "open", "pending", "solved", "closed"][ticket_index % 5],
                "priority": ["low", "normal", "high", "urgent"][ticket_index % 4],
                "subject": f"Benchmark support request {ticket_index}",
            }
        )
        for message_index in range(1, 6):
            messages.append(
                {
                    "ticket_id": ticket_id,
                    "message_no": message_index,
                    "author": ["requester", "agent", "system"][message_index % 3],
                    "body": "Synthetic support message with enough text to model conversational exports.",
                    "public": message_index % 4 != 0,
                }
            )
        for label_index in range(1, 4):
            labels.append(
                {"ticket_id": ticket_id, "label": f"label-{(ticket_index + label_index) % 31}"}
            )
        sla_events.append(
            {
                "ticket_id": ticket_id,
                "policy": f"policy-{ticket_index % 8}",
                "target_minutes": 60 + (ticket_index % 240),
                "breached": ticket_index % 11 == 0,
            }
        )
    return {
        **_meta("large-support-export", "large", "text-heavy-export"),
        "tickets": tickets,
        "messages": messages,
        "labels": labels,
        "sla_events": sla_events,
    }


def make_large_knowledge_graph() -> JsonObject:
    nodes: list[JsonObject] = []
    edges: list[JsonObject] = []
    annotations: list[JsonObject] = []
    for node_index in range(1, 1450):
        node_id = f"NODE-{node_index:05d}"
        nodes.append(
            {
                "id": node_id,
                "kind": ["concept", "service", "document", "person", "dataset"][node_index % 5],
                "label": f"Knowledge graph node {node_index}",
                "community": f"community-{node_index % 24}",
                "weight": (node_index % 100) / 10,
            }
        )
        annotations.append(
            {
                "node_id": node_id,
                "source": f"source-{node_index % 41}",
                "confidence": ["low", "medium", "high"][node_index % 3],
                "note": "Synthetic annotation for graph-oriented benchmark coverage.",
            }
        )
        if node_index > 1:
            edges.append(
                {
                    "source": f"NODE-{node_index - 1:05d}",
                    "target": node_id,
                    "predicate": ["depends_on", "mentions", "owns", "derives_from"][node_index % 4],
                    "strength": (node_index % 17) + 1,
                }
            )
        if node_index > 10 and node_index % 3 == 0:
            edges.append(
                {
                    "source": f"NODE-{node_index - 10:05d}",
                    "target": node_id,
                    "predicate": "cross_links",
                    "strength": (node_index % 9) + 1,
                }
            )
    return {
        **_meta("large-knowledge-graph", "large", "graph-relational"),
        "nodes": nodes,
        "edges": edges,
        "annotations": annotations,
    }


def make_wide_table_survey() -> JsonObject:
    responses: list[JsonObject] = []
    for response_index in range(1, 220):
        row: JsonObject = {
            "id": f"RESP-{response_index:05d}",
            "segment": ["enterprise", "smb", "consumer", "public"][response_index % 4],
            "region": ["emea", "amer", "apac"][response_index % 3],
        }
        for question_index in range(1, 31):
            row[f"q{question_index:02d}"] = (response_index + question_index) % 7
        responses.append(row)
    return {
        **_meta("wide-table-survey", "medium", "wide-table"),
        "responses": responses,
    }


def make_deep_hierarchy_project() -> JsonObject:
    levels: list[JsonObject] = []
    links: list[JsonObject] = []
    requirements: list[JsonObject] = []
    node_no = 0
    previous_level_ids = ["ROOT"]
    levels.append({"id": "ROOT", "parent_id": "", "depth": 0, "title": "Program root"})
    for depth in range(1, 8):
        current: list[str] = []
        fanout = max(2, 8 - depth)
        for parent_id in previous_level_ids:
            for child_index in range(1, fanout + 1):
                node_no += 1
                node_id = f"NODE-D{depth}-{node_no:05d}"
                levels.append(
                    {
                        "id": node_id,
                        "parent_id": parent_id,
                        "depth": depth,
                        "title": f"Project hierarchy node depth {depth} number {node_no}",
                    }
                )
                links.append({"source": parent_id, "target": node_id, "kind": "contains"})
                requirements.append(
                    {
                        "node_id": node_id,
                        "requirement": f"Requirement for {node_id} must remain traceable.",
                        "status": ["draft", "approved", "implemented", "verified"][node_no % 4],
                    }
                )
                current.append(node_id)
        previous_level_ids = current[:120]
    return {
        **_meta("deep-hierarchy-project", "large", "deep-hierarchy"),
        "levels": levels,
        "links": links,
        "requirements": requirements,
    }


def make_github_openapi(source_path: Path = DEFAULT_GITHUB_OPENAPI) -> JsonObject:
    if source_path.exists():
        raw = json.loads(source_path.read_text(encoding="utf-8"))
    else:
        raw = {
            "openapi": "3.0.3",
            "info": {"title": "GitHub v3 REST API", "version": "unknown"},
            "tags": [],
            "servers": [],
            "paths": {},
        }

    tags = [
        {
            "name": cell_text(tag.get("name", "")),
            "description": cell_text(tag.get("description", ""), limit=220),
        }
        for tag in raw.get("tags", [])[:80]
        if isinstance(tag, dict)
    ]
    servers = [
        {
            "url": cell_text(server.get("url", "")),
            "description": cell_text(server.get("description", ""), limit=220),
        }
        for server in raw.get("servers", [])[:12]
        if isinstance(server, dict)
    ]
    operations: list[JsonObject] = []
    parameters: list[JsonObject] = []
    responses: list[JsonObject] = []
    methods = {"get", "put", "post", "delete", "patch", "head", "options", "trace"}

    for path_key, path_item in raw.get("paths", {}).items():
        if len(operations) >= 360:
            break
        if not isinstance(path_item, dict):
            continue
        path_parameters = path_item.get("parameters", [])
        for method, operation in path_item.items():
            if method not in methods or not isinstance(operation, dict):
                continue
            op_id = str(operation.get("operationId") or f"{method}_{len(operations) + 1}")
            tag = ""
            op_tags = operation.get("tags")
            if isinstance(op_tags, list) and op_tags:
                tag = str(op_tags[0])
            operations.append(
                {
                    "operation_id": cell_text(op_id),
                    "method": method.upper(),
                    "path": cell_text(path_key),
                    "tag": cell_text(tag),
                    "summary": cell_text(operation.get("summary", ""), limit=220),
                    "deprecated": bool(operation.get("deprecated", False)),
                }
            )
            combined_params = []
            if isinstance(path_parameters, list):
                combined_params.extend(path_parameters)
            if isinstance(operation.get("parameters"), list):
                combined_params.extend(operation["parameters"])
            for param in combined_params[:10]:
                if not isinstance(param, dict):
                    continue
                schema = param.get("schema") if isinstance(param.get("schema"), dict) else {}
                parameters.append(
                    {
                        "operation_id": cell_text(op_id),
                        "name": cell_text(param.get("name", "")),
                        "location": cell_text(param.get("in", "")),
                        "required": bool(param.get("required", False)),
                        "schema_type": cell_text(schema.get("type", "")),
                    }
                )
            op_responses = operation.get("responses", {})
            if isinstance(op_responses, dict):
                for status, response in list(op_responses.items())[:8]:
                    description = (
                        response.get("description", "") if isinstance(response, dict) else ""
                    )
                    responses.append(
                        {
                            "operation_id": cell_text(op_id),
                            "status": cell_text(status),
                            "description": cell_text(description, limit=220),
                        }
                    )

    info = raw.get("info", {}) if isinstance(raw.get("info"), dict) else {}
    return {
        **_meta("github.openapi", "large", "real-world-openapi-sampled"),
        "source_file": "examples/golden/github.openapi/github.openapi.json",
        "source_openapi": cell_text(raw.get("openapi", "")),
        "title": cell_text(info.get("title", "GitHub v3 REST API")),
        "source_version": cell_text(info.get("version", "")),
        "sampling_policy": "First 360 REST operations normalized into SDIF-representable tables.",
        "tags": tags,
        "servers": servers,
        "operations": operations,
        "parameters": parameters,
        "responses": responses,
    }


def fixture_builders(openapi_path: Path) -> dict[str, JsonObject]:
    return {
        "small-invoice": make_small_invoice(),
        "small-incident": make_small_incident(),
        "small-api-catalog": make_small_api_catalog(),
        "medium-invoice-batch": make_medium_invoice_batch(),
        "medium-observability-run": make_medium_observability_run(),
        "medium-policy-catalog": make_medium_policy_catalog(),
        "medium-product-catalog": make_medium_product_catalog(),
        "wide-table-survey": make_wide_table_survey(),
        "deep-hierarchy-project": make_deep_hierarchy_project(),
        "large-audit-trail": make_large_audit_trail(),
        "large-support-export": make_large_support_export(),
        "large-knowledge-graph": make_large_knowledge_graph(),
        "github.openapi": make_github_openapi(openapi_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate benchmark golden fixture corpus.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_GOLDEN_DIR)
    parser.add_argument("--github-openapi", type=Path, default=DEFAULT_GITHUB_OPENAPI)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    fixtures = fixture_builders(args.github_openapi)
    for name, data in fixtures.items():
        write_fixture(args.output_dir, name, data)

    print(f"Generated {len(fixtures)} benchmark fixtures in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
