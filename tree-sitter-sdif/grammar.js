// MVP Tree-sitter grammar scaffold for SDIF syntax highlighting.
// The normative parser is the Python parser under src/sdif/parser.
module.exports = grammar({
  name: 'sdif',

  extras: $ => [/\s/, $.comment],

  rules: {
    source_file: $ => repeat($._statement),

    _statement: $ => choice(
      $.directive,
      $.table,
      $.relation_block,
      $.rules_block,
      $.narrative_block,
      $.block_header,
      $.field,
      $.comment
    ),

    directive: $ => seq('@', $.identifier, repeat1($.atom)),
    field: $ => seq($.identifier, repeat1($.atom)),
    block_header: $ => seq($.identifier, ':'),
    table: $ => seq($.table_header, repeat($.table_row)),
    table_header: $ => seq($.identifier, '[', commaSep1($.identifier), ']', ':'),
    table_row: _ => token(seq(/[ \t]+/, /[^\n]+/)),
    relation_block: $ => seq('rel:', repeat($.relation_row)),
    relation_row: _ => token(seq(/[ \t]+/, /[^\n]+/)),
    rules_block: $ => seq('rules:', repeat($.rule_row)),
    rule_row: _ => token(seq(/[ \t]+/, /[^\n]+/)),
    narrative_block: $ => seq($.identifier, '"""', repeat($.narrative_text), '"""'),
    narrative_text: _ => token(/[^"]+/),
    comment: _ => token(seq('#', /.*/)),
    identifier: _ => /[A-Za-z_][A-Za-z0-9_-]*/,
    atom: _ => /[^\s#]+/,
  }
});

function commaSep1(rule) {
  return seq(rule, repeat(seq(',', rule)));
}
