#!/bin/bash
# Cats relevant files from both repos into a single context bundle for Gemma.
# Intentionally piped via cat (NOT Read tool) so contents don't enter Claude's window.
# See ~/.claude/projects/-Users-macBot-Work-test/memory/feedback_local_model_context.md

set -e

OUT="/tmp/sheets-hardening/context-bundle.txt"
TEST_REPO="$HOME/Work/test"
DAKOTA="$HOME/Work/dakota-software"

{
  echo "============================================================"
  echo "SHEETS PIPELINE HARDENING — CONTEXT BUNDLE"
  echo "Generated: $(date)"
  echo "Spans two repos: ~/Work/test (madmax) + ~/Work/dakota-software"
  echo "============================================================"
  echo

  echo "## ~/Work/test/CLAUDE.md"
  cat "$TEST_REPO/CLAUDE.md" 2>/dev/null || echo "(missing)"
  echo

  echo "## ~/Work/test/backlog.md"
  cat "$TEST_REPO/backlog.md" 2>/dev/null || echo "(missing)"
  echo

  echo "## ~/Work/test/session-log.md (head 200)"
  head -200 "$TEST_REPO/session-log.md" 2>/dev/null || echo "(missing)"
  echo

  echo "## ~/Work/test/local-ai.md"
  cat "$TEST_REPO/local-ai.md" 2>/dev/null || echo "(missing)"
  echo

  echo "## ~/Work/test/harden.md"
  cat "$TEST_REPO/harden.md" 2>/dev/null || echo "(missing)"
  echo

  echo "============================================================"
  echo "## dakota-software docs/sheets/"
  echo "============================================================"
  for f in roadmap.md phase-2-inventory.md phase1-test-plan.md \
           tab-structure-by-property.md read-write-methods.md \
           alert-system-design.md alert-tiers-design.md alert-audit-2026-05.md \
           pipeline-proposal.md via-verona-make-plan.md \
           annual-validation-plan.md do-not-fix.md \
           sorting-hat-kickoff.md sorting-hat-alert-discussion.md \
           2026-05-12-phase-1-shipped.md; do
    echo
    echo "### docs/sheets/$f"
    cat "$DAKOTA/docs/sheets/$f" 2>/dev/null || echo "(missing)"
  done

  echo "============================================================"
  echo "## dakota-software docs/cash-tracking/"
  echo "============================================================"
  for f in phase-3-plan.md cash-tracking-format-analysis.md \
           2026-05-16-csv-ingest-design.md \
           2026-05-18-phase-3-complete-handoff.md \
           2026-05-19-rollup-formulas-and-verification-roadmap.md; do
    echo
    echo "### docs/cash-tracking/$f"
    cat "$DAKOTA/docs/cash-tracking/$f" 2>/dev/null || echo "(missing)"
  done

  echo "============================================================"
  echo "## dakota-software bot/pdf-extractor/ (design + small files only)"
  echo "============================================================"
  for f in PIPELINE-SPEC.md WIRE-BRIDGE-PLAN.md WIRE-BRIDGE-PROMPT.md \
           SORTING_HAT_CUTOVER.md PDF_READER_README.md FIX-FDA-PROMPT.md \
           property_map.json requirements.txt; do
    echo
    echo "### bot/pdf-extractor/$f"
    cat "$DAKOTA/bot/pdf-extractor/$f" 2>/dev/null || echo "(missing)"
  done

  echo
  echo "## bot/pdf-extractor/ — source files: filenames + LOC only (NOT contents)"
  ls -la "$DAKOTA/bot/pdf-extractor/"*.py "$DAKOTA/bot/pdf-extractor/"*.sh 2>/dev/null
  echo
  for f in "$DAKOTA/bot/pdf-extractor/"*.py "$DAKOTA/bot/pdf-extractor/"*.sh; do
    [ -f "$f" ] && echo "$(wc -l < "$f") lines: $(basename "$f")"
  done

  echo "============================================================"
  echo "## Recent git log — dakota-software (last 50)"
  echo "============================================================"
  cd "$DAKOTA" && git log --oneline -50

  echo
  echo "============================================================"
  echo "## Recent git log — test repo (last 30)"
  echo "============================================================"
  cd "$TEST_REPO" && git log --oneline -30

} > "$OUT"

echo "Built: $OUT ($(wc -l < "$OUT") lines, $(wc -c < "$OUT") bytes)"
