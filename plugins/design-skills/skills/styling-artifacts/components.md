# Component catalogue

Every component here has its CSS in `components.css` and takes colour only
from `tokens.css`. The class names are the contract: use the markup shapes
below and the CSS does the rest. Digits that line up in columns get
`class="num"`. Small-caps labels are `.eyebrow`, never a heading. `example.html`
shows every entry live in both themes.

## Chrome

### Top bar with pill tabs

Sticky, 56px, three columns: brand on the left, tabs in the centre, run
metadata and the theme toggle on the right. The selected tab inverts to ink on
bg. Counts sit inside the tab at a lighter weight. A page with one view has no
top bar, only a page head, and the toggle goes in the page head's `.page-right`.

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
  <div class="top-right">
    <div class="top-meta"><span>writer <b>gpt-5.6</b></span><span>judge <b>sonnet</b></span></div>
    <!-- theme toggle button from theme-toggle.html -->
  </div>
</header>
```

Views toggle with `.view` / `.view.is-active` and a hash router. Each view is a
`<section role="tabpanel">`. Hash shape: `#tab` for a view, `#tab/item-id` for
an item inside it, `#tab/item-id/anchor` for a position within the item. Every
list row, table link and shortlist entry navigates by setting the hash, so
links can be copied.

### Theme toggle

The button goes in `.top-right` of the top bar, or in `.page-right` of the
page head when the page has no top bar; the script goes at the end of the
body. Both are in `theme-toggle.html`. The boot script in `head.html` goes before the
stylesheet. The toggle switches from whatever theme is showing, saves the
choice in `localStorage` as `dsa-theme`, and updates its `aria-label`. It also
fires a `themechange` event on `document`, for anything that reads rendered
colours.

### Segmented control

For switching between two to four views inside a panel. Navigation between
pages stays in the top bar.

```html
<div class="seg" role="tablist" aria-label="Unit">
  <button role="tab" aria-selected="true">Counts</button>
  <button role="tab" aria-selected="false">Share</button>
</div>
```

### Split layout: sticky list + detail

A 300px list column, sticky under the top bar, with a search box and keyboard
hint in `.list-head`, and a detail column at `padding: 32px 40px`, max 1480px.
The current item gets `aria-current="true"`. Each item has a title, a muted
second line, and on the right either a `.slots` strip of 9px squares (one per
sub-item, up to about six, `.is-on` / `.is-warn`) or a `.counts` pair when
there are more sub-items than squares can show. Stacks below 1100px.

```html
<div class="split">
  <aside class="list">
    <div class="list-head">
      <input class="search" type="search" placeholder="Search title, author or ISBN" aria-label="Search">
      <div class="list-hint"><span>43 books</span><span>↑ ↓ to move</span></div>
    </div>
    <ul class="list-items">
      <li><button class="list-item" aria-current="true">
        <span><span class="t">The Hollow Vale</span><span class="a">A. Writer</span></span>
        <span class="slots"><span class="slot is-on"></span><span class="slot"></span><span class="slot"></span></span>
      </button></li>
      <li><button class="list-item">
        <span><span class="t">The Bat</span><span class="a">Jo Nesbo</span></span>
        <span class="counts"><b class="warn">5</b><b>4</b></span>
      </button></li>
    </ul>
  </aside>
  <article class="detail">…</article>
</div>
```

### Rail nav

Links to the sections of a long detail view, sticky beside the content. Give
the current section `aria-current="true"`.

```html
<nav class="rail-nav" aria-label="Sections">
  <a href="#flags" aria-current="true">Flags<span class="count num">7</span></a>
  <a href="#passages">Passages<span class="count num">11</span></a>
</nav>
```

### Controls

One primary `.btn` per view, labelled with what it does. `.btn.ghost` for
secondary actions. `.search` and `.select` sit on `--bg` with a `--line-2`
border. `.filter-row` lays them out with a trailing `.count`.

```html
<div class="filter-row">
  <input class="search" type="search" placeholder="Search title or ISBN" aria-label="Search">
  <select class="select" aria-label="Verdict"><option>Any verdict</option></select>
  <button class="btn">Publish</button>
  <button class="btn ghost">Export CSV</button>
  <span class="count num">1,148 of 1,148</span>
</div>
```

## Heads and leads

### Page head

Title at 30px weight 500 in the wide cut; subtitle at 16px weight 300;
identifiers as a 12px muted row. Chips on the right hold categorical metadata;
`.chip.tone` (dashed border) marks a softer category. On a page with no top
bar, wrap the chips and the theme toggle in `.page-right`.

```html
<div class="page-head">
  <div>
    <h1 class="page-title">The Hollow Vale</h1>
    <div class="page-sub">A. Writer</div>
    <div class="page-ids"><span>ISBN 9780000000001</span><span>work 487176</span></div>
  </div>
  <div class="page-right">
    <div class="chips"><span class="chip">literary fiction</span><span class="chip tone">melancholic</span></div>
    <!-- theme toggle button here when there is no top bar -->
  </div>
</div>
```

### Page stack

Inside `.wrap`, put the page's sections in a `.stack` (flex column, 40px gap)
rather than giving each one a margin. The page foot keeps a small gap of its
own inside the stack.

```html
<main class="wrap"><div class="stack">
  <div class="page-head">…</div>
  <div class="lead">…</div>
  <div class="charts">…</div>
  <div class="page-foot">…</div>
</div></main>
```

### Section heading

`.section-title` (18px) with `.section-sub` (13px muted) directly below.

### Side-rail section

For pages that explain as they go. A 250px sticky column holds an eyebrow, a
title and one or two `.sec-note` paragraphs; the material sits on the right.
Sections stack with a border between them. Stacks below 1100px.

```html
<div class="sec">
  <div class="sec-head">
    <span class="eyebrow">The pipeline</span>
    <h2>Five stages</h2>
    <p class="sec-note">Every quote on this page was sliced from the manuscript itself.</p>
  </div>
  <div>…figure, card or table…</div>
</div>
```

### Lead: hero number + reading

`.lead` is a two-column grid. Left: an eyebrow, the `.hero-num` (64px weight
300, wide cut, with a `<small>` denominator), a `.hero-label` sentence that
completes the number, then a `.stat-row` of up to three tiles. Right:
`.reading`, two or three paragraphs at 64ch that say what the numbers show and
where they stop. Four or more tiles do not fit beside the reading: put the
`.stat-row` as a direct child of `.lead`, after the two columns, and it spans
the full width.

```html
<div class="lead">
  <div>
    <div class="eyebrow">Winning slot, all 43 books</div>
    <div class="hero-num num">31<small>of 43</small></div>
    <div class="hero-label">winners came from variant 0, the first candidate the judge reads.</div>
    <div class="stat-row">
      <div class="stat"><div class="v num">1,148</div><div class="l">titles screened</div></div>
      <div class="stat bad"><div class="v num">27%</div><div class="l">of quiet titles carried a miss</div></div>
    </div>
  </div>
  <div class="reading"><p>…</p><p>…</p></div>
</div>
```

### Stat tiles

`.stat-row` is an auto-fit grid, min 150px. Each `.stat` has a 26px value over
a 12px label. The label explains the number in words rather than repeating a
field name. Add `.good`, `.caution` or `.bad` only when the number is itself a
state.

### Verdict panel

The decision and its reasoning side by side: a 220px column with the
accent-coloured answer and its label, then the rationale at 72ch. A
`.banner.caution` inside the answer column carries a caveat. Use whenever a
page reports one outcome that has a reason.

```html
<div class="verdict-panel">
  <div class="verdict-answer">
    <span class="eyebrow">Judge's pick</span>
    <span class="big">Variant 0</span>
    <span class="angle">final letter returns</span>
    <span class="banner caution">every candidate below the bar</span>
  </div>
  <div class="verdict-rationale"><span class="eyebrow">Rationale</span><p>…</p></div>
</div>
```

## Cards

### Comparison cards

`.cards` is an auto-fit grid, min 320px. Each `.card` has a head (eyebrow-style
slot name plus a 15px angle, `.tag` on the winner), body copy at 62ch with bold
at 700, a `.card-foot` on surface-2 holding a `.state` chip and a note, and an
optional `.card-meta` row. The winner gets `.is-winner` for the accent ring.
`margin-top: auto` pushes the footer down so cards in a row line up.

```html
<article class="card is-winner">
  <div class="card-head">
    <div class="card-id"><span class="slot-name">Variant 0</span><span class="angle">final letter returns</span></div>
    <span class="tag">Winner</span>
  </div>
  <div class="copy"><p>…</p></div>
  <div class="card-foot">
    <div class="card-foot-head"><span class="eyebrow">Judge's note</span><span class="state good">survives screen</span></div>
    <p>…</p>
  </div>
  <div class="card-meta"><span class="num">111 words</span><span class="num">12.9 s</span></div>
</article>
```

### Reference cards

`.ref-cards` / `.ref-card`: title, muted meta line, then 13px copy that scrolls
after 340px. For material the reader might consult without reading in full.

```html
<article class="ref-card">
  <div class="ref-title">Three Days in June</div>
  <div class="ref-meta">Anne Tyler · Vintage</div>
  <div class="ref-copy"><p>…</p></div>
</article>
```

### Key-value grid

`.kv`: auto-fit, min 180px, eyebrow over value. For identifiers, configuration
and other short values. Sentences go in a `.block`.

```html
<div class="kv">
  <div><span class="eyebrow">Run</span><span class="v num">20260804T091243Z</span></div>
  <div><span class="eyebrow">Judge</span><span class="v">sonnet</span></div>
</div>
```

### Callout with tag

A framed statement the reader should not skip. The `.tag-label` says what kind
of statement it is. Add `.caution`, `.bad` or `.good` to tint the frame.

```html
<div class="callout caution">
  <span class="tag-label">read this honestly</span>
  <p><strong>The scorer errs toward under-rating.</strong> Lean on the receipts when a decision is close.</p>
</div>
```

### Note

`.note`: a muted aside on surface-2 with a left border, 70ch.

### Banners

One-line state with its marker. `.banner.good`, `.caution`, `.bad`,
`.neutral`. `.banner-more` right-aligns a count or hint.

```html
<div class="banner caution">Every candidate below the bar<span class="banner-more">3 of 43 books</span></div>
```

### Empty state

```html
<div class="empty">Select a title to see its receipts.<span>1,148 screened · 11,803 receipts held</span></div>
```

## State

Colour and shape always go together on a marker. Good is a filled circle,
caution a diamond, bad a filled square, neutral an outlined circle. Map the
subject's own ladder onto these four: critical / blocked / eliminated → bad;
important / assess / below the bar → caution; survives / passes / clean →
good; suggestion / unclear / not run / no data → neutral. Collapse a ladder
longer than four rungs, lowest rungs to neutral.

State follows the page's question. A flag "worth raising" is good on a page
that judges the screen (the flag did its job) and bad on a page that judges
titles (the title has a problem). When a page carries two ladders, map both
from the same point of view, so a red verdict never sits beside green evidence
for it.

The shapes live on markers: chips, table marks, banners and legend swatches.
Chart fills are flat, and the legend above the chart names them.

### Chips

```html
<span class="state good">survives screen</span>
<span class="state caution">below the bar</span>
<span class="state bad">eliminated</span>
<span class="state neutral">unclear</span>
```

### Marks and legend

`.marks` is a row of 10px `.mark` shapes, one per sub-item; `.is-win` adds the
accent ring. Put a `.legend` above any table or chart that uses marks. Legend
swatches are `<i>` with the state class, or `.accent` / `.muted` for chart
fills.

```html
<div class="legend"><span><i class="good"></i>survives</span><span><i class="bad"></i>eliminated</span><span><i class="accent"></i>winner</span></div>
<span class="marks"><span class="mark good is-win"></span><span class="mark bad"></span><span class="mark neutral"></span></span>
```

## Data

### Table

`.table-wrap` (bordered surface, scrolls sideways) around `table.table`: 13px
text, 11px uppercase headers, accent wash on hover, no border on the last row.
`tr.is-current` marks the selected row. Cells that navigate are
`<button class="link">` with a `.t` title and `.a` second line. Digit columns
get `.num` on both `th` and `td`. A sortable header is `th.sortable` with
`aria-sort` and a button inside; the page script reorders the rows.

```html
<div class="table-wrap"><table class="table">
  <thead><tr>
    <th class="sortable" aria-sort="none"><button>Title</button></th>
    <th>Verdicts</th>
    <th class="sortable num" aria-sort="descending"><button>Words</button></th>
  </tr></thead>
  <tbody>
    <tr class="is-current">
      <td><button class="link"><div class="t">Always on My Mind</div><div class="a">Carys Green</div></button></td>
      <td><span class="marks"><span class="mark good is-win"></span><span class="mark bad"></span></span></td>
      <td class="num">99</td>
    </tr>
  </tbody>
</table></div>
```

### Bar chart

`.chart` holds an `h3`, a `.sub` and `.bars`. Each `.bar-row` is a 60px key, a
track and a 56px value with a `<small>` percentage. Fills are accent by
default, `.muted` for a baseline category, `.ok` / `.warn` / `.bad` for state.
Several `.bar-fill`s in one track stack. Keys longer than one short word need
`.bars.wide-key`. An expected value is a dashed `.expect` line inside
`.expect-wrap`, with `.has-expect` on `.bars` to make room for its label.
Every row carries `data-tip` or `title` with the underlying counts.

```html
<div class="chart">
  <h3>Winning slot</h3>
  <div class="sub">all 43 books · dashed line is the expected share</div>
  <div class="bars has-expect">
    <div class="expect-wrap"><span class="expect" style="left:33.3%"></span><span class="expect-label" style="left:33.3%">33% expected</span></div>
    <div class="bar-row" data-tip="31 of 43 · 72%"><span class="k">Variant 0</span><span class="bar-track"><span class="bar-fill" style="width:72%"></span></span><span class="v num">31<small>72%</small></span></div>
    <div class="bar-row" data-tip="7 of 43 · 16%"><span class="k">Variant 1</span><span class="bar-track"><span class="bar-fill muted" style="width:16%"></span></span><span class="v num">7<small>16%</small></span></div>
  </div>
</div>
```

Stacked: `<span class="bar-track"><span class="bar-fill ok" style="width:62%"></span><span class="bar-fill warn" style="width:18%"></span></span>` with a legend above.

### Ladder

Ordered levels, each with a count. The left border shows the level's state
(`.good`, `.caution`, `.bad`, `.accent`) and the `.track` shows its share.

```html
<div class="ladder">
  <div class="rung good"><span class="lab">Sweet<small>attraction, nothing physical</small></span><span class="n num">388</span><span class="track"><i style="width:34%"></i></span></div>
  <div class="rung bad"><span class="lab">Explicit</span><span class="n num">41</span><span class="track"><i style="width:4%"></i></span></div>
</div>
```

### Heatmap grid

`table.heat`. Each cell sets `--v` to a fraction from 0 to 1, which mixes the
accent into `--surface-2`. Add `.hot` above about 0.6 so the text flips to
`--accent-ink`, `.z` for zero, and `.diag` to outline the cells that matter.

```html
<table class="heat" aria-label="Predicted against true rung">
  <thead><tr><th></th><th>Pred 0</th><th>Pred 1</th></tr></thead>
  <tbody>
    <tr><th scope="row">True 0</th><td class="diag hot" style="--v:.9">18</td><td style="--v:.15">3</td></tr>
    <tr><th scope="row">True 1</th><td style="--v:.3">6</td><td class="diag hot" style="--v:.7">14</td></tr>
  </tbody>
</table>
```

### Progress

```html
<div class="progress good"><span class="track"><i style="width:100%"></i></span><span class="v num">43 of 43 judged</span></div>
```

### Tooltip

One `<div class="tip" id="tip" role="tooltip"></div>` at the end of the body.
The page script fills it from `data-tip` on pointer enter, positions it from
the pointer, and toggles `.on`. `example.html` has the script.

## Prose and code

### Running copy

`.reading` (15px / 1.65, 64ch) for a lead's argument; `.copy` (15px / 1.6,
62ch, strong at 700) for quoted material inside a card. Copy says what the
numbers show and where they stop.

### Folds

`<details class="fold">` with a `<summary>` that is a flex row: label on the
left, `.sum-right` (muted count or hint) on the right, a plus or minus marker.
The body uses `.fold-grid` (1.4fr / 1fr) and `.block` (eyebrow + 14px prose).
For context the reader needs some of the time: inputs, source material,
configuration.

```html
<div class="folds">
  <details class="fold">
    <summary>Book context<span class="sum-right">synopsis, themes, tone</span></summary>
    <div class="fold-body"><div class="fold-grid">
      <div class="block prose"><span class="eyebrow">Synopsis</span><p>…</p></div>
      <div><div class="block"><span class="eyebrow">Themes</span><ul><li>…</li></ul></div></div>
    </div></div>
  </details>
</div>
```

### Code

`code` inline and `pre` blocks use the same family at 13px on `--surface-2`,
so surface and size tell them apart rather than a monospace face. For a before
and after comparison use `.code-pair`, with `.proposed` on the column that
should carry the accent border.

```html
<div class="code-pair">
  <div><span class="eyebrow">Current</span><pre><code>…</code></pre></div>
  <div class="proposed"><span class="eyebrow">Suggested</span><pre><code>…</code></pre></div>
</div>
```

### Page foot

`.page-foot`: an `h3` and two or three paragraphs at 74ch, above a
`--line-2` rule. Say what the page shows, what the numbers rest on, and what
they cannot show.

## Responsive

One breakpoint at 1100px: the top bar wraps and drops its metadata, the split
stacks with the list capped at 40vh, the two-column grids collapse, and
paddings tighten. Add nothing else unless the content demands it.
