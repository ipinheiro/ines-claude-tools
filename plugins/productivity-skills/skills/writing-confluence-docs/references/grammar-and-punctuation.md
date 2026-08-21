# Grammar and punctuation

British conventions, adapted from the Google developer documentation style guide. Where the two disagree, this file says so and gives the reason.

## Grammar

### Present tense

Describe what the software does, not what it will do. The reader is running it now.

| Write | Not |
|-------|-----|
| The command returns a job ID | The command will return a job ID |
| If the check fails, the run stops | If the check fails, the run will stop |
| The sync job runs every morning | The sync job is going to run every morning |

Reserve the future tense for things that genuinely have not happened: "We will complete a DPIA before go-live."

### Active voice

Name the thing doing the acting. Passive voice hides it, and in technical writing the actor is usually the information the reader wanted.

| Write | Not |
|-------|-----|
| The sync job writes to PostgreSQL | PostgreSQL is written to |
| Vault issues short-lived credentials | Short-lived credentials are issued |
| Editors approve the copy before submission | The copy is approved before submission |

To spot it: if you can add "by zombies" after the verb and the sentence still parses, it is passive.

Passive is right when the actor is genuinely unknown or irrelevant: "The file was corrupted in transit."

### Sentence structure

One idea per sentence. Put the subject and verb near the beginning. Keep the conditional clause first: "If the run fails, check the DLQ."

Don't stack nouns. "Marketing copy generation pipeline failure alerting configuration" is five nouns deep and unparseable. Break it up with prepositions: "configuring alerts for failures in the marketing copy pipeline".

Keep the helper words that prevent ambiguity. "Verify that the queue is empty" is clearer than "verify the queue is empty", and translates better.

### That and which

`that` defines which one you mean, and takes no comma. `which` adds an aside, and takes one.

- "The column that the filter operates on" - tells you which column.
- "The work queue, which holds about 4,000 titles, drains overnight" - the aside could be deleted without changing what "the work queue" refers to.

If you can drop the clause and the sentence still points at the same thing, it is a `which` clause and needs its comma.

### Collective nouns

British usage lets a collective noun take a plural verb when the members act individually, and a singular verb when the group acts as one unit. Both are correct. Be consistent within a page.

- "The US GDH team ingest CloudTrail logs into Datadog" - the people do it.
- "The DSA team owns the Snowflake datasets" - the team as an entity.

### Pronouns

Use they/them for a person whose pronouns you do not know. Never guess from a name.

Make sure every pronoun has one possible antecedent. "The sync job queries Snowflake and writes to PostgreSQL, which runs every morning" leaves the reader guessing what runs every morning. Repeat the noun instead.

### Anthropomorphism

Software does not want, think, know, believe, or decide. It detects, returns, rejects, retries, and records.

| Write | Not |
|-------|-----|
| The scheduler detects that the run failed | The scheduler knows the run failed |
| The validator rejects malformed UTF-8 | The validator doesn't like malformed UTF-8 |
| The agent returns a structured output | The agent tries to give you a structured output |

### Contractions

Fine, and they make a page read faster: `doesn't`, `you'll`, `it's`, `don't`. Avoid awkward ones that slow the reader down: not `it'd`, not `there're`.

`it's` is "it is". `its` is possessive. There is no such word as `its'`.

## Punctuation

### Em dashes and en dashes

Do not use them. Use a spaced hyphen ` - `, a comma, brackets, or two sentences.

For number ranges write `to`: "5 to 10 minutes", "2012 to 2016". This avoids the en dash question entirely and reads aloud correctly.

### Commas

**Serial comma**, always: "ingestion, orchestration, and export". Without it, "the queue, ingestion and preprocessing pods" could be two things or three.

**After an introductory word or phrase**: "Finally, deploy the chart." "Based on the priority order, the queue picks the next ISBN."

**Before a coordinating conjunction joining two independent clauses**: "The libraries make ingestion easier, and they validate the manifest." Drop it when both clauses are very short.

**Around a non-restrictive clause**: see `that` and `which` above.

**Not before `because`**, unless the sentence would otherwise be ambiguous.

### Full stops

End every sentence. In lists, end an item only if it is a sentence; see `formatting.md`.

Acronyms and initialisms take no full stops: `API`, `DLQ`, `UAT`, `PRH`. British usage also drops the full stop from contractions that end in the same letter as the full word: `Mr`, `Dr`, `Ltd`. Shortened words that do not keep the final letter keep the point: `etc.`, `vol.`

### Colons

A colon introduces a list or an explanation. Whatever precedes it must be a complete sentence.

What follows a colon starts lowercase, unless it is a proper noun, a heading, a quotation, or a label such as **Note:**.

- Right: "The pipeline has three stages: fetch, preprocess, and summarise."
- Wrong: "The three stages are: fetch, preprocess, and summarise." The lead-in is not a sentence.

### Semicolons

Use sparingly. A semicolon joins two independent clauses that belong together: "The variable must have a value; otherwise, the server returns an error."

Most semicolons are better as full stops. If you are using one to hold together a long sentence, split the sentence instead.

### Apostrophes

Possessive of a singular noun: `the pipeline's output`. Plural noun ending in s: `the editors' folder`. Plural not ending in s: `the children's imprint`.

Acronyms pluralise with a bare `s`: `APIs`, `DLQs`, `ISBNs`. Never `API's` unless you mean something belonging to the API.

**Never inflect a code identifier.** Add a noun and inflect that instead.

| Write | Not |
|-------|-----|
| The `ADDRESS` constant's value | `ADDRESS`'s value |
| Send a `POST` request | `POST` the data |
| The `edition_id` values | The `edition_id`s |

### Quotation marks

Straight marks, never curly. Curly quotes break when pasted into a terminal or a config file.

Double quotes by default. Single quotes only for a quote inside a quote, or where the language being shown uses them.

**Punctuation goes outside the closing quote** unless it belongs to the quoted material. This is the British convention. Google, writing American English, puts commas and full stops inside; we do not, because the British rule is the only one that stays correct around literal strings and error messages.

- "Alice sees the message "Content has been modified by another user"."
- "If you enter `escape`, the program exits."

Use quotation marks for the title of a section you cannot link to, and for a direct quotation. Use code font for anything literal. Use italics for the title of a full-length work.

### Hyphens

**Hyphenate a compound modifier before a noun**, not after.

- "a source-anchored extraction" but "the extraction is source anchored"
- "a well-designed schema" but "the schema is well designed"
- "a 64-bit system", "a five-minute wait"

**Never after an adverb ending in -ly**: "publicly available endpoints", "automatically generated copy".

**Prefixes usually close up**: `preprocess`, `nonfiction`, `multiregion`, `reusable`. Hyphenate after `self-` and `cross-`, before a capital or a number, and where the closed form would be misread: `self-managing`, `cross-region`, `non-Google`, `post-2000`, `re-mark`.

**Compound nouns close up** where usage has settled: `webpage`, `hostname`, `workaround`, `backlist`, `frontlist`.

**Suspended hyphens** take a space after, not before: "one- or two-hour intervals".

Never put spaces around a hyphen inside a compound. The spaced hyphen ` - ` is punctuation between clauses, which is a different job.

### Parentheses

Use sparingly. The sentence must still work if the bracketed text is deleted. If it does not, the content is not an aside and belongs in the sentence.

Nested parentheses are a sign the sentence needs splitting.

### Slashes

Avoid. `and/or` almost always means `or`. `read/write access` is fine as an established compound; `the editor/reviewer` is not, so say "the editor or the reviewer".

### Ellipses

Only for genuinely truncated output in an example. Never as a pause in prose.

### Exclamation marks

Never, outside a quoted error message or a code sample.

## Abbreviations and acronyms

Spell out on first use with the abbreviation in brackets, then use the abbreviation: "human in the loop (HITL) review is mandatory". Do this per page, not per document set, because readers arrive mid-tree.

Terms the audience uses daily do not need expanding: `API`, `JSON`, `SQL`, `URL`, `HTML`, `CSV`, `PDF`. Terms that do: `HITL`, `DLQ`, `IRSA`, `HWM`, `ONIX`, `NDCG`, `DPIA`, `SLO`.

**Write "for example" and "that is", not `e.g.` and `i.e.`** They are frequently confused, they read as legalese, and the punctuation around them is contested: this wiki already carries both `e.g.,` and `e.g.` on one page. Spelling them out removes the question.

Rewrite around `etc.` where you can. A list ending in `etc.` usually means the author stopped thinking; either finish the list or introduce it with "such as".

Never use an acronym as a verb. Not "we DLQ'd the record", but "we wrote the record to the dead-letter queue".
