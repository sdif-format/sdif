// MVP Tree-sitter grammar for SDIF editor tooling and incremental parsing.
// Keep this tooling grammar aligned with conformance/manifest.sdif.
module.exports = grammar({
  name: 'sdif',

  extras: $ => [/\s/, $.comment],

  rules: {
    source_file: $ => repeat($._statement),

    _statement: $ => choice(
      $.directive,
      $.alias_header,
      $.table,
      $.relation_block,
      $.rules_block,
      $.narrative_block,
      $.block_header,
      $.field,
      $.comment
    ),

    directive: $ => seq('@', $.identifier, repeat1($._value)),
    alias_header: $ => seq('alias', '[', commaSep1($.alias_entry), ']'),
    alias_entry: $ => seq($.identifier, '=', $.identifier),
    field: $ => seq($.identifier, repeat1($._value)),
    block_header: $ => seq($.identifier, ':'),
    table: $ => seq($.table_header, repeat($.table_row)),
    table_header: $ => seq($.identifier, '[', commaSep1($.column), ']', ':'),
    column: $ => seq($.identifier, optional('$')),
    table_row: _ => token(seq(/[ \t]*/, /[^\n]*\t[^\n]*/)),
    relation_block: $ => seq('rel:', repeat($.relation_row)),
    relation_row: _ => token(seq(/[ \t]+/, /[^\n]+/)),
    rules_block: $ => seq('rules:', repeat($.rule_row)),
    rule_row: _ => token(seq(/[ \t]+/, /[^\n]+/)),
    narrative_block: $ => seq($.identifier, '"""', repeat($.narrative_text), '"""'),
    narrative_text: _ => token(/[^"]+/),
    comment: _ => token(seq('#', /.*/)),
    identifier: _ => /[A-Za-z_][A-Za-z0-9_-]*/,
    _value: $ => choice($.string, $.atom),
    string: _ => token(seq('"', repeat(choice(/[^"\\]/, /\\./)), '"')),
    atom: _ => /[^\s#"]+/,
  }
});

function commaSep1(rule) {
  return seq(rule, repeat(seq(',', rule)));
}
