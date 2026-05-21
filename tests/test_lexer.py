from sdif.parser.lexer import TokenKind, lex_lines


def test_lexer_classifies_directives_blocks_tables_fields_comments_and_indent():
    tokens = lex_lines("""
# comment
@sdif 1.0
kind Plan
owner:
  id team.platform
items[id,status]:
  R1\tdone
""")

    assert [(t.kind, t.value, t.indent) for t in tokens] == [
        (TokenKind.COMMENT, "# comment", 0),
        (TokenKind.DIRECTIVE, "@sdif 1.0", 0),
        (TokenKind.FIELD, "kind Plan", 0),
        (TokenKind.BLOCK, "owner:", 0),
        (TokenKind.FIELD, "id team.platform", 2),
        (TokenKind.TABLE_HEADER, "items[id,status]:", 0),
        (TokenKind.TABLE_ROW, "R1\tdone", 2),
    ]
