"""Shared format generators and corpus writing for all benchmark tracks.

Import this module after `infra` to ensure the SDIF library path is set up.
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape

import yaml  # type: ignore[import-untyped]

import infra  # noqa: F401 — ensures REPO_ROOT/src is on sys.path before sdif imports

from sdif.ai import ai_view  # noqa: E402
from sdif.json import json_data_to_sdif  # noqa: E402

FORMAT_FILE_NAMES: dict[str, str] = {
    "CSV Bundle": "csv_bundle.csv",
    "JSON Compact": "json_compact.json",
    "JSON Pretty": "json_pretty.json",
    "SDIF": "sdif.sdif",
    "SDIF AI": "sdif_ai.sdif.ai",
    "TOON": "toon.toon",
    "XML": "xml.xml",
    "YAML": "yaml.yaml",
}

AI_ALIASES: dict[str, str] = {
    "authority": "auth",
    "description": "desc",
    "evidence": "ev",
    "lifecycle": "life",
    "priority": "pri",
    "schema": "sch",
    "status": "st",
    "version": "v",
}


def json_compact(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def json_pretty(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def yaml_generated(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def xml_generated(data: dict[str, Any]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    _emit_xml_value("document", data, lines, indent=0)
    return "\n".join(lines) + "\n"


def csv_bundle_generated(data: dict[str, Any]) -> str:
    sections: list[str] = []
    scalar_rows: list[tuple[str, object]] = []
    for key, value in data.items():
        if _is_uniform_object_array(value):
            sections.append(_csv_section(key, value))  # type: ignore[arg-type]
        else:
            scalar_rows.append((key, value))
    if scalar_rows:
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(["key", "value"])
        for key, value in scalar_rows:
            writer.writerow([key, _csv_cell(value)])
        sections.insert(0, "# fields\n" + output.getvalue().rstrip("\n"))
    return "\n\n".join(sections).rstrip() + "\n"


def compact_ai_projection(sdif_text: str) -> str:
    from sdif.core.policy import Policy

    policy = Policy(
        max_document_size=10_000_000,
        max_table_row_count=100_000,
        max_string_length=1_000_000,
    )
    candidates = [
        ai_view(sdif_text, {}, include_header=False, policy=policy),
        ai_view(sdif_text, AI_ALIASES, include_header=True, policy=policy),
    ]
    return min(candidates, key=lambda c: len(c.encode("utf-8")))


def toon_from_cli(data: dict[str, Any]) -> str | None:
    if os.environ.get("SDIF_BENCHMARK_TOON") == "0":
        return None
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "source.json"
        output = Path(tmp) / "source.toon"
        source.write_text(json_compact(data), encoding="utf-8")
        toon = shutil.which("toon")
        if toon is not None:
            rendered = _run_command([toon, str(source), "-o", str(output)], output)
            if rendered is not None:
                return rendered
        npx = shutil.which("npx")
        if npx is None:
            infra.verbose_warning("TOON skipped: neither `toon` nor `npx` was found.")
            return None
        return _run_command(
            [npx, "-y", "@toon-format/cli", str(source), "-o", str(output)],
            output,
            timeout_seconds=60,
        )


def build_formats(data: dict[str, Any]) -> list[tuple[str, str]]:
    sdif_text = json_data_to_sdif(data, include_header=True)
    formats: list[tuple[str, str]] = [
        ("JSON Compact", json_compact(data)),
        ("JSON Pretty", json_pretty(data)),
        ("YAML", yaml_generated(data)),
        ("XML", xml_generated(data)),
        ("CSV Bundle", csv_bundle_generated(data)),
        ("SDIF", sdif_text),
        ("SDIF AI", compact_ai_projection(sdif_text)),
    ]
    toon_text = toon_from_cli(data)
    if toon_text is not None:
        formats.append(("TOON", toon_text))
    return formats


def build_formats_dict(data: dict[str, Any]) -> dict[str, str]:
    return dict(build_formats(data))


def corpus_file_name(format_name: str) -> str:
    try:
        return FORMAT_FILE_NAMES[format_name]
    except KeyError as exc:
        raise ValueError(f"Unsupported benchmark format for corpus output: {format_name}") from exc


def write_document_corpus(
    run_dir: Path, document_name: str, format_texts: dict[str, str]
) -> None:
    document_dir = run_dir / infra.CORPUS_DIR_NAME / document_name
    document_dir.mkdir(parents=True, exist_ok=True)
    for format_name, text in format_texts.items():
        file_name = FORMAT_FILE_NAMES.get(format_name)
        if file_name:
            (document_dir / file_name).write_text(text, encoding="utf-8")


def _run_command(
    command: list[str], output: Path, timeout_seconds: int = 30
) -> str | None:
    try:
        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        infra.verbose_warning(f"Command failed to start: {' '.join(command)} | {exc}")
        return None
    if completed.returncode != 0:
        infra.verbose_warning(
            f"Command returned non-zero exit status: {' '.join(command)} "
            f"| stderr={completed.stderr.strip()}"
        )
        return None
    if output.exists():
        return output.read_text(encoding="utf-8")
    if completed.stdout.strip():
        return completed.stdout
    return None


def _emit_xml_value(name: str, value: object, lines: list[str], indent: int) -> None:
    prefix = " " * indent
    tag = _xml_tag(name)
    if isinstance(value, dict):
        lines.append(f"{prefix}<{tag}>")
        for key, child in value.items():
            _emit_xml_value(str(key), child, lines, indent + 2)
        lines.append(f"{prefix}</{tag}>")
    elif isinstance(value, list):
        lines.append(f"{prefix}<{tag}>")
        for item in value:
            _emit_xml_value("item", item, lines, indent + 2)
        lines.append(f"{prefix}</{tag}>")
    else:
        lines.append(f"{prefix}<{tag}>{xml_escape(_scalar_text(value))}</{tag}>")


def _xml_tag(name: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", name):
        return name
    return "item"


def _scalar_text(value: object) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def _is_uniform_object_array(value: object) -> bool:
    if not isinstance(value, list) or not value:
        return False
    if not all(isinstance(item, dict) for item in value):
        return False
    columns = list(value[0].keys())
    if not columns:
        return False
    expected = set(columns)
    return all(set(item.keys()) == expected for item in value)


def _csv_section(name: str, rows: list[dict[str, object]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    columns = list(rows[0].keys())
    writer.writerow(columns)
    for row in rows:
        writer.writerow([_csv_cell(row[column]) for column in columns])
    return f"# table:{name}\n{output.getvalue().rstrip(chr(10))}"


def _csv_cell(value: object) -> str:
    if isinstance(value, str | int | float) or value is None or isinstance(value, bool):
        return _scalar_text(value)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
