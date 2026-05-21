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
      $.block_header,
      $.field,
      $.comment
    ),

    directive: $ => seq('@', $.identifier, repeat1($.atom)),
    field: $ => seq($.identifier, repeat1($.atom)),
    block_header: $ => seq($.identifier, ':'),
    table: $ => seq($.identifier, '[', commaSep1($.identifier), ']', ':'),
    comment: _ => token(seq('#', /.*/)),
    identifier: _ => /[A-Za-z_][A-Za-z0-9_-]*/,
    atom: _ => /[^\s#]+/,
  }
});

function commaSep1(rule) {
  return seq(rule, repeat(seq(',', rule)));
}
