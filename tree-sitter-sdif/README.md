# tree-sitter-sdif

MVP Tree-sitter package for SDIF editor tooling, syntax highlighting, and
incremental parse experiments. This package is intentionally tooling-only: the
normative parser and canonical AST remain in the Python package under `src/sdif/`.

SDIF and `.sdif.ai` are the agent-facing interchange surfaces. JSON fixtures may
exist for equivalence checks, but agents should not need to use JSON to work with
SDIF documents.

## Local commands

Install a Tree-sitter CLI compatible with this package and run:

```bash
npm install
npm run generate
npm test
```

The checked-in corpus starts with `corpus/core.txt` and should stay aligned with
representative SDIF documents and the Python parser behavior.
