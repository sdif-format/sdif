#include "tree_sitter/parser.h"

#if defined(__GNUC__) || defined(__clang__)
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#endif

#define LANGUAGE_VERSION 14
#define STATE_COUNT 52
#define LARGE_STATE_COUNT 2
#define SYMBOL_COUNT 43
#define ALIAS_COUNT 0
#define TOKEN_COUNT 19
#define EXTERNAL_TOKEN_COUNT 0
#define FIELD_COUNT 0
#define MAX_ALIAS_SEQUENCE_LENGTH 6
#define PRODUCTION_ID_COUNT 1

enum ts_symbol_identifiers {
  anon_sym_AT = 1,
  anon_sym_alias = 2,
  anon_sym_LBRACK = 3,
  anon_sym_COMMA = 4,
  anon_sym_RBRACK = 5,
  anon_sym_EQ = 6,
  anon_sym_COLON = 7,
  anon_sym_DOLLAR = 8,
  sym_table_row = 9,
  anon_sym_rel_COLON = 10,
  aux_sym_relation_row_token1 = 11,
  anon_sym_rules_COLON = 12,
  anon_sym_DQUOTE_DQUOTE_DQUOTE = 13,
  sym_narrative_text = 14,
  sym_comment = 15,
  sym_identifier = 16,
  sym_string = 17,
  sym_atom = 18,
  sym_source_file = 19,
  sym__statement = 20,
  sym_directive = 21,
  sym_alias_header = 22,
  sym_alias_entry = 23,
  sym_field = 24,
  sym_block_header = 25,
  sym_table = 26,
  sym_table_header = 27,
  sym_column = 28,
  sym_relation_block = 29,
  sym_relation_row = 30,
  sym_rules_block = 31,
  sym_rule_row = 32,
  sym_narrative_block = 33,
  sym__value = 34,
  aux_sym_source_file_repeat1 = 35,
  aux_sym_directive_repeat1 = 36,
  aux_sym_alias_header_repeat1 = 37,
  aux_sym_table_repeat1 = 38,
  aux_sym_table_header_repeat1 = 39,
  aux_sym_relation_block_repeat1 = 40,
  aux_sym_rules_block_repeat1 = 41,
  aux_sym_narrative_block_repeat1 = 42,
};

static const char * const ts_symbol_names[] = {
  [ts_builtin_sym_end] = "end",
  [anon_sym_AT] = "@",
  [anon_sym_alias] = "alias",
  [anon_sym_LBRACK] = "[",
  [anon_sym_COMMA] = ",",
  [anon_sym_RBRACK] = "]",
  [anon_sym_EQ] = "=",
  [anon_sym_COLON] = ":",
  [anon_sym_DOLLAR] = "$",
  [sym_table_row] = "table_row",
  [anon_sym_rel_COLON] = "rel:",
  [aux_sym_relation_row_token1] = "relation_row_token1",
  [anon_sym_rules_COLON] = "rules:",
  [anon_sym_DQUOTE_DQUOTE_DQUOTE] = "\"\"\"",
  [sym_narrative_text] = "narrative_text",
  [sym_comment] = "comment",
  [sym_identifier] = "identifier",
  [sym_string] = "string",
  [sym_atom] = "atom",
  [sym_source_file] = "source_file",
  [sym__statement] = "_statement",
  [sym_directive] = "directive",
  [sym_alias_header] = "alias_header",
  [sym_alias_entry] = "alias_entry",
  [sym_field] = "field",
  [sym_block_header] = "block_header",
  [sym_table] = "table",
  [sym_table_header] = "table_header",
  [sym_column] = "column",
  [sym_relation_block] = "relation_block",
  [sym_relation_row] = "relation_row",
  [sym_rules_block] = "rules_block",
  [sym_rule_row] = "rule_row",
  [sym_narrative_block] = "narrative_block",
  [sym__value] = "_value",
  [aux_sym_source_file_repeat1] = "source_file_repeat1",
  [aux_sym_directive_repeat1] = "directive_repeat1",
  [aux_sym_alias_header_repeat1] = "alias_header_repeat1",
  [aux_sym_table_repeat1] = "table_repeat1",
  [aux_sym_table_header_repeat1] = "table_header_repeat1",
  [aux_sym_relation_block_repeat1] = "relation_block_repeat1",
  [aux_sym_rules_block_repeat1] = "rules_block_repeat1",
  [aux_sym_narrative_block_repeat1] = "narrative_block_repeat1",
};

static const TSSymbol ts_symbol_map[] = {
  [ts_builtin_sym_end] = ts_builtin_sym_end,
  [anon_sym_AT] = anon_sym_AT,
  [anon_sym_alias] = anon_sym_alias,
  [anon_sym_LBRACK] = anon_sym_LBRACK,
  [anon_sym_COMMA] = anon_sym_COMMA,
  [anon_sym_RBRACK] = anon_sym_RBRACK,
  [anon_sym_EQ] = anon_sym_EQ,
  [anon_sym_COLON] = anon_sym_COLON,
  [anon_sym_DOLLAR] = anon_sym_DOLLAR,
  [sym_table_row] = sym_table_row,
  [anon_sym_rel_COLON] = anon_sym_rel_COLON,
  [aux_sym_relation_row_token1] = aux_sym_relation_row_token1,
  [anon_sym_rules_COLON] = anon_sym_rules_COLON,
  [anon_sym_DQUOTE_DQUOTE_DQUOTE] = anon_sym_DQUOTE_DQUOTE_DQUOTE,
  [sym_narrative_text] = sym_narrative_text,
  [sym_comment] = sym_comment,
  [sym_identifier] = sym_identifier,
  [sym_string] = sym_string,
  [sym_atom] = sym_atom,
  [sym_source_file] = sym_source_file,
  [sym__statement] = sym__statement,
  [sym_directive] = sym_directive,
  [sym_alias_header] = sym_alias_header,
  [sym_alias_entry] = sym_alias_entry,
  [sym_field] = sym_field,
  [sym_block_header] = sym_block_header,
  [sym_table] = sym_table,
  [sym_table_header] = sym_table_header,
  [sym_column] = sym_column,
  [sym_relation_block] = sym_relation_block,
  [sym_relation_row] = sym_relation_row,
  [sym_rules_block] = sym_rules_block,
  [sym_rule_row] = sym_rule_row,
  [sym_narrative_block] = sym_narrative_block,
  [sym__value] = sym__value,
  [aux_sym_source_file_repeat1] = aux_sym_source_file_repeat1,
  [aux_sym_directive_repeat1] = aux_sym_directive_repeat1,
  [aux_sym_alias_header_repeat1] = aux_sym_alias_header_repeat1,
  [aux_sym_table_repeat1] = aux_sym_table_repeat1,
  [aux_sym_table_header_repeat1] = aux_sym_table_header_repeat1,
  [aux_sym_relation_block_repeat1] = aux_sym_relation_block_repeat1,
  [aux_sym_rules_block_repeat1] = aux_sym_rules_block_repeat1,
  [aux_sym_narrative_block_repeat1] = aux_sym_narrative_block_repeat1,
};

static const TSSymbolMetadata ts_symbol_metadata[] = {
  [ts_builtin_sym_end] = {
    .visible = false,
    .named = true,
  },
  [anon_sym_AT] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_alias] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_LBRACK] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_COMMA] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_RBRACK] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_EQ] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_COLON] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_DOLLAR] = {
    .visible = true,
    .named = false,
  },
  [sym_table_row] = {
    .visible = true,
    .named = true,
  },
  [anon_sym_rel_COLON] = {
    .visible = true,
    .named = false,
  },
  [aux_sym_relation_row_token1] = {
    .visible = false,
    .named = false,
  },
  [anon_sym_rules_COLON] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_DQUOTE_DQUOTE_DQUOTE] = {
    .visible = true,
    .named = false,
  },
  [sym_narrative_text] = {
    .visible = true,
    .named = true,
  },
  [sym_comment] = {
    .visible = true,
    .named = true,
  },
  [sym_identifier] = {
    .visible = true,
    .named = true,
  },
  [sym_string] = {
    .visible = true,
    .named = true,
  },
  [sym_atom] = {
    .visible = true,
    .named = true,
  },
  [sym_source_file] = {
    .visible = true,
    .named = true,
  },
  [sym__statement] = {
    .visible = false,
    .named = true,
  },
  [sym_directive] = {
    .visible = true,
    .named = true,
  },
  [sym_alias_header] = {
    .visible = true,
    .named = true,
  },
  [sym_alias_entry] = {
    .visible = true,
    .named = true,
  },
  [sym_field] = {
    .visible = true,
    .named = true,
  },
  [sym_block_header] = {
    .visible = true,
    .named = true,
  },
  [sym_table] = {
    .visible = true,
    .named = true,
  },
  [sym_table_header] = {
    .visible = true,
    .named = true,
  },
  [sym_column] = {
    .visible = true,
    .named = true,
  },
  [sym_relation_block] = {
    .visible = true,
    .named = true,
  },
  [sym_relation_row] = {
    .visible = true,
    .named = true,
  },
  [sym_rules_block] = {
    .visible = true,
    .named = true,
  },
  [sym_rule_row] = {
    .visible = true,
    .named = true,
  },
  [sym_narrative_block] = {
    .visible = true,
    .named = true,
  },
  [sym__value] = {
    .visible = false,
    .named = true,
  },
  [aux_sym_source_file_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_directive_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_alias_header_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_table_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_table_header_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_relation_block_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_rules_block_repeat1] = {
    .visible = false,
    .named = false,
  },
  [aux_sym_narrative_block_repeat1] = {
    .visible = false,
    .named = false,
  },
};

static const TSSymbol ts_alias_sequences[PRODUCTION_ID_COUNT][MAX_ALIAS_SEQUENCE_LENGTH] = {
  [0] = {0},
};

static const uint16_t ts_non_terminal_alias_map[] = {
  0,
};

static const TSStateId ts_primary_state_ids[STATE_COUNT] = {
  [0] = 0,
  [1] = 1,
  [2] = 2,
  [3] = 3,
  [4] = 4,
  [5] = 5,
  [6] = 6,
  [7] = 7,
  [8] = 8,
  [9] = 9,
  [10] = 10,
  [11] = 11,
  [12] = 12,
  [13] = 13,
  [14] = 14,
  [15] = 15,
  [16] = 16,
  [17] = 17,
  [18] = 18,
  [19] = 19,
  [20] = 20,
  [21] = 21,
  [22] = 22,
  [23] = 23,
  [24] = 24,
  [25] = 25,
  [26] = 26,
  [27] = 27,
  [28] = 28,
  [29] = 29,
  [30] = 30,
  [31] = 31,
  [32] = 32,
  [33] = 33,
  [34] = 34,
  [35] = 35,
  [36] = 36,
  [37] = 37,
  [38] = 38,
  [39] = 39,
  [40] = 40,
  [41] = 41,
  [42] = 42,
  [43] = 43,
  [44] = 44,
  [45] = 45,
  [46] = 46,
  [47] = 47,
  [48] = 48,
  [49] = 49,
  [50] = 50,
  [51] = 51,
};

static bool ts_lex(TSLexer *lexer, TSStateId state) {
  START_LEXER();
  eof = lexer->eof(lexer);
  switch (state) {
    case 0:
      if (eof) ADVANCE(17);
      ADVANCE_MAP(
        '"', 5,
        '#', 79,
        '$', 35,
        ',', 30,
        ':', 33,
        '=', 32,
        '@', 18,
        '[', 28,
        ']', 31,
        'a', 104,
        'r', 98,
      );
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(0);
      if (('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 1:
      if (lookahead == '\t') ADVANCE(36);
      if (lookahead == '\n') SKIP(1);
      if (lookahead == ' ') ADVANCE(1);
      if (lookahead == '#') ADVANCE(78);
      if (lookahead == '@') ADVANCE(19);
      if (lookahead == 'a') ADVANCE(86);
      if (lookahead == 'r') ADVANCE(83);
      if ((0x0b <= lookahead && lookahead <= '\r')) ADVANCE(1);
      if (('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0) ADVANCE(2);
      END_STATE();
    case 2:
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 3:
      if (lookahead == '\n') SKIP(11);
      if (lookahead == '#') ADVANCE(68);
      if (lookahead == '@') ADVANCE(22);
      if (lookahead == 'a') ADVANCE(62);
      if (lookahead == 'r') ADVANCE(59);
      if (lookahead == '\t' ||
          lookahead == ' ') ADVANCE(55);
      if ((0x0b <= lookahead && lookahead <= '\r')) ADVANCE(55);
      if (('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0) ADVANCE(68);
      END_STATE();
    case 4:
      if (lookahead == '"') ADVANCE(5);
      if (lookahead == '#') ADVANCE(79);
      if (lookahead == ':') ADVANCE(34);
      if (lookahead == '[') ADVANCE(29);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(4);
      if (lookahead != 0) ADVANCE(118);
      END_STATE();
    case 5:
      if (lookahead == '"') ADVANCE(117);
      if (lookahead == '\\') ADVANCE(13);
      if (lookahead != 0) ADVANCE(7);
      END_STATE();
    case 6:
      if (lookahead == '"') ADVANCE(74);
      END_STATE();
    case 7:
      if (lookahead == '"') ADVANCE(116);
      if (lookahead == '\\') ADVANCE(13);
      if (lookahead != 0) ADVANCE(7);
      END_STATE();
    case 8:
      if (lookahead == '"') ADVANCE(10);
      if (lookahead == '#') ADVANCE(75);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(76);
      if (lookahead != 0) ADVANCE(77);
      END_STATE();
    case 9:
      if (lookahead == '"') ADVANCE(7);
      if (lookahead == '#') ADVANCE(79);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(9);
      if (lookahead != 0) ADVANCE(118);
      END_STATE();
    case 10:
      if (lookahead == '"') ADVANCE(6);
      END_STATE();
    case 11:
      if (lookahead == '#') ADVANCE(79);
      if (lookahead == '@') ADVANCE(18);
      if (lookahead == 'a') ADVANCE(104);
      if (lookahead == 'r') ADVANCE(98);
      if (lookahead == '\t' ||
          lookahead == ' ') ADVANCE(3);
      if (('\n' <= lookahead && lookahead <= '\r')) SKIP(11);
      if (('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 12:
      if (lookahead == '#') ADVANCE(79);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(12);
      if (('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 13:
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(7);
      END_STATE();
    case 14:
      if (eof) ADVANCE(17);
      if (lookahead == '\t') ADVANCE(36);
      if (lookahead == '\n') SKIP(14);
      if (lookahead == ' ') ADVANCE(1);
      if (lookahead == '#') ADVANCE(78);
      if (lookahead == '@') ADVANCE(19);
      if (lookahead == 'a') ADVANCE(86);
      if (lookahead == 'r') ADVANCE(83);
      if ((0x0b <= lookahead && lookahead <= '\r')) ADVANCE(1);
      if (('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0) ADVANCE(2);
      END_STATE();
    case 15:
      if (eof) ADVANCE(17);
      if (lookahead == '"') ADVANCE(7);
      if (lookahead == '#') ADVANCE(79);
      if (lookahead == '@') ADVANCE(21);
      if (lookahead == 'a') ADVANCE(107);
      if (lookahead == 'r') ADVANCE(100);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') SKIP(15);
      if (('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0) ADVANCE(118);
      END_STATE();
    case 16:
      if (eof) ADVANCE(17);
      if (lookahead == '#') ADVANCE(79);
      if (lookahead == '@') ADVANCE(18);
      if (lookahead == 'a') ADVANCE(104);
      if (lookahead == 'r') ADVANCE(98);
      if (lookahead == '\t' ||
          lookahead == ' ') ADVANCE(3);
      if (('\n' <= lookahead && lookahead <= '\r')) SKIP(16);
      if (('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 17:
      ACCEPT_TOKEN(ts_builtin_sym_end);
      END_STATE();
    case 18:
      ACCEPT_TOKEN(anon_sym_AT);
      END_STATE();
    case 19:
      ACCEPT_TOKEN(anon_sym_AT);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 20:
      ACCEPT_TOKEN(anon_sym_AT);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 21:
      ACCEPT_TOKEN(anon_sym_AT);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 22:
      ACCEPT_TOKEN(anon_sym_AT);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 23:
      ACCEPT_TOKEN(anon_sym_alias);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 24:
      ACCEPT_TOKEN(anon_sym_alias);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 25:
      ACCEPT_TOKEN(anon_sym_alias);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 26:
      ACCEPT_TOKEN(anon_sym_alias);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 27:
      ACCEPT_TOKEN(anon_sym_alias);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 28:
      ACCEPT_TOKEN(anon_sym_LBRACK);
      END_STATE();
    case 29:
      ACCEPT_TOKEN(anon_sym_LBRACK);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 30:
      ACCEPT_TOKEN(anon_sym_COMMA);
      END_STATE();
    case 31:
      ACCEPT_TOKEN(anon_sym_RBRACK);
      END_STATE();
    case 32:
      ACCEPT_TOKEN(anon_sym_EQ);
      END_STATE();
    case 33:
      ACCEPT_TOKEN(anon_sym_COLON);
      END_STATE();
    case 34:
      ACCEPT_TOKEN(anon_sym_COLON);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 35:
      ACCEPT_TOKEN(anon_sym_DOLLAR);
      END_STATE();
    case 36:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(36);
      if (lookahead == ' ') ADVANCE(36);
      if (lookahead == '#') ADVANCE(49);
      if (lookahead == '@') ADVANCE(20);
      if (lookahead == 'a') ADVANCE(43);
      if (lookahead == 'r') ADVANCE(40);
      if ((0x0b <= lookahead && lookahead <= '\r')) ADVANCE(36);
      if (('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead)) ADVANCE(49);
      END_STATE();
    case 37:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == ':') ADVANCE(52);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 38:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == ':') ADVANCE(71);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 39:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'a') ADVANCE(47);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 40:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'e') ADVANCE(44);
      if (lookahead == 'u') ADVANCE(45);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 41:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'e') ADVANCE(46);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 42:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'i') ADVANCE(39);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 43:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'l') ADVANCE(42);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 44:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'l') ADVANCE(37);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 45:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'l') ADVANCE(41);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 46:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 's') ADVANCE(38);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 47:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 's') ADVANCE(24);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 48:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(48);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 49:
      ACCEPT_TOKEN(sym_table_row);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 50:
      ACCEPT_TOKEN(anon_sym_rel_COLON);
      END_STATE();
    case 51:
      ACCEPT_TOKEN(anon_sym_rel_COLON);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 52:
      ACCEPT_TOKEN(anon_sym_rel_COLON);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 53:
      ACCEPT_TOKEN(anon_sym_rel_COLON);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 54:
      ACCEPT_TOKEN(anon_sym_rel_COLON);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 55:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead == '#') ADVANCE(68);
      if (lookahead == '@') ADVANCE(22);
      if (lookahead == 'a') ADVANCE(62);
      if (lookahead == 'r') ADVANCE(59);
      if (lookahead == '\t' ||
          lookahead == ' ') ADVANCE(55);
      if ((0x0b <= lookahead && lookahead <= '\r')) ADVANCE(55);
      if (('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead)) ADVANCE(68);
      END_STATE();
    case 56:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead == ':') ADVANCE(54);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 57:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead == ':') ADVANCE(73);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 58:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead == 'a') ADVANCE(65);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 59:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead == 'e') ADVANCE(63);
      if (lookahead == 'u') ADVANCE(64);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 60:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead == 'e') ADVANCE(66);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 61:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead == 'i') ADVANCE(58);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 62:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead == 'l') ADVANCE(61);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 63:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead == 'l') ADVANCE(56);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 64:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead == 'l') ADVANCE(60);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 65:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead == 's') ADVANCE(27);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 66:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead == 's') ADVANCE(57);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 67:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(67);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 68:
      ACCEPT_TOKEN(aux_sym_relation_row_token1);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 69:
      ACCEPT_TOKEN(anon_sym_rules_COLON);
      END_STATE();
    case 70:
      ACCEPT_TOKEN(anon_sym_rules_COLON);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 71:
      ACCEPT_TOKEN(anon_sym_rules_COLON);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(49);
      END_STATE();
    case 72:
      ACCEPT_TOKEN(anon_sym_rules_COLON);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 73:
      ACCEPT_TOKEN(anon_sym_rules_COLON);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(68);
      END_STATE();
    case 74:
      ACCEPT_TOKEN(anon_sym_DQUOTE_DQUOTE_DQUOTE);
      END_STATE();
    case 75:
      ACCEPT_TOKEN(sym_narrative_text);
      if (lookahead == '\n') ADVANCE(77);
      if (lookahead == '"') ADVANCE(79);
      if (lookahead != 0) ADVANCE(75);
      END_STATE();
    case 76:
      ACCEPT_TOKEN(sym_narrative_text);
      if (lookahead == '#') ADVANCE(75);
      if (('\t' <= lookahead && lookahead <= '\r') ||
          lookahead == ' ') ADVANCE(76);
      if (lookahead != 0 &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(77);
      END_STATE();
    case 77:
      ACCEPT_TOKEN(sym_narrative_text);
      if (lookahead != 0 &&
          lookahead != '"') ADVANCE(77);
      END_STATE();
    case 78:
      ACCEPT_TOKEN(sym_comment);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(78);
      END_STATE();
    case 79:
      ACCEPT_TOKEN(sym_comment);
      if (lookahead != 0 &&
          lookahead != '\n') ADVANCE(79);
      END_STATE();
    case 80:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == ':') ADVANCE(51);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 81:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == ':') ADVANCE(70);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 82:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'a') ADVANCE(89);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 83:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'e') ADVANCE(87);
      if (lookahead == 'u') ADVANCE(88);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 84:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'e') ADVANCE(90);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 85:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'i') ADVANCE(82);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 86:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'l') ADVANCE(85);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 87:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'l') ADVANCE(80);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 88:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 'l') ADVANCE(84);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 89:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 's') ADVANCE(23);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 90:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == 's') ADVANCE(81);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 91:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '\t') ADVANCE(49);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(91);
      if (lookahead != 0 &&
          lookahead != '\t' &&
          lookahead != '\n') ADVANCE(2);
      END_STATE();
    case 92:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == ':') ADVANCE(50);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 93:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == ':') ADVANCE(69);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 94:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == ':') ADVANCE(53);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 95:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == ':') ADVANCE(72);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 96:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'a') ADVANCE(110);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 97:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'a') ADVANCE(111);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('b' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 98:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'e') ADVANCE(105);
      if (lookahead == 'u') ADVANCE(106);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 99:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'e') ADVANCE(112);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 100:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'e') ADVANCE(108);
      if (lookahead == 'u') ADVANCE(109);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 101:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'e') ADVANCE(113);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 102:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'i') ADVANCE(96);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 103:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'i') ADVANCE(97);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 104:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'l') ADVANCE(102);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 105:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'l') ADVANCE(92);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 106:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'l') ADVANCE(99);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 107:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'l') ADVANCE(103);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 108:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'l') ADVANCE(94);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 109:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 'l') ADVANCE(101);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 110:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 's') ADVANCE(25);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 111:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 's') ADVANCE(26);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 112:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 's') ADVANCE(93);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 113:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == 's') ADVANCE(95);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 114:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(114);
      END_STATE();
    case 115:
      ACCEPT_TOKEN(sym_identifier);
      if (lookahead == '-' ||
          ('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(115);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    case 116:
      ACCEPT_TOKEN(sym_string);
      END_STATE();
    case 117:
      ACCEPT_TOKEN(sym_string);
      if (lookahead == '"') ADVANCE(74);
      END_STATE();
    case 118:
      ACCEPT_TOKEN(sym_atom);
      if (lookahead != 0 &&
          (lookahead < '\t' || '\r' < lookahead) &&
          lookahead != ' ' &&
          lookahead != '"' &&
          lookahead != '#') ADVANCE(118);
      END_STATE();
    default:
      return false;
  }
}

static const TSLexMode ts_lex_modes[STATE_COUNT] = {
  [0] = {.lex_state = 0},
  [1] = {.lex_state = 0},
  [2] = {.lex_state = 0},
  [3] = {.lex_state = 0},
  [4] = {.lex_state = 15},
  [5] = {.lex_state = 15},
  [6] = {.lex_state = 15},
  [7] = {.lex_state = 16},
  [8] = {.lex_state = 16},
  [9] = {.lex_state = 16},
  [10] = {.lex_state = 16},
  [11] = {.lex_state = 16},
  [12] = {.lex_state = 16},
  [13] = {.lex_state = 14},
  [14] = {.lex_state = 14},
  [15] = {.lex_state = 14},
  [16] = {.lex_state = 16},
  [17] = {.lex_state = 4},
  [18] = {.lex_state = 14},
  [19] = {.lex_state = 14},
  [20] = {.lex_state = 16},
  [21] = {.lex_state = 0},
  [22] = {.lex_state = 0},
  [23] = {.lex_state = 0},
  [24] = {.lex_state = 0},
  [25] = {.lex_state = 0},
  [26] = {.lex_state = 9},
  [27] = {.lex_state = 0},
  [28] = {.lex_state = 0},
  [29] = {.lex_state = 0},
  [30] = {.lex_state = 8},
  [31] = {.lex_state = 0},
  [32] = {.lex_state = 8},
  [33] = {.lex_state = 0},
  [34] = {.lex_state = 0},
  [35] = {.lex_state = 8},
  [36] = {.lex_state = 0},
  [37] = {.lex_state = 0},
  [38] = {.lex_state = 12},
  [39] = {.lex_state = 12},
  [40] = {.lex_state = 0},
  [41] = {.lex_state = 12},
  [42] = {.lex_state = 0},
  [43] = {.lex_state = 0},
  [44] = {.lex_state = 12},
  [45] = {.lex_state = 12},
  [46] = {.lex_state = 0},
  [47] = {.lex_state = 0},
  [48] = {.lex_state = 0},
  [49] = {.lex_state = 0},
  [50] = {.lex_state = 0},
  [51] = {.lex_state = 12},
};

static const uint16_t ts_parse_table[LARGE_STATE_COUNT][SYMBOL_COUNT] = {
  [0] = {
    [ts_builtin_sym_end] = ACTIONS(1),
    [anon_sym_AT] = ACTIONS(1),
    [anon_sym_alias] = ACTIONS(1),
    [anon_sym_LBRACK] = ACTIONS(1),
    [anon_sym_COMMA] = ACTIONS(1),
    [anon_sym_RBRACK] = ACTIONS(1),
    [anon_sym_EQ] = ACTIONS(1),
    [anon_sym_COLON] = ACTIONS(1),
    [anon_sym_DOLLAR] = ACTIONS(1),
    [anon_sym_rel_COLON] = ACTIONS(1),
    [anon_sym_rules_COLON] = ACTIONS(1),
    [anon_sym_DQUOTE_DQUOTE_DQUOTE] = ACTIONS(1),
    [sym_comment] = ACTIONS(3),
    [sym_identifier] = ACTIONS(1),
    [sym_string] = ACTIONS(1),
  },
  [1] = {
    [sym_source_file] = STATE(48),
    [sym__statement] = STATE(2),
    [sym_directive] = STATE(2),
    [sym_alias_header] = STATE(2),
    [sym_field] = STATE(2),
    [sym_block_header] = STATE(2),
    [sym_table] = STATE(2),
    [sym_table_header] = STATE(14),
    [sym_relation_block] = STATE(2),
    [sym_rules_block] = STATE(2),
    [sym_narrative_block] = STATE(2),
    [aux_sym_source_file_repeat1] = STATE(2),
    [ts_builtin_sym_end] = ACTIONS(5),
    [anon_sym_AT] = ACTIONS(7),
    [anon_sym_alias] = ACTIONS(9),
    [anon_sym_rel_COLON] = ACTIONS(11),
    [anon_sym_rules_COLON] = ACTIONS(13),
    [sym_comment] = ACTIONS(15),
    [sym_identifier] = ACTIONS(17),
  },
};

static const uint16_t ts_small_parse_table[] = {
  [0] = 9,
    ACTIONS(7), 1,
      anon_sym_AT,
    ACTIONS(9), 1,
      anon_sym_alias,
    ACTIONS(11), 1,
      anon_sym_rel_COLON,
    ACTIONS(13), 1,
      anon_sym_rules_COLON,
    ACTIONS(17), 1,
      sym_identifier,
    ACTIONS(19), 1,
      ts_builtin_sym_end,
    ACTIONS(21), 1,
      sym_comment,
    STATE(14), 1,
      sym_table_header,
    STATE(3), 10,
      sym__statement,
      sym_directive,
      sym_alias_header,
      sym_field,
      sym_block_header,
      sym_table,
      sym_relation_block,
      sym_rules_block,
      sym_narrative_block,
      aux_sym_source_file_repeat1,
  [37] = 9,
    ACTIONS(23), 1,
      ts_builtin_sym_end,
    ACTIONS(25), 1,
      anon_sym_AT,
    ACTIONS(28), 1,
      anon_sym_alias,
    ACTIONS(31), 1,
      anon_sym_rel_COLON,
    ACTIONS(34), 1,
      anon_sym_rules_COLON,
    ACTIONS(37), 1,
      sym_comment,
    ACTIONS(40), 1,
      sym_identifier,
    STATE(14), 1,
      sym_table_header,
    STATE(3), 10,
      sym__statement,
      sym_directive,
      sym_alias_header,
      sym_field,
      sym_block_header,
      sym_table,
      sym_relation_block,
      sym_rules_block,
      sym_narrative_block,
      aux_sym_source_file_repeat1,
  [74] = 5,
    ACTIONS(47), 1,
      sym_string,
    ACTIONS(49), 1,
      sym_atom,
    ACTIONS(43), 2,
      ts_builtin_sym_end,
      sym_comment,
    STATE(5), 2,
      sym__value,
      aux_sym_directive_repeat1,
    ACTIONS(45), 5,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_identifier,
  [96] = 5,
    ACTIONS(55), 1,
      sym_string,
    ACTIONS(58), 1,
      sym_atom,
    ACTIONS(51), 2,
      ts_builtin_sym_end,
      sym_comment,
    STATE(5), 2,
      sym__value,
      aux_sym_directive_repeat1,
    ACTIONS(53), 5,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_identifier,
  [118] = 5,
    ACTIONS(47), 1,
      sym_string,
    ACTIONS(49), 1,
      sym_atom,
    ACTIONS(61), 2,
      ts_builtin_sym_end,
      sym_comment,
    STATE(5), 2,
      sym__value,
      aux_sym_directive_repeat1,
    ACTIONS(63), 5,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_identifier,
  [140] = 4,
    ACTIONS(65), 1,
      ts_builtin_sym_end,
    ACTIONS(69), 1,
      aux_sym_relation_row_token1,
    STATE(11), 2,
      sym_relation_row,
      aux_sym_relation_block_repeat1,
    ACTIONS(67), 6,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
      sym_identifier,
  [159] = 4,
    ACTIONS(71), 1,
      ts_builtin_sym_end,
    ACTIONS(75), 1,
      aux_sym_relation_row_token1,
    STATE(12), 2,
      sym_rule_row,
      aux_sym_rules_block_repeat1,
    ACTIONS(73), 6,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
      sym_identifier,
  [178] = 4,
    ACTIONS(77), 1,
      ts_builtin_sym_end,
    ACTIONS(81), 1,
      aux_sym_relation_row_token1,
    STATE(9), 2,
      sym_rule_row,
      aux_sym_rules_block_repeat1,
    ACTIONS(79), 6,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
      sym_identifier,
  [197] = 4,
    ACTIONS(84), 1,
      ts_builtin_sym_end,
    ACTIONS(88), 1,
      aux_sym_relation_row_token1,
    STATE(10), 2,
      sym_relation_row,
      aux_sym_relation_block_repeat1,
    ACTIONS(86), 6,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
      sym_identifier,
  [216] = 4,
    ACTIONS(69), 1,
      aux_sym_relation_row_token1,
    ACTIONS(91), 1,
      ts_builtin_sym_end,
    STATE(10), 2,
      sym_relation_row,
      aux_sym_relation_block_repeat1,
    ACTIONS(93), 6,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
      sym_identifier,
  [235] = 4,
    ACTIONS(75), 1,
      aux_sym_relation_row_token1,
    ACTIONS(95), 1,
      ts_builtin_sym_end,
    STATE(9), 2,
      sym_rule_row,
      aux_sym_rules_block_repeat1,
    ACTIONS(97), 6,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
      sym_identifier,
  [254] = 4,
    ACTIONS(99), 1,
      ts_builtin_sym_end,
    ACTIONS(103), 1,
      sym_table_row,
    STATE(13), 1,
      aux_sym_table_repeat1,
    ACTIONS(101), 6,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
      sym_identifier,
  [272] = 4,
    ACTIONS(106), 1,
      ts_builtin_sym_end,
    ACTIONS(110), 1,
      sym_table_row,
    STATE(15), 1,
      aux_sym_table_repeat1,
    ACTIONS(108), 6,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
      sym_identifier,
  [290] = 4,
    ACTIONS(112), 1,
      ts_builtin_sym_end,
    ACTIONS(116), 1,
      sym_table_row,
    STATE(13), 1,
      aux_sym_table_repeat1,
    ACTIONS(114), 6,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
      sym_identifier,
  [308] = 2,
    ACTIONS(118), 1,
      ts_builtin_sym_end,
    ACTIONS(120), 7,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      aux_sym_relation_row_token1,
      anon_sym_rules_COLON,
      sym_comment,
      sym_identifier,
  [321] = 6,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(122), 1,
      anon_sym_LBRACK,
    ACTIONS(124), 1,
      anon_sym_COLON,
    ACTIONS(126), 1,
      anon_sym_DQUOTE_DQUOTE_DQUOTE,
    ACTIONS(128), 2,
      sym_string,
      sym_atom,
    STATE(4), 2,
      sym__value,
      aux_sym_directive_repeat1,
  [342] = 2,
    ACTIONS(130), 1,
      ts_builtin_sym_end,
    ACTIONS(132), 7,
      anon_sym_AT,
      anon_sym_alias,
      sym_table_row,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
      sym_identifier,
  [355] = 2,
    ACTIONS(134), 1,
      ts_builtin_sym_end,
    ACTIONS(136), 7,
      anon_sym_AT,
      anon_sym_alias,
      sym_table_row,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
      sym_identifier,
  [368] = 2,
    ACTIONS(138), 1,
      ts_builtin_sym_end,
    ACTIONS(140), 7,
      anon_sym_AT,
      anon_sym_alias,
      anon_sym_rel_COLON,
      aux_sym_relation_row_token1,
      anon_sym_rules_COLON,
      sym_comment,
      sym_identifier,
  [381] = 2,
    ACTIONS(144), 2,
      anon_sym_alias,
      sym_identifier,
    ACTIONS(142), 5,
      ts_builtin_sym_end,
      anon_sym_AT,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
  [393] = 2,
    ACTIONS(148), 2,
      anon_sym_alias,
      sym_identifier,
    ACTIONS(146), 5,
      ts_builtin_sym_end,
      anon_sym_AT,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
  [405] = 2,
    ACTIONS(152), 2,
      anon_sym_alias,
      sym_identifier,
    ACTIONS(150), 5,
      ts_builtin_sym_end,
      anon_sym_AT,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
  [417] = 2,
    ACTIONS(156), 2,
      anon_sym_alias,
      sym_identifier,
    ACTIONS(154), 5,
      ts_builtin_sym_end,
      anon_sym_AT,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
  [429] = 2,
    ACTIONS(160), 2,
      anon_sym_alias,
      sym_identifier,
    ACTIONS(158), 5,
      ts_builtin_sym_end,
      anon_sym_AT,
      anon_sym_rel_COLON,
      anon_sym_rules_COLON,
      sym_comment,
  [441] = 3,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(162), 2,
      sym_string,
      sym_atom,
    STATE(6), 2,
      sym__value,
      aux_sym_directive_repeat1,
  [453] = 4,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(164), 1,
      anon_sym_COMMA,
    ACTIONS(167), 1,
      anon_sym_RBRACK,
    STATE(27), 1,
      aux_sym_table_header_repeat1,
  [466] = 3,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(171), 1,
      anon_sym_DOLLAR,
    ACTIONS(169), 2,
      anon_sym_COMMA,
      anon_sym_RBRACK,
  [477] = 4,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(173), 1,
      anon_sym_COMMA,
    ACTIONS(175), 1,
      anon_sym_RBRACK,
    STATE(34), 1,
      aux_sym_table_header_repeat1,
  [490] = 4,
    ACTIONS(177), 1,
      anon_sym_DQUOTE_DQUOTE_DQUOTE,
    ACTIONS(179), 1,
      sym_narrative_text,
    ACTIONS(181), 1,
      sym_comment,
    STATE(35), 1,
      aux_sym_narrative_block_repeat1,
  [503] = 4,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(183), 1,
      anon_sym_COMMA,
    ACTIONS(185), 1,
      anon_sym_RBRACK,
    STATE(33), 1,
      aux_sym_alias_header_repeat1,
  [516] = 4,
    ACTIONS(181), 1,
      sym_comment,
    ACTIONS(187), 1,
      anon_sym_DQUOTE_DQUOTE_DQUOTE,
    ACTIONS(189), 1,
      sym_narrative_text,
    STATE(30), 1,
      aux_sym_narrative_block_repeat1,
  [529] = 4,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(183), 1,
      anon_sym_COMMA,
    ACTIONS(191), 1,
      anon_sym_RBRACK,
    STATE(36), 1,
      aux_sym_alias_header_repeat1,
  [542] = 4,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(173), 1,
      anon_sym_COMMA,
    ACTIONS(193), 1,
      anon_sym_RBRACK,
    STATE(27), 1,
      aux_sym_table_header_repeat1,
  [555] = 4,
    ACTIONS(181), 1,
      sym_comment,
    ACTIONS(195), 1,
      anon_sym_DQUOTE_DQUOTE_DQUOTE,
    ACTIONS(197), 1,
      sym_narrative_text,
    STATE(35), 1,
      aux_sym_narrative_block_repeat1,
  [568] = 4,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(200), 1,
      anon_sym_COMMA,
    ACTIONS(203), 1,
      anon_sym_RBRACK,
    STATE(36), 1,
      aux_sym_alias_header_repeat1,
  [581] = 2,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(167), 2,
      anon_sym_COMMA,
      anon_sym_RBRACK,
  [589] = 3,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(205), 1,
      sym_identifier,
    STATE(29), 1,
      sym_column,
  [599] = 3,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(207), 1,
      sym_identifier,
    STATE(43), 1,
      sym_alias_entry,
  [609] = 2,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(209), 2,
      anon_sym_COMMA,
      anon_sym_RBRACK,
  [617] = 3,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(205), 1,
      sym_identifier,
    STATE(37), 1,
      sym_column,
  [627] = 2,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(211), 2,
      anon_sym_COMMA,
      anon_sym_RBRACK,
  [635] = 2,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(203), 2,
      anon_sym_COMMA,
      anon_sym_RBRACK,
  [643] = 3,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(207), 1,
      sym_identifier,
    STATE(31), 1,
      sym_alias_entry,
  [653] = 2,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(213), 1,
      sym_identifier,
  [660] = 2,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(215), 1,
      anon_sym_COLON,
  [667] = 2,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(217), 1,
      anon_sym_EQ,
  [674] = 2,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(219), 1,
      ts_builtin_sym_end,
  [681] = 2,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(221), 1,
      anon_sym_COLON,
  [688] = 2,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(223), 1,
      anon_sym_LBRACK,
  [695] = 2,
    ACTIONS(3), 1,
      sym_comment,
    ACTIONS(225), 1,
      sym_identifier,
};

static const uint32_t ts_small_parse_table_map[] = {
  [SMALL_STATE(2)] = 0,
  [SMALL_STATE(3)] = 37,
  [SMALL_STATE(4)] = 74,
  [SMALL_STATE(5)] = 96,
  [SMALL_STATE(6)] = 118,
  [SMALL_STATE(7)] = 140,
  [SMALL_STATE(8)] = 159,
  [SMALL_STATE(9)] = 178,
  [SMALL_STATE(10)] = 197,
  [SMALL_STATE(11)] = 216,
  [SMALL_STATE(12)] = 235,
  [SMALL_STATE(13)] = 254,
  [SMALL_STATE(14)] = 272,
  [SMALL_STATE(15)] = 290,
  [SMALL_STATE(16)] = 308,
  [SMALL_STATE(17)] = 321,
  [SMALL_STATE(18)] = 342,
  [SMALL_STATE(19)] = 355,
  [SMALL_STATE(20)] = 368,
  [SMALL_STATE(21)] = 381,
  [SMALL_STATE(22)] = 393,
  [SMALL_STATE(23)] = 405,
  [SMALL_STATE(24)] = 417,
  [SMALL_STATE(25)] = 429,
  [SMALL_STATE(26)] = 441,
  [SMALL_STATE(27)] = 453,
  [SMALL_STATE(28)] = 466,
  [SMALL_STATE(29)] = 477,
  [SMALL_STATE(30)] = 490,
  [SMALL_STATE(31)] = 503,
  [SMALL_STATE(32)] = 516,
  [SMALL_STATE(33)] = 529,
  [SMALL_STATE(34)] = 542,
  [SMALL_STATE(35)] = 555,
  [SMALL_STATE(36)] = 568,
  [SMALL_STATE(37)] = 581,
  [SMALL_STATE(38)] = 589,
  [SMALL_STATE(39)] = 599,
  [SMALL_STATE(40)] = 609,
  [SMALL_STATE(41)] = 617,
  [SMALL_STATE(42)] = 627,
  [SMALL_STATE(43)] = 635,
  [SMALL_STATE(44)] = 643,
  [SMALL_STATE(45)] = 653,
  [SMALL_STATE(46)] = 660,
  [SMALL_STATE(47)] = 667,
  [SMALL_STATE(48)] = 674,
  [SMALL_STATE(49)] = 681,
  [SMALL_STATE(50)] = 688,
  [SMALL_STATE(51)] = 695,
};

static const TSParseActionEntry ts_parse_actions[] = {
  [0] = {.entry = {.count = 0, .reusable = false}},
  [1] = {.entry = {.count = 1, .reusable = false}}, RECOVER(),
  [3] = {.entry = {.count = 1, .reusable = true}}, SHIFT_EXTRA(),
  [5] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_source_file, 0, 0, 0),
  [7] = {.entry = {.count = 1, .reusable = true}}, SHIFT(51),
  [9] = {.entry = {.count = 1, .reusable = false}}, SHIFT(50),
  [11] = {.entry = {.count = 1, .reusable = true}}, SHIFT(7),
  [13] = {.entry = {.count = 1, .reusable = true}}, SHIFT(8),
  [15] = {.entry = {.count = 1, .reusable = true}}, SHIFT(2),
  [17] = {.entry = {.count = 1, .reusable = false}}, SHIFT(17),
  [19] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_source_file, 1, 0, 0),
  [21] = {.entry = {.count = 1, .reusable = true}}, SHIFT(3),
  [23] = {.entry = {.count = 1, .reusable = true}}, REDUCE(aux_sym_source_file_repeat1, 2, 0, 0),
  [25] = {.entry = {.count = 2, .reusable = true}}, REDUCE(aux_sym_source_file_repeat1, 2, 0, 0), SHIFT_REPEAT(51),
  [28] = {.entry = {.count = 2, .reusable = false}}, REDUCE(aux_sym_source_file_repeat1, 2, 0, 0), SHIFT_REPEAT(50),
  [31] = {.entry = {.count = 2, .reusable = true}}, REDUCE(aux_sym_source_file_repeat1, 2, 0, 0), SHIFT_REPEAT(7),
  [34] = {.entry = {.count = 2, .reusable = true}}, REDUCE(aux_sym_source_file_repeat1, 2, 0, 0), SHIFT_REPEAT(8),
  [37] = {.entry = {.count = 2, .reusable = true}}, REDUCE(aux_sym_source_file_repeat1, 2, 0, 0), SHIFT_REPEAT(3),
  [40] = {.entry = {.count = 2, .reusable = false}}, REDUCE(aux_sym_source_file_repeat1, 2, 0, 0), SHIFT_REPEAT(17),
  [43] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_field, 2, 0, 0),
  [45] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_field, 2, 0, 0),
  [47] = {.entry = {.count = 1, .reusable = true}}, SHIFT(5),
  [49] = {.entry = {.count = 1, .reusable = false}}, SHIFT(5),
  [51] = {.entry = {.count = 1, .reusable = true}}, REDUCE(aux_sym_directive_repeat1, 2, 0, 0),
  [53] = {.entry = {.count = 1, .reusable = false}}, REDUCE(aux_sym_directive_repeat1, 2, 0, 0),
  [55] = {.entry = {.count = 2, .reusable = true}}, REDUCE(aux_sym_directive_repeat1, 2, 0, 0), SHIFT_REPEAT(5),
  [58] = {.entry = {.count = 2, .reusable = false}}, REDUCE(aux_sym_directive_repeat1, 2, 0, 0), SHIFT_REPEAT(5),
  [61] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_directive, 3, 0, 0),
  [63] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_directive, 3, 0, 0),
  [65] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_relation_block, 1, 0, 0),
  [67] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_relation_block, 1, 0, 0),
  [69] = {.entry = {.count = 1, .reusable = false}}, SHIFT(16),
  [71] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_rules_block, 1, 0, 0),
  [73] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_rules_block, 1, 0, 0),
  [75] = {.entry = {.count = 1, .reusable = false}}, SHIFT(20),
  [77] = {.entry = {.count = 1, .reusable = true}}, REDUCE(aux_sym_rules_block_repeat1, 2, 0, 0),
  [79] = {.entry = {.count = 1, .reusable = false}}, REDUCE(aux_sym_rules_block_repeat1, 2, 0, 0),
  [81] = {.entry = {.count = 2, .reusable = false}}, REDUCE(aux_sym_rules_block_repeat1, 2, 0, 0), SHIFT_REPEAT(20),
  [84] = {.entry = {.count = 1, .reusable = true}}, REDUCE(aux_sym_relation_block_repeat1, 2, 0, 0),
  [86] = {.entry = {.count = 1, .reusable = false}}, REDUCE(aux_sym_relation_block_repeat1, 2, 0, 0),
  [88] = {.entry = {.count = 2, .reusable = false}}, REDUCE(aux_sym_relation_block_repeat1, 2, 0, 0), SHIFT_REPEAT(16),
  [91] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_relation_block, 2, 0, 0),
  [93] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_relation_block, 2, 0, 0),
  [95] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_rules_block, 2, 0, 0),
  [97] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_rules_block, 2, 0, 0),
  [99] = {.entry = {.count = 1, .reusable = true}}, REDUCE(aux_sym_table_repeat1, 2, 0, 0),
  [101] = {.entry = {.count = 1, .reusable = false}}, REDUCE(aux_sym_table_repeat1, 2, 0, 0),
  [103] = {.entry = {.count = 2, .reusable = false}}, REDUCE(aux_sym_table_repeat1, 2, 0, 0), SHIFT_REPEAT(13),
  [106] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_table, 1, 0, 0),
  [108] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_table, 1, 0, 0),
  [110] = {.entry = {.count = 1, .reusable = false}}, SHIFT(15),
  [112] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_table, 2, 0, 0),
  [114] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_table, 2, 0, 0),
  [116] = {.entry = {.count = 1, .reusable = false}}, SHIFT(13),
  [118] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_relation_row, 1, 0, 0),
  [120] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_relation_row, 1, 0, 0),
  [122] = {.entry = {.count = 1, .reusable = false}}, SHIFT(38),
  [124] = {.entry = {.count = 1, .reusable = false}}, SHIFT(25),
  [126] = {.entry = {.count = 1, .reusable = true}}, SHIFT(32),
  [128] = {.entry = {.count = 1, .reusable = false}}, SHIFT(4),
  [130] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_table_header, 6, 0, 0),
  [132] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_table_header, 6, 0, 0),
  [134] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_table_header, 5, 0, 0),
  [136] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_table_header, 5, 0, 0),
  [138] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_rule_row, 1, 0, 0),
  [140] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_rule_row, 1, 0, 0),
  [142] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_alias_header, 5, 0, 0),
  [144] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_alias_header, 5, 0, 0),
  [146] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_narrative_block, 4, 0, 0),
  [148] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_narrative_block, 4, 0, 0),
  [150] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_alias_header, 4, 0, 0),
  [152] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_alias_header, 4, 0, 0),
  [154] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_narrative_block, 3, 0, 0),
  [156] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_narrative_block, 3, 0, 0),
  [158] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_block_header, 2, 0, 0),
  [160] = {.entry = {.count = 1, .reusable = false}}, REDUCE(sym_block_header, 2, 0, 0),
  [162] = {.entry = {.count = 1, .reusable = true}}, SHIFT(6),
  [164] = {.entry = {.count = 2, .reusable = true}}, REDUCE(aux_sym_table_header_repeat1, 2, 0, 0), SHIFT_REPEAT(41),
  [167] = {.entry = {.count = 1, .reusable = true}}, REDUCE(aux_sym_table_header_repeat1, 2, 0, 0),
  [169] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_column, 1, 0, 0),
  [171] = {.entry = {.count = 1, .reusable = true}}, SHIFT(40),
  [173] = {.entry = {.count = 1, .reusable = true}}, SHIFT(41),
  [175] = {.entry = {.count = 1, .reusable = true}}, SHIFT(46),
  [177] = {.entry = {.count = 1, .reusable = false}}, SHIFT(22),
  [179] = {.entry = {.count = 1, .reusable = false}}, SHIFT(35),
  [181] = {.entry = {.count = 1, .reusable = false}}, SHIFT_EXTRA(),
  [183] = {.entry = {.count = 1, .reusable = true}}, SHIFT(39),
  [185] = {.entry = {.count = 1, .reusable = true}}, SHIFT(23),
  [187] = {.entry = {.count = 1, .reusable = false}}, SHIFT(24),
  [189] = {.entry = {.count = 1, .reusable = false}}, SHIFT(30),
  [191] = {.entry = {.count = 1, .reusable = true}}, SHIFT(21),
  [193] = {.entry = {.count = 1, .reusable = true}}, SHIFT(49),
  [195] = {.entry = {.count = 1, .reusable = false}}, REDUCE(aux_sym_narrative_block_repeat1, 2, 0, 0),
  [197] = {.entry = {.count = 2, .reusable = false}}, REDUCE(aux_sym_narrative_block_repeat1, 2, 0, 0), SHIFT_REPEAT(35),
  [200] = {.entry = {.count = 2, .reusable = true}}, REDUCE(aux_sym_alias_header_repeat1, 2, 0, 0), SHIFT_REPEAT(39),
  [203] = {.entry = {.count = 1, .reusable = true}}, REDUCE(aux_sym_alias_header_repeat1, 2, 0, 0),
  [205] = {.entry = {.count = 1, .reusable = true}}, SHIFT(28),
  [207] = {.entry = {.count = 1, .reusable = true}}, SHIFT(47),
  [209] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_column, 2, 0, 0),
  [211] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_alias_entry, 3, 0, 0),
  [213] = {.entry = {.count = 1, .reusable = true}}, SHIFT(42),
  [215] = {.entry = {.count = 1, .reusable = true}}, SHIFT(19),
  [217] = {.entry = {.count = 1, .reusable = true}}, SHIFT(45),
  [219] = {.entry = {.count = 1, .reusable = true}},  ACCEPT_INPUT(),
  [221] = {.entry = {.count = 1, .reusable = true}}, SHIFT(18),
  [223] = {.entry = {.count = 1, .reusable = true}}, SHIFT(44),
  [225] = {.entry = {.count = 1, .reusable = true}}, SHIFT(26),
};

#ifdef __cplusplus
extern "C" {
#endif
#ifdef TREE_SITTER_HIDE_SYMBOLS
#define TS_PUBLIC
#elif defined(_WIN32)
#define TS_PUBLIC __declspec(dllexport)
#else
#define TS_PUBLIC __attribute__((visibility("default")))
#endif

TS_PUBLIC const TSLanguage *tree_sitter_sdif(void) {
  static const TSLanguage language = {
    .version = LANGUAGE_VERSION,
    .symbol_count = SYMBOL_COUNT,
    .alias_count = ALIAS_COUNT,
    .token_count = TOKEN_COUNT,
    .external_token_count = EXTERNAL_TOKEN_COUNT,
    .state_count = STATE_COUNT,
    .large_state_count = LARGE_STATE_COUNT,
    .production_id_count = PRODUCTION_ID_COUNT,
    .field_count = FIELD_COUNT,
    .max_alias_sequence_length = MAX_ALIAS_SEQUENCE_LENGTH,
    .parse_table = &ts_parse_table[0][0],
    .small_parse_table = ts_small_parse_table,
    .small_parse_table_map = ts_small_parse_table_map,
    .parse_actions = ts_parse_actions,
    .symbol_names = ts_symbol_names,
    .symbol_metadata = ts_symbol_metadata,
    .public_symbol_map = ts_symbol_map,
    .alias_map = ts_non_terminal_alias_map,
    .alias_sequences = &ts_alias_sequences[0][0],
    .lex_modes = ts_lex_modes,
    .lex_fn = ts_lex,
    .primary_state_ids = ts_primary_state_ids,
  };
  return &language;
}
#ifdef __cplusplus
}
#endif
