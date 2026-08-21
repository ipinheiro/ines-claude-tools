---
name: writing-confluence-docs
description: This skill should be used when writing, drafting, editing, or reviewing a page for the team Confluence wiki - solution overviews, technical design docs, UX overviews, how-to guides, runbooks - or when tidying up an existing page. Triggers on "write a Confluence page", "document this in Confluence", "write it up on the wiki", "write up the design", "write the docs", "review this page", "confluence".
---

# Writing Confluence docs

House style for the Data Science and Analytics UK wiki, adapted from the Google developer documentation style guide and from the pages this team already considers good.

It covers how we write, not what shape a page takes. There is no template here: a solution overview and a how-to guide earn their structure from what their readers need, and a skeleton would only produce pages that all sound the same.

Five reference files. Read the ones the work needs.

| File | Covers |
|------|--------|
| `references/british-english.md` | Spellings, and the more important list of things never to respell |
| `references/grammar-and-punctuation.md` | Tense, voice, agreement, that/which, commas, quotes, hyphens, apostrophes |
| `references/words-and-terminology.md` | Jargon, plain-language swaps, hollow words, inclusive language, timeless wording, team vocabulary |
| `references/formatting.md` | Headings, lists, tables, bold and code font, numbers, dates and times |
| `references/confluence-mechanics.md` | Macros, code blocks, the diagram palette, panels, page hierarchy, links |

## The rules that never bend

| Rule | Detail |
|------|--------|
| British spelling in prose | summarise, analyse, behaviour, centre, artefact, catalogue, licence (noun). Never respell code, config keys, or quoted text |
| Dates are `YYYY-MM-DD` | `2026-08-18`. Never `18/08/26`, never `Aug 18, 2026` |
| Times are 24-hour | `14:15`, not `2:15 PM`. Machine timestamps are ISO 8601: `2026-08-18T14:15:00Z` |
| Headings are sentence case | "Where to start", not "Where To Start". Proper nouns keep their capitals |
| No em dashes | Use a spaced hyphen ` - `, or split the sentence in two |
| Serial comma | "ingestion, orchestration, and export" |
| Present tense | "The command returns a job ID", not "will return" |
| Active voice | "The sync job writes to PostgreSQL", not "PostgreSQL is written to" |

## Be prescriptive

Documentation tells the reader what to do. It does not lay out every option and leave them to choose. A page that offers three ways to configure a resource has moved the decision onto someone with less context than the author had.

Pick the path the team actually uses, document that one, and mention alternatives only where the choice genuinely belongs to the reader.

Say precisely how binding each statement is:

| Meaning | Write | Not |
|---------|-------|-----|
| Required | "You must set `approved` to false", or an imperative: "Set `approved` to false" | "should" |
| Recommended | "We recommend one asset per output" | "should" |
| Optional | "You can override the schedule in `resources.yaml`" | "should" |
| Likely outcome | "The job might time out on a large title" | "could possibly" |

"Should" is the problem word. It reads as a requirement to one person and a suggestion to the next. Replace it with `must`, `we recommend`, or `can`.

## Voice

| Who | How to refer to them | Example |
|-----|---------------------|---------|
| This team | **we** | "We chose manual save because the copy goes to an external system." |
| Users and other teams | **third person** | "Editors review the copy and submit it to Biblio." "The US GDH team ingest CloudTrail logs into Datadog." |
| The reader carrying out a step | **imperative** | "Wrap the library in a thin Dagster layer." |
| The reader facing a consequence | **you** | "Get this wrong and you'll be redeploying to change a date." |

"You" is for consequences and context, never for narrating steps. Write "Add the resource to `definitions.py`", not "You'll want to add the resource to `definitions.py`".

Never write "the user" when a role will do. Say "editors", "metadata managers", "Zembla search users".

Contractions are fine and make the page read faster: "doesn't", "you'll", "it's". Do not make the software want, think, or decide things. The scheduler does not "know" the run failed; it detects that the run failed.

## What makes a page good

**Open on the reader's situation, not a definition.** The first paragraph should describe where the reader is standing and why they came here. "You have a Python package that trains models, loads data, uploads predictions. It works. Now you want it running on the platform every day without you thinking about it."

**State the scope, and state the non-scope with a reason.** Every good page on this wiki does this. One line is enough for a guide: "This guide doesn't cover deployment, Kubernetes, or CI/CD. For that, see Deploying a Code Location." For a design doc, a table with a `Rationale` column is better, because "why not" is the question readers actually ask. An out-of-scope list without reasons reads as an oversight rather than a decision.

**Give every decision a "Why X?" heading.** Not "Database choice" but "Why both Snowflake and PostgreSQL?". State the decision, then number the reasons. Where alternatives were weighed, say which ones and why they lost. A reader who disagrees with a decision needs to know whether their objection was already considered.

**Explain interactions with a concrete scenario.** Name the actors and give real times. "Alice opens the copy editor at 10:00. Bob opens the same book at 10:05 and saves at 10:15. When Alice tries to save at 10:20, she sees a conflict notification." Then say what each person sees. This beats any abstract description of optimistic locking.

**Put anything enumerable in a table.** Error messages, states, endpoints, risks, out-of-scope items, glossary terms. See `references/formatting.md` for how to build one.

**Define the vocabulary.** If the page uses a term a new starter would not know, it needs a glossary. Give a plain-English definition and, where the term is a domain identifier, an example: "Work: the conceptual grouping for all editions of a book published by PRH, identifiable by a Biblio Work ID. Example: The Secret of Secrets by Dan Brown, Work ID 442981."

**Mark what is unfinished.** An "Open questions" section with owners beats a page that reads as complete but isn't. Never leave a bare `????` in the body.

## Grammar and punctuation

Full detail in `references/grammar-and-punctuation.md`. The rules that come up on nearly every page:

- **Conditions before instructions.** "If the run fails, check the DLQ", not "Check the DLQ if the run fails". Same for location and purpose: "In Dagster, click **Launch**"; "To rerun last Monday, change the date in the form".
- **`that` defines, `which` adds.** "The column that the filter operates on" restricts which column. "The queue, which holds about 4,000 titles, drains overnight" adds an aside, and takes a comma.
- **Punctuation goes outside a closing quote** unless it belongs to the quoted material. This is the British convention, and it is the only one that is safe around literal strings.
- **Straight quotes, doubles by default.** Never curly quotes: they break when pasted into a terminal.
- **Write "for example" and "that is",** not `e.g.` and `i.e.`. This wiki currently has both `e.g.,` and `e.g.` on the same page; spelling them out ends the argument.
- **Hyphenate a compound modifier before a noun,** not after. "A source-anchored extraction" but "the extraction is source anchored". Never hyphenate after an `-ly` adverb: "publicly available endpoints".
- **Spell out an acronym on first use** unless the audience uses it daily. HITL, DLQ, and IRSA need expanding. API, JSON, and SQL do not.

## Words

Full lists in `references/words-and-terminology.md`.

**Prefer the plain word.** `ingest` is `load` or `import`. `leverage` is `use`. `utilise` is `use`. `commence` is `start`. `in order to` is `to`. Shorter words survive translation and non-native readers better, and they read faster for everyone.

**Introduce jargon, or drop it.** A specialist term earns its place when readers search for it or the industry has settled on it. On first use, define it in a clause or link a definition: "optimistic locking, where editing isn't blocked but overwrites are prevented". Vague nouns like "solution", "workload", and "capability" usually mean the sentence has not been thought through.

**Write as if the page will be read in two years.** Cut `currently`, `now`, `new`, `newer`, `latest`, `existing`, `soon`, `eventually`, `at present`, `as of this writing`. "The emulator supports these filters", not "the emulator now supports". Where recency genuinely matters, give a date or a version instead.

**Don't tell the reader it's easy.** Cut `simply`, `just`, `easy`, `quick`, `obviously`, `of course`. If it goes wrong for them, the page has called them stupid.

**Inclusive language.** `allowlist` and `blocklist`, not whitelist and blacklist. `main` or `primary`, not master. A `sanity check` is a completeness check. A `dummy value` is a placeholder. Avoid `crazy`, `insane`, `blind to`, `cripples`. Use they/them where a person's pronouns are unknown, and vary the names in examples.

**Words that mark a machine wrote it.** The `writing-clearly` skill owns this, along with sentence architecture: characters as subjects, actions as verbs, and where the emphasis in a sentence lands. Use it alongside this one for anything longer than a paragraph.

## Red flags

| If you catch yourself | Do this instead |
|-----------------------|-----------------|
| Opening with "X is a framework that..." | Open on the reader's situation |
| Writing "should" | Decide: `must`, `we recommend`, or `can` |
| Listing three ways to do the same thing | Pick the one the team uses and document that |
| Writing an out-of-scope list with no reasons | Add a `Rationale` column |
| Heading a section "Database choice" | Head it "Why both Snowflake and PostgreSQL?" |
| Describing a race condition abstractly | Write the scenario with named people and times |
| Typing a hyphen pair or an em dash | Use a spaced hyphen, or two sentences |
| Typing `e.g.` or `i.e.` | "for example", "that is" |
| Writing "currently" or "the new endpoint" | Cut it, or give a date or version |
| Writing "simply run" or "this is easy" | Cut the adverb |
| Writing "the user" | Name the role |
| Writing "You'll want to run..." | "Run..." |
| Hand-writing a table of contents | Use the TOC macro |
| Respelling `serialize()` or `color:` to British | Leave code alone |
| Pasting a diagram without a language fence | Fence it as mermaid and apply the palette |

## Before you publish

- [ ] Every heading is sentence case
- [ ] No em dashes, no curly quotes anywhere in the body
- [ ] Every date is `YYYY-MM-DD`, every time 24-hour
- [ ] British spelling in prose, American spelling untouched inside code, config keys, and quotes
- [ ] No `should`: every instruction is a `must`, a `we recommend`, or a `can`
- [ ] No `currently`, `new`, `latest`, `simply`, `just`, or `easy`
- [ ] No `e.g.` or `i.e.`
- [ ] Scope and non-scope are both stated, and non-scope has reasons
- [ ] Every significant decision has a "Why X?" heading with its reasons
- [ ] Every acronym is expanded on first use, or is one the audience uses daily
- [ ] Terms a new starter wouldn't know are in a glossary
- [ ] Every link has descriptive text
- [ ] Every code block declares its language
- [ ] Every diagram is fenced as mermaid and uses the house palette
- [ ] Any table of contents is the macro, not hand-written anchors
- [ ] No `TBD`, `????`, or empty section left in the body without an owner in "Open questions"
