import pytest
from sdif import Policy, PolicyError, parse_text, parse_file


def test_policy_document_size():
    # 9 bytes limit
    policy = Policy(max_document_size=9)
    with pytest.raises(PolicyError) as excinfo:
        parse_text("@sdif 1.0\n", policy=policy)
    assert excinfo.value.code == "SDIF_POLICY_DOCUMENT_SIZE"


def test_policy_nesting_depth():
    policy = Policy(max_nesting_depth=2)
    # depth 1 is fine
    parse_text("@sdif 1.0\nparent:\n  child:\n    field value", policy=policy)

    # depth 3 is blocked
    with pytest.raises(PolicyError) as excinfo:
        parse_text(
            "@sdif 1.0\nparent:\n  child:\n    grandchild:\n      field value", policy=policy
        )
    assert excinfo.value.code == "SDIF_POLICY_NESTING_DEPTH"


def test_policy_string_length():
    policy = Policy(max_string_length=5)
    # field value too long
    with pytest.raises(PolicyError) as excinfo:
        parse_text("@sdif 1.0\nkey longvalue", policy=policy)
    assert excinfo.value.code == "SDIF_POLICY_STRING_LENGTH"


def test_policy_table_row_count():
    policy = Policy(max_table_row_count=2)
    # 3 rows, too long
    text = "@sdif 1.0\nmytable[col]:\n  val1\n  val2\n  val3\n"
    with pytest.raises(PolicyError) as excinfo:
        parse_text(text, policy=policy)
    assert excinfo.value.code == "SDIF_POLICY_TABLE_ROW_COUNT"


def test_policy_includes_disabled_by_default(tmp_path):
    f1 = tmp_path / "f1.sdif"
    f2 = tmp_path / "f2.sdif"
    f1.write_text("@sdif 1.0\n@include f2.sdif\n", encoding="utf-8")
    f2.write_text("@sdif 1.0\nkey val\n", encoding="utf-8")

    # default policy (allow_includes=False)
    with pytest.raises(PolicyError) as excinfo:
        parse_file(f1)
    assert excinfo.value.code == "SDIF_POLICY_INCLUDE"


def test_policy_includes_path_allowlist(tmp_path):
    f1 = tmp_path / "f1.sdif"
    f2 = tmp_path / "f2.sdif"
    f1.write_text("@sdif 1.0\n@include f2.sdif\n", encoding="utf-8")
    f2.write_text("@sdif 1.0\nkey val\n", encoding="utf-8")

    # allow_includes=True but empty allowlist
    policy = Policy(allow_includes=True, allowed_include_paths=frozenset())
    with pytest.raises(PolicyError) as excinfo:
        parse_file(f1, policy=policy)
    assert excinfo.value.code == "SDIF_POLICY_INCLUDE_PATH"

    # allowlist contains parent directory
    policy_ok = Policy(allow_includes=True, allowed_include_paths=frozenset([tmp_path]))
    doc = parse_file(f1, policy=policy_ok)
    assert doc.fields["key"].value == "val"


def test_policy_include_depth(tmp_path):
    # depth limit = 2
    # f1 -> f2 -> f3 -> f4
    f1 = tmp_path / "f1.sdif"
    f2 = tmp_path / "f2.sdif"
    f3 = tmp_path / "f3.sdif"
    f4 = tmp_path / "f4.sdif"
    f1.write_text("@sdif 1.0\n@include f2.sdif\n", encoding="utf-8")
    f2.write_text("@sdif 1.0\n@include f3.sdif\n", encoding="utf-8")
    f3.write_text("@sdif 1.0\n@include f4.sdif\n", encoding="utf-8")
    f4.write_text("@sdif 1.0\nkey val\n", encoding="utf-8")

    policy = Policy(
        allow_includes=True, allowed_include_paths=frozenset([tmp_path]), max_include_depth=2
    )
    with pytest.raises(PolicyError) as excinfo:
        parse_file(f1, policy=policy)
    assert excinfo.value.code == "SDIF_POLICY_INCLUDE_DEPTH"


def test_policy_include_cycle(tmp_path):
    f1 = tmp_path / "f1.sdif"
    f2 = tmp_path / "f2.sdif"
    f1.write_text("@sdif 1.0\n@include f2.sdif\n", encoding="utf-8")
    f2.write_text("@sdif 1.0\n@include f1.sdif\n", encoding="utf-8")

    policy = Policy(allow_includes=True, allowed_include_paths=frozenset([tmp_path]))
    with pytest.raises(PolicyError) as excinfo:
        parse_file(f1, policy=policy)
    assert excinfo.value.code == "SDIF_POLICY_INCLUDE_CYCLE"


def test_policy_expanded_bytes(tmp_path):
    f1 = tmp_path / "f1.sdif"
    f2 = tmp_path / "f2.sdif"
    f1.write_text("@sdif 1.0\n@include f2.sdif\n", encoding="utf-8")
    f2.write_text("@sdif 1.0\nkey val\n", encoding="utf-8")

    # f1 size ~25 bytes, f2 size ~18 bytes, total ~43 bytes.
    # set limit to 30 bytes
    policy = Policy(
        allow_includes=True, allowed_include_paths=frozenset([tmp_path]), max_expanded_bytes=30
    )
    with pytest.raises(PolicyError) as excinfo:
        parse_file(f1, policy=policy)
    assert excinfo.value.code == "SDIF_POLICY_EXPANDED_BYTES"


def test_policy_remote_include(tmp_path):
    f1 = tmp_path / "f1.sdif"
    f1.write_text('@sdif 1.0\n@include "https://example.com/other.sdif"\n', encoding="utf-8")

    policy = Policy(allow_includes=True, allowed_include_paths=frozenset([tmp_path]))
    with pytest.raises(PolicyError) as excinfo:
        parse_file(f1, policy=policy)
    assert excinfo.value.code == "SDIF_POLICY_REMOTE_INCLUDE"


def test_policy_alias_reserved():
    # Reserved term as alias name
    with pytest.raises(PolicyError) as excinfo:
        parse_text("@sdif.ai 1.0\nalias[include=myval]\n")
    assert excinfo.value.code == "SDIF_POLICY_ALIAS_RESERVED"

    # Reserved term as canonical name
    with pytest.raises(PolicyError) as excinfo:
        parse_text("@sdif.ai 1.0\nalias[myval=include]\n")
    assert excinfo.value.code == "SDIF_POLICY_ALIAS_RESERVED"


def test_policy_alias_collision():
    with pytest.raises(PolicyError) as excinfo:
        parse_text("@sdif.ai 1.0\nalias[st=status,st=other]\n")
    assert excinfo.value.code == "SDIF_POLICY_ALIAS_COLLISION"


def test_policy_alias_expansion():
    from sdif.ai.aliases import sdif_from_ai

    # alias expansion limit set to 2
    policy = Policy(max_alias_expansion=2)

    ai_doc = (
        "@sdif.ai 1.0\nalias[st=status,pr=priority,lif=lifecycle]\nst open\npr P0\nlif Active\n"
    )

    # 3 expansions (st -> status, pr -> priority, lif -> lifecycle)
    # This exceeds limit = 2
    with pytest.raises(PolicyError) as excinfo:
        sdif_from_ai(ai_doc, policy=policy)
    assert excinfo.value.code == "SDIF_POLICY_ALIAS_EXPANSION"
