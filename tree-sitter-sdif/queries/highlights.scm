; SDIF highlighting is for editor/agent tooling. The Python parser remains normative.

(directive
  "@" @punctuation.special
  (identifier) @keyword)

(block_header
  (identifier) @type)

(table_header
  (identifier) @type)

(relation_block
  "rel:" @keyword)

(rules_block
  "rules:" @keyword)

(narrative_block
  (identifier) @type
  "\"\"\"" @punctuation.delimiter
  (narrative_text) @string)

(comment) @comment
(atom) @string.special
(table_row) @string
(relation_row) @string
(rule_row) @string
