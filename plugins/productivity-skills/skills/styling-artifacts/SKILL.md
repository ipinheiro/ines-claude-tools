---
name: styling-artifacts
description: Use when building, publishing, or restyling any HTML artifact page for Inês - a report, dashboard, review page, run explorer, verdict or comparison view, data summary - at the point of choosing fonts, colours, layout, or components. Also use when asked for "the house style", "like the Blurb Lab page", or "the usual look".
---

# Styling artifacts

## Overview

Inês has a house visual system and every artifact uses it. This skill is the
"existing design system" that `artifact-design`'s first fundamental defers to:
`artifact-design` still decides treatment depth, structure, and copy; this
skill supplies the identity. The subject shapes what the page says and how it
is organised. It does not get its own palette or typeface.

One family, one accent, three semantic colours, hierarchy from weight and
tracking, labels as small caps. Reference: `example.html` in this directory
is a working page in the system.

## When to use

- Any HTML Artifact publish. Load `artifact-design` first, then this, then
  write CSS.
- Restyling a page that was built without it.
- Not for Markdown artifacts. Not when Inês names a different look in so many
  words - her words win; say which rule you are departing from.

## The page, part by part

1. **Head.** The link from `font-link.html`. Roboto 300/400/500/700 is the
   only family. Code uses the `code` / `pre` rules in `components.css`
   (system monospace, 13px, on `--surface-2`).
2. **Tokens.** The stylesheet opens with `tokens.css` verbatim, all three
   theme blocks. Every colour on the page is a `var(--…)` from it.
3. **Accent and state.** `--accent` is the single emphasis hue: selected
   item, winner ring, primary bar, link hover. `--ok`, `--warn`, `--bad` with
   their `-soft` pairs carry state and nothing else. Map the subject's states
   onto four treatments: good → ok, caution → warn, bad → bad, neutral or
   absent → outlined muted (`.verdict-chip.unclear`, `.mv.unclear`). A ladder
   with more than four rungs is collapsed onto these, lowest rungs to neutral
   (a severity ladder: Critical → bad, Important → caution, Suggestion and
   below → neutral; nothing is "good").
4. **Type.** Body 15px / 1.5. Headings weight 500 with slightly negative
   tracking; a subtitle is weight 300. Big numbers are weight 300 at 64px
   with a `<small>` denominator. Labels are `.eyebrow` (11px, 0.08em
   tracking, uppercase, muted). Digits in columns get `.num`. `strong` is 500
   in UI text and 700 inside quoted copy.
5. **Surfaces.** Page on `--bg`; cards on `--surface` with a 1px `--line`
   border, `--radius` 6px, `--shadow`; card footers and notes on
   `--surface-2`; selected and hover rows on `--accent-wash`.
6. **Components.** Take them from `components.css` with the markup in
   `components.md`. Build a new one only when none fits, styled through the
   same tokens and in the same register.
7. **Composition.** Pick the row that matches the page's job:

| Page's job | Composition |
|---|---|
| Report one outcome and its reasons | page head → verdict panel → comparison cards → folds for context |
| Let the reader browse many items | top bar with pill tabs → split list + detail (the row above inside each detail) |
| Summarise a run or batch | overview lead (hero number + stat tiles beside a reading) → bar charts → table with legend |
| Overview plus browse | tabs: Overview, then one tab per item group; hash router |

8. **Voice.** The hero number is a thesis and its label is the sentence that
   completes it ("31 of 43 winners came from variant 0"). The reading beside
   it says what the numbers show and what they cannot. Stat labels are
   phrases that explain the number, not field names. Chart rows carry the
   underlying counts in `title=`.
9. **Responsive.** The single 1100px breakpoint from `components.css`.

## Before publishing

- Every colour literal in the stylesheet sits inside the three `tokens.css`
  blocks; the media-query block and the `[data-theme="dark"]` block match.
- `body` paints `--bg`. Focus states visible. `prefers-reduced-motion`
  honoured.
- `<title>` is a name, not a caption (`artifact-design` covers this).

## Common mistakes

| Mistake | Correction |
|---|---|
| A serif display face or a second family "for character" | Roboto alone; character comes from weight 300 vs 500 and tracking |
| A fresh palette because the subject suggests one | Tokens are fixed; the subject changes structure and copy |
| `--warn` used for emphasis, or the accent used for a state | Accent emphasises, semantic colours report state |
| Severity or outcome colours named after the domain (`--critical`) | Map domain states onto `--ok` / `--warn` / `--bad` |
| Masthead, colophon, numbered markers, drop caps | Not in the register; a top bar or a page head, and folds for the rest |
| Margins between laid-out siblings (cards, tiles, columns) | Grid or flex with `gap`; adjacent-sibling margins are for prose rhythm only (`p + p`, `.ctx-block + .ctx-block`) |
