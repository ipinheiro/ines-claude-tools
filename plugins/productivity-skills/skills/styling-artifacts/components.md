# Component catalogue

Every component below has its CSS in `components.css` and reads colour only
from `tokens.css`. Markup shapes are the ones the CSS expects; class names are
the contract. Numbers that line up in columns get `class="num"`. Small caps
labels are `.eyebrow`, never a heading.

## Page chrome

### Top bar with pill tabs
Sticky, 56px, three-column grid: brand on the left, tabs centred, run metadata
on the right. The selected tab inverts to ink-on-bg; counts sit inside the tab
at reduced weight. Use when the page has 2-4 views; a single-view page has no
tab bar, just a `.book-head`-style title block.

```html
<header class="top">
  <div class="brand">
    <span class="brand-name">Blurb Lab Verdicts</span>
    <span class="brand-sub">43 runs · 20 Aug</span>
  </div>
  <nav class="tabs" role="tablist" aria-label="Sections">
    <button class="tab" role="tab" aria-selected="true">Overview</button>
    <button class="tab" role="tab" aria-selected="false">Fiction<span class="count num">28</span></button>
  </nav>
  <div class="runmeta"><span>writer <b>gpt-5.6-terra</b></span><span>judge <b>sonnet</b></span></div>
</header>
```

Views toggle with `.view` / `.view.is-active` and a hash router; each view is
a `<section role="tabpanel">`. Hash shape: `#tab` for a view, `#tab/item-id`
for an item inside it, `#tab/item-id/anchor` for a position within the item
(a file and a line, a variant index). Every list row, table link and shortlist
entry navigates by setting the hash, so links are copyable.

### Split layout: sticky list + detail
300px list column, sticky under the top bar, with a search box and keyboard
hint in `.list-head`; detail column with `padding: 32px 40px`, max 1480px. The
current list item gets `aria-current="true"` (accent wash + 2px accent left
border). Items carry a title, a muted second line, and on the right either a `.slots`
strip of 9px squares (one per sub-item, up to about six, `.is-win` /
`.is-bar` for state) or a `.counts` pair of small numbers (`<span
class="counts"><b class="warn">5</b><b>4</b></span>`) when the item holds
more sub-items than squares can show. Collapses to stacked at 1100px.

```html
<div class="split">
  <aside class="list">
    <div class="list-head">
      <input class="search" type="search" placeholder="Search title, author or ISBN" aria-label="Search">
      <div class="list-hint"><span>43 books</span><span>↑ ↓ to move</span></div>
    </div>
    <ul class="book-list">
      <li><button class="book-item" aria-current="true">
        <span><span class="t">The Hollow Vale</span><span class="a">A. Writer</span></span>
        <span class="slots"><span class="slot is-win"></span><span class="slot"></span><span class="slot"></span></span>
      </button></li>
    </ul>
  </aside>
  <article class="detail">…</article>
</div>
```

## Heads and panels

### Page / item head
Title at 30px weight 500 with tight tracking; subtitle at 16px weight 300;
identifiers as a 12px muted row. Chips on the right for categorical metadata;
`.chip.tone` (dashed border) distinguishes a softer category from a hard one.

```html
<div class="book-head">
  <div>
    <h1 class="book-title">The Hollow Vale</h1>
    <div class="book-author">A. Writer</div>
    <div class="book-ids"><span>ISBN 9780000000001</span><span>work 487176</span></div>
  </div>
  <div class="chips"><span class="chip">literary fiction</span><span class="chip tone">melancholic</span></div>
</div>
```

### Verdict panel
The decision and its reasoning, side by side: a 220px column with the big
accent-coloured answer and its label, then the rationale at 72ch. An optional
`.bar-flag` (warn-soft pill with a dot) carries a caveat about the decision.
Use whenever a page reports a single outcome that has a reason.

```html
<div class="verdict-panel">
  <div class="verdict-winner">
    <span class="eyebrow">Judge's pick</span>
    <span class="big">Variant 0</span>
    <span class="angle">final letter returns</span>
    <span class="bar-flag">every candidate below the bar</span>
  </div>
  <div class="verdict-rationale"><span class="eyebrow">Rationale</span><p>…</p></div>
</div>
```

## Cards

### Comparison cards (`.variants` / `.variant`)
Auto-fit grid, min 320px. Each card: head (eyebrow slot name + 15px angle,
`.win-tag` on the winner), body copy at 62ch with bold at 700, then a
`.judge-note` footer on surface-2 holding a `.verdict-chip` and the note. The
winner gets an accent ring (`.is-winner`). Footer is pushed to the bottom with
`margin-top: auto` so cards in a row align.

```html
<article class="variant is-winner">
  <div class="variant-head">
    <div class="variant-id"><span class="slot-name">Variant 0</span><span class="angle">final letter returns</span></div>
    <span class="win-tag">Winner</span>
  </div>
  <div class="copy"><p>…</p></div>
  <div class="judge-note">
    <div class="judge-note-head"><span class="eyebrow">Judge's note</span><span class="verdict-chip survives">survives screen</span></div>
    <p>…</p>
  </div>
  <div class="variant-meta"><span class="num">111 words</span><span class="num">12.9 s</span></div>
</article>
```

`.verdict-chip` variants: `.survives` (ok), `.caution` (warn), `.eliminated`
(bad), `.unclear` (outlined, muted). The class names come from the judging
page but the chip is generic: good / caution / bad / neutral. Semantic colour
is separate from the accent.

### Exemplar / reference cards (`.exemplars` / `.exemplar`)
Same grid, lighter treatment: title, muted meta line, then scrollable copy at
13px capped at 340px. Use for supporting material the reader may want to
consult but not read in full.

### Stat tiles (`.stat-row` / `.stat`)
Auto-fit, min 150px. A 26px value over a 12px muted label. Three to four per
row; the label is a phrase that explains the number, not a key.

### Key-value grid (`.kv`)
Auto-fit, min 180px. Eyebrow over value. For run metadata, identifiers, config
- short values. Values wrap only when a token cannot fit the column; a
sentence belongs in a `.ctx-block`, not here.

### Code
`code` inline and `pre` blocks share the system monospace stack at 13px on
`--surface-2`; blocks get a `--line` border and scroll horizontally. For a
before / after comparison use `.code-pair`: two columns, each an eyebrow over
a `pre`, with `.proposed` on the column whose border should carry the accent.

```html
<div class="code-pair">
  <div><span class="eyebrow">Current</span><pre><code>…</code></pre></div>
  <div class="proposed"><span class="eyebrow">Suggested</span><pre><code>…</code></pre></div>
</div>
```

## Folds

`<details class="fold">` with a `<summary>` that is a flex row: label left,
`.sum-right` (muted count or hint) right, and a `+` / `–` marker via `::after`.
The body uses `.ctx-grid` (1.4fr / 1fr) and `.ctx-block` (eyebrow + 14px
prose). Folds stack with a top border and a bottom border each. Use them for
context the reader needs sometimes: inputs, source material, configuration.

```html
<div class="folds">
  <details class="fold">
    <summary>Book context<span class="sum-right">synopsis, tags, key points</span></summary>
    <div class="fold-body"><div class="ctx-grid">
      <div class="ctx-block synopsis"><span class="eyebrow">Synopsis</span><p>…</p></div>
      <div><div class="ctx-block"><span class="eyebrow">Themes</span><p>…</p></div></div>
    </div></div>
  </details>
</div>
```

## Overview

### Lead: hero number + reading
`.ov-lead` is a two-column grid: left, an eyebrow, the `.hero-num` (64px
weight 300, tight tracking, with a `<small>` denominator) and a `.hero-label`
sentence that completes the number; then a `.stat-row`. Right, `.reading`: two
or three paragraphs at 64ch that interpret the numbers and say what they can
and cannot show. The hero number is the page's thesis; the reading is its
argument.

```html
<div class="ov-lead">
  <div>
    <div class="eyebrow">Winning slot, all 43 books</div>
    <div class="hero-num num">31<small>of 43</small></div>
    <div class="hero-label">winners came from variant 0, the first candidate the judge reads.</div>
    <div class="stat-row">…</div>
  </div>
  <div class="reading"><p>…</p><p>…</p></div>
</div>
```

### Bar charts (`.charts` / `.chart`)
Cards with an `h3`, a `.sub`, and `.bars`. Each `.bar-row` is a 60px key,
a track, and a 56px value with a `<small>` percentage. Fills are accent by
default, `.muted` for a baseline category, `.warn` for a caveat category. An
expected-value marker is a 1px `.expect` line with a 10px `.expect-label`
beneath, positioned inside `.expect-wrap`. Always give the row a `title=`
with the underlying counts. `.rate-row` is the same shape with a wider value
column for "x of y" readouts. Keys longer than one short word need
`.bars.wide-key` (140px key column; the expectation marker shifts with it).

### Table (`.ov-table-wrap` / `.ov-table`)
Bordered surface, 13px, uppercase 11px headers, row hover in accent wash,
last row without a border. Cells that navigate are `<button class="link">`
carrying a `.t` title and `.a` muted second line. `.mini-verdicts` is a row of
10px dots (`.mv.survives` filled ok, `.mv.eliminated` bad outline on bad-soft,
`.mv.unclear` outline only, `.is-win` double ring in accent). Put a `.legend`
above any table or chart that uses the dots.

### Section headings
`.section-title` (18px) with `.section-sub` (13px muted) directly below.

## Responsive
One breakpoint at 1100px: the top bar wraps and drops run meta, the split
becomes stacked with the list capped at 40vh, the two-column grids collapse,
paddings tighten. Add nothing else unless the content demands it.
