# Machine-written tells

Patterns that are statistically overrepresented in generated text. Readers who see a lot of it spot them quickly, and prose carrying several of them reads as unowned regardless of whether a person wrote it.

Trimmed to what we actually write: documentation, commit messages, merge requests, release notes, reports, Teams and Slack posts. The social-media varieties (engagement bait, humble-brag framing, thought-leadership hooks) are left out because we do not write for that surface.

## Vocabulary

Never use these in prose. Each one is an abstract placeholder standing where a specific word should be. `robust` says nothing; `survives a dropped connection` says something.

**Significance inflation:** pivotal, crucial, vital, key (as an adjective), essential, imperative, testament, indelible mark, turning point, setting the stage for, evolving landscape, focal point, deeply rooted, cornerstone

**Filler verbs:** delve, garner, bolster, foster, underscore, showcase, encompass, cultivate, leverage, utilise, streamline, facilitate, navigate (figuratively), embark, elevate, empower, unpack

**Promotional adjectives:** vibrant, intricate, meticulous, groundbreaking, renowned, profound, rich (abstract), robust, comprehensive, innovative, transformative, seamless, cutting-edge, holistic, nuanced, multifaceted, impactful, actionable

**Hedged emphasis:** highlighting, underscoring, emphasising, reflecting, symbolising, ensuring, enhancing, contributing to

**Abstract nouns:** landscape, realm, paradigm, tapestry, synergy, catalyst, ecosystem, journey, endeavour

Replace with the plain word, or cut and let the fact carry itself. `important` for `crucial`. `detailed` for `meticulous`. `shows` for `showcases`.

## Throat-clearing

Openings that delay the sentence. Delete the phrase and start with the subject.

`it's important to note`, `it's worth noting`, `it should be noted`, `let's dive in`, `dive into`, `when it comes to`, `in the realm of`, `at the end of the day`, `it goes without saying`, `first and foremost`, `last but not least`, `without further ado`, `in today's rapidly evolving`, `here's the thing`, `what this means is`, `to be clear`, `the key here is`, `that said`, `in conclusion`, `to summarise`

If a reader can see it is the end, `in conclusion` adds nothing.

## Agency dodging

Verbs that describe a capability instead of an action, leaving nobody doing anything.

`allows`, `enables`, `ensures`, `provides`, `serves as`, `facilitates`, `supports` (when it means "does")

> The allowlist allows the agent to run safely. → The agent runs inside an allowlist.

> This provides visibility into failures. → You can see which records failed.

See "Name the agent" in `SKILL.md`. This is the same defect at the level of word choice.

## The pronoun crutch

`This` plus an abstract noun, used to open a sentence rather than name the thing.

`This approach`, `This constraint`, `This architecture`, `This means that`, `This ensures`

> This constraint forces specificity. → Writing the query as a file forces specificity.

The reader has to look backwards to work out what `this` refers to. Name it instead.

## Participial padding

An `-ing` clause bolted to the end of a sentence, performing analysis rather than adding information.

| Padded | Plain |
|--------|-------|
| The team released v2.0, highlighting the importance of backwards compatibility. | The team released v2.0 with full backwards compatibility. |
| Revenue grew 15%, underscoring the company's strong market position. | Revenue grew 15%. |
| The API supports pagination, ensuring efficient retrieval. | The API supports pagination. |

Cover the clause with your hand. If the sentence still says everything it needs to, delete the clause.

## Negative parallelism

`Not just X, but Y` argues against a claim nobody made. State Y.

> This is not just a refactor, but a fundamental rethinking of the schema. → We redesigned the schema.

> The update doesn't merely fix bugs, it transforms the experience. → The update fixes the sync bug and redesigns the dashboard.

Watch for `not only... but`, `it's not... it's`, `more than just`.

## Triads

Three adjectives or phrases in a row, with evidence for none of them.

> The framework is fast, flexible and reliable. → The framework handles 10k rows a second.

Two is fine. If all three genuinely matter, give each one its own sentence and its own evidence.

## Transitions used as decoration

`moreover`, `furthermore`, `additionally`, `consequently`, `nevertheless`, `nonetheless`, `thus`, `hence`, `subsequently`, `likewise`, `conversely`

None is wrong alone. Clustering them is the tell. At most one per paragraph, and prefer to show the relationship by putting the two sentences next to each other. If you have to announce that two ideas are connected, the ordering failed.

## Vague attribution

Name the source or drop the claim.

| Vague | Grounded |
|-------|----------|
| Experts argue this approach is more efficient. | Our benchmark ran it three times faster. |
| Industry reports suggest growing adoption. | Adoption grew 40% in 2025 (State of JS). |
| It is widely considered best practice. | [Cut, or cite who considers it so.] |

## Echo closers

A short final sentence restating what the paragraph just said. `The current system has none.` `Ambiguity breaks it.` `That is the whole point.`

Not banned outright, because occasionally one lands. At most once in a piece. More than that and the writing sounds like it is applauding itself.

## Structural tells

**Bold as a substitute for structure.** Bold marks genuine emphasis or a UI label. It is not a heading, and it does not belong at the front of every bullet in a list.

**Everything formatted as a list.** Prose that flows as an argument should be paragraphs. Lists are for items that are genuinely parallel and genuinely unordered.

**Title Case Headings.** Sentence case, always.

**Em dashes.** House rule: never. Use a spaced hyphen, a comma, brackets, or two sentences.

## The scan

Before sending anything outward, search the draft for: the vocabulary list above, `it's important to note`, `allows`, `ensures`, `This ` at the start of a sentence, `, ensuring`, `, highlighting`, `not just`, and any em dash.
