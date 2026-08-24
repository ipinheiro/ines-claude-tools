---
name: styling-artifacts
description: "Use when building, publishing or restyling an HTML artifact page - a report, dashboard, run explorer, review or comparison page, data summary, explainer - at the point of choosing fonts, colours, layout or components. Also use when someone asks for the house style, the team style, the usual look, or for a page to match the other artifacts."
---

# Styling artifacts

## Overview

The Data Science and Analytics team has one visual system for artifacts, and
every HTML artifact uses it. This skill is the "existing design system" that
the bundled `artifact-design` skill defers to in its first fundamental:
`artifact-design` still decides treatment depth, structure and copy, and this
skill supplies the identity. The subject shapes what the page says and how it
is organised. It does not get its own palette or typeface.

One family (Archivo), one accent (rust), three states (good, caution, bad)
with a shape each, paper neutrals with a warm charcoal dark, and a theme
toggle on every page. `example.html` in this directory shows every component
live in both themes; open it before building anything unfamiliar.

## When to use

- Any HTML artifact publish. Load `artifact-design` first, then this, then
  write CSS.
- Restyling a page that was built without it.
- Not for Markdown artifacts.
- Not when the user names a different look in so many words. Their words win;
  say which rule you are departing from.

## The page, part by part

1. **Head.** Paste `${CLAUDE_SKILL_DIR}/head.html` at the top of the page: the
   Archivo font link and the theme boot script. Archivo is the only family.
   No serif, no monospace; code uses Archivo at 13px on `--surface-2`.
2. **Tokens.** The stylesheet opens with `${CLAUDE_SKILL_DIR}/tokens.css`
   pasted in full: three theme blocks, base styles and the three utilities.
   Every colour on the page is a `var(--…)` from it. A colour literal outside
   those blocks is a bug.
3. **Toggle.** The button from `${CLAUDE_SKILL_DIR}/theme-toggle.html` goes in
   `.top-right` of the top bar, or in `.page-right` of the page head when the
   page has no top bar; its script goes at the end of the body. Every page
   has it.
4. **Type.** Body 15px / 1.5 weight 400. Headings weight 500 with slightly
   tight tracking; subtitles and the hero number weight 300. The wide cut
   (`.display` or `font-stretch: 112%`) is for elements 22px and larger
   only: page title, hero number, verdict answer, stat values. Labels are
   `.eyebrow`. Digits in columns get `.num`. `strong` is 500 in UI text and
   700 inside quoted copy.
5. **Accent and state.** `--accent` marks emphasis: the selected item, the
   winner ring, the primary bar, the button, the link. `--ok`, `--warn` and
   `--bad` with their `-soft` pairs mark state and nothing else. Map the
   subject's own ladder onto four treatments: good, caution, bad, and
   outlined neutral for unclear or absent. A ladder with more than four rungs
   collapses onto these, lowest rungs to neutral. State follows the page's
   question: a flag "worth raising" is good on a page that judges the screen
   and bad on a page that judges titles, and a page with two ladders maps
   both from the same point of view. Every marker carries its shape as well
   as its colour (circle, diamond, square, outlined circle), which the
   `.state`, `.mark`, `.banner` and `.legend` classes do for you. Chart fills
   are flat; the legend names them.
6. **Surfaces.** Page on `--bg`; cards, top bar and tables on `--surface`
   with a 1px `--line` border, `--radius` and `--shadow`; card footers, code
   and notes on `--surface-2`; selected and hovered rows on `--accent-wash`.
7. **Components.** Take them from `${CLAUDE_SKILL_DIR}/components.css` with
   the markup in `${CLAUDE_SKILL_DIR}/components.md`. Paste the whole sheet;
   unused rules cost nothing. Sections inside `.wrap` go in a `.stack`, not
   behind margins. Build a new component only when none fits, and style it
   through the same tokens at the same sizes.
8. **Composition.** Pick the row that matches the page's job:

| Page's job | Composition |
|---|---|
| Report one outcome and its reasons | page head → verdict panel → comparison cards → folds for context |
| Let the reader browse many items | top bar with pill tabs → split list + detail, the row above inside each detail |
| Summarise a run or batch | lead (hero number + stat tiles beside a reading) → charts → table with legend |
| Explain how something works | side-rail sections: sticky title and framing prose beside each figure, card or table |
| Overview plus browse | pill tabs: Overview, then one tab per item group; hash router, `#tab/item-id` |

9. **Voice.** The hero number states the page's main finding and its label
   completes the sentence ("31 of 43 winners came from variant 0"). The
   reading beside it says what the numbers show and where they stop. Stat
   labels explain the number in words, not field names. Chart rows carry the
   underlying counts in `data-tip` or `title`. The page foot says what the
   numbers rest on. Write the copy with `productivity-skills:writing-clearly`
   (same marketplace; read it from the repo if it is not installed).
10. **Charts beyond bars.** The bundled `dataviz` skill decides chart form;
    these tokens replace its palette.
11. **Responsive.** The single 1100px breakpoint in `components.css`.

## Before publishing

- Every colour literal in the stylesheet sits inside the three `tokens.css`
  blocks, and the media-query block matches the `[data-theme="dark"]` block.
- `body` paints `--bg`. The toggle is present and switches both ways.
- The font link is the Archivo one from `head.html`. No other `font-family`
  appears except the `--font` stack.
- Every state on the page maps onto good / caution / bad / neutral with a
  shape. A legend sits above any table or chart that uses marks.
- Focus states visible, `prefers-reduced-motion` honoured, wide content in
  its own `overflow-x: auto` container.
- `<title>` is a name, not a caption (`artifact-design` covers this).

## Common mistakes

| Mistake | Correction |
|---|---|
| A second family "for character", a serif for quotes, a monospace for code | Archivo alone. Character comes from weight 300 against 500 and the wide cut on large elements |
| A fresh palette because the subject suggests one, or a dark mode that is near-black | The tokens are fixed; the subject changes structure and copy. Dark is the warm charcoal in `tokens.css` |
| `--warn` or `--bad` used for emphasis, or the accent used for a state | The accent emphasises; the state colours report state |
| A state carried by colour alone | Use `.state`, `.mark`, `.banner` or `.legend`, which add the shape |
| Domain names for colours (`--critical`, `--blocked`) | Map the domain onto `--ok` / `--warn` / `--bad` |
| No toggle, or a toggle that ignores the host theme | Boot script from `head.html`, button and script from `theme-toggle.html` |
| Masthead, numbered section markers, drop caps, frosted glass, gradient hero | Not in the register. A top bar or a page head, then the compositions above |
| Margins between laid-out siblings (cards, tiles, columns, sections) | Grid or flex with `gap`, `.stack` for sections; sibling margins are for prose rhythm only (`p + p`, `.block + .block`) |
| A stat label that is a field name (`n_titles`) | A phrase that explains the number ("titles screened") |
| Four stat tiles squeezed beside the reading in a lead | Three fit. Four or more go in a `.stat-row` placed as a direct child of `.lead`, which spans the width |
| A red verdict chip beside green chips for the evidence behind it | Two ladders on one page are mapped from the same point of view |
| A three-state toggle (system / light / dark) | Two states, from whatever is showing. The un-stamped document already follows the host |

## Files

| File | What it is |
|---|---|
| `tokens.css` | Three theme blocks, base styles, `.display` / `.eyebrow` / `.num`. Paste in full |
| `components.css` | Every component, styled through the tokens. Paste in full |
| `components.md` | The catalogue: one entry per component, with markup |
| `head.html` | Font link and theme boot script |
| `theme-toggle.html` | Toggle button and its script |
| `example.html` | Every component live in both themes. Built by `scripts/build_example.py` from the files above; edit those, not this |
