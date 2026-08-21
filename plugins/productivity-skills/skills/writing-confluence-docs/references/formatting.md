# Formatting

Typographic conventions. For the Confluence macros that render them, see `confluence-mechanics.md`.

## Headings and titles

Sentence case, always. Capitalise the first word and any proper noun, nothing else.

Do not skip levels. A page that goes `H2` then `H4` has a broken outline and a broken table of contents.

Headings are link targets, and other pages link to them. Rewording a heading breaks those links, so word it well the first time and leave it alone.

A heading phrased as a question is good where the section answers that question: "Why both Snowflake and PostgreSQL?", "What is an asset?". Do not phrase a heading as a question the section does not answer.

Headings should make sense read on their own, as a list, with no surrounding text. That is how the table of contents presents them.

## Lists

**Bulleted** for items with no inherent order. **Numbered** for sequences and for anything referred to by number later. **Description lists** for term-and-definition pairs.

Introduce a list with a complete sentence, then a colon. Do not use a fragment that the list items complete.

- Right: "You can do any of the following with the API:" followed by "Create an item.", "Delete an item."
- Wrong: "Use the API to:" followed by "Create item", "Delete item".

Start each item with a capital letter, unless case carries meaning, as it does for a code identifier.

End an item with a full stop only if it is a sentence. Single words, short fragments, code, and link text take no full stop. Be consistent within one list: if one item needs a full stop, either give them all one or rewrite the list so none does.

Keep items parallel. If one starts with a verb, they all start with a verb.

Nest sparingly, and never more than two levels. A third level means the content wants to be sections.

## Procedures

Numbered steps. One action per step. Start each step with an imperative verb.

Put the location before the action, and the goal before the action:

- "In Dagster, click **Launch**." Not "Click **Launch** in Dagster."
- "To rerun last Monday, change the date in the form." Not "Change the date in the form to rerun last Monday."

Mark an optional step with `Optional:` at the start, not `(Optional)`.

State the result in the same step as the action that causes it: "Click **Run**. The results appear when the query finishes."

Do not write `please`. Do not use directional language such as "above", "below", or "on the right", because layout changes and screen readers do not follow it. Link to the section instead.

Give one way to do the thing, not three. See "Be prescriptive" in `SKILL.md`.

A single-step procedure is not a numbered list. Write it as one sentence.

## Tables

Give the header row column names in the reader's terms: `What you'll learn`, `Rationale`, `Plain English`, `Fix`. Not `Column 1`, and not `Description` when something more specific exists.

Sentence case in cells. No full stop unless the cell is a sentence.

Keep cells to a phrase or a sentence. A cell that needs a paragraph is content that wants to be prose under a heading.

Beyond about five columns a table stops working on a laptop, let alone a phone. Split it, or use a description list.

Every table needs a lead-in sentence saying what it contains. A table dropped into a page with no introduction makes the reader work out its purpose from the contents.

## Bold, code font, and italics

| Formatting | Use for |
|------------|---------|
| **Bold** | UI element names: buttons, menus, tabs, field labels, dialog titles |
| `Code font` | Anything typed, returned, or literal: identifiers, filenames, paths, commands, values, HTTP status codes, environment variables |
| *Italics* | The title of a full-length work, and a term at the moment you define it |
| No formatting | Product and service names, domain names, URLs the reader navigates to |

Never underline. On the web it means a link.

Do not bold whole sentences for emphasis, and do not use bold as a substitute for a heading on every list item.

### What gets code font

Identifiers (`edition_id`), class and method names (`MarketingCopyAgent`, `push_copy_text`), filenames and paths (`definitions.py`, `resources.yaml`), commands and utilities (`kubectl`, `make local`), environment variables (`GITLAB_TOKEN`), data types (`STRUCT`), literal values (`true`, `null`, `409 Conflict`), and placeholders (`EDITION_ID`).

Not: product names (Snowflake, Datadog, Box), domain names, or a conceptual reference to a component rather than the identifier for it.

### Never inflect a code identifier

Add a noun and inflect that instead. See `grammar-and-punctuation.md` for the full rule.

## UI elements

Bold the element, and use the verb that matches the interaction.

| Verb | For |
|------|-----|
| Click | Buttons, links, menu items |
| Select | Checkboxes, radio buttons, options in a list |
| Enter | Text typed into a field |
| Press | Keyboard keys: "Press Control+C" |
| Tap | Touchscreens only |

Prepositions follow the container: **in** a dialog, field, list, menu, or pane; **on** a page, tab, or toolbar.

For a menu path, write it out: "In the **File** menu, select **Open**."

## Numbers

Spell out zero to nine. Use numerals from 10 up.

Always use numerals, whatever the size, for versions (`v2.0`), measurements (`5 GB`, `6 queries per second`), percentages (`40%`), money, and anything the reader will compare against a number on a screen.

Do not start a sentence with a numeral. Spell it out or, better, rewrite the sentence.

Write ordinals out: first, second, twelfth. Not 1st, 2nd, 12th.

Ranges take `to`: "5 to 10 minutes", "2012 to 2016". This keeps the em dash ban intact and reads aloud correctly.

Group thousands with commas: `18,000,000`. Put a leading zero on a decimal below one: `0.3`, not `.3`.

Put a space between a number and its unit: `200 GB`, `90k words`, `5 minutes`.

## Dates and times

Dates are `YYYY-MM-DD`: `2026-08-18`. Never `18/08/26`, which reads as a different date in the US, and never a spelled-out month.

Times are 24-hour: `14:15`, not `2:15 PM`.

Machine timestamps are ISO 8601 with a timezone: `2026-08-18T14:15:00Z`.

Give a timezone only when it matters, and then give the region and offset rather than an abbreviation: "UK time (UTC+1)", not "BST".

Durations are words: "10 minutes", "24 hours", "8 to 12 months".

Do not use seasons. They are inverted in the southern hemisphere, and this is a global company. Write months, quarters, or a phase name: "November and December", "Q4", "Phase 1".

Do not write relative dates such as "last Tuesday", "next quarter", or "since last month" in reference documentation. They are wrong the day after they are written. Give the date.
