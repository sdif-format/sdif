package tree_sitter_sdif_test

import (
	"testing"

	tree_sitter "github.com/smacker/go-tree-sitter"
	"github.com/tree-sitter/tree-sitter-sdif"
)

func TestCanLoadGrammar(t *testing.T) {
	language := tree_sitter.NewLanguage(tree_sitter_sdif.Language())
	if language == nil {
		t.Errorf("Error loading Sdif grammar")
	}
}
