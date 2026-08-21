# Words and terminology

## Prefer the plain word

Shorter words survive translation and non-native readers better, and everyone reads them faster.

| Instead of | Write |
|------------|-------|
| ingest | load, import |
| leverage (verb) | use |
| utilise | use |
| commence, initiate | start |
| terminate | stop, end |
| in order to | to |
| prior to | before |
| subsequent to, following | after |
| in the event that | if |
| at this point in time | now, or cut it |
| a number of | some, or give the number |
| facilitate | help, or name the actual action |
| perform a review of | review |
| make use of | use |
| is able to | can |
| due to the fact that | because |
| blast radius | affected area |
| post-mortem | incident review |

## Hollow nouns

These usually mean the sentence has not been thought through. Name the actual thing.

`solution`, `capability`, `workload`, `offering`, `piece`, `space`, `landscape`, `journey`, `synergy`, `alignment`, `enablement`.

"Plainview is a summarisation solution" says less than "Plainview summarises ePubs and manuscripts". If you cannot replace the hollow noun with something concrete, the sentence has no content.

## Jargon

A specialist term earns its place when readers search for it, when the industry has settled on it, or when the precise term prevents a misreading. Otherwise it is a barrier.

**Used once:** define it in a clause or brackets, or link a definition.

> Outputs are anchored to the source with citations (a verbatim quote plus a paragraph offset).

**Used repeatedly:** define it on first use, then use it freely.

> The system uses optimistic locking, where editing isn't blocked but overwrites are prevented. Optimistic locking means two editors can work at once...

**Never** introduce a term in a glossary at the bottom and use it undefined at the top. Readers do not read bottom-up.

## Don't tell the reader it's easy

Cut `simply`, `just`, `easy`, `easily`, `quick`, `quickly`, `obviously`, `of course`, `clearly`, `merely`, `straightforward`.

They add nothing when the step works, and when it fails they tell the reader the fault is theirs. "Simply run `make local`" becomes "Run `make local`".

The same applies to overclaiming: avoid `seamless`, `effortless`, `powerful`, `world-class`, `best-in-class`, `cutting-edge`.

## Timeless wording

A wiki page needs to withstand the test of time. Anything anchored to the moment of writing rots.

Cut: `currently`, `now`, `at present`, `presently`, `as of this writing`, `new`, `newer`, `latest`, `existing`, `old`, `older`, `recently`, `soon`, `shortly`, `eventually`, `does not yet`, `in the future`.

| Write | Not |
|-------|-----|
| The emulator supports these filters | The emulator now supports these filters |
| These subcommands interact with the load balancer | These new subcommands interact with the load balancer |
| The API doesn't support bulk submission | The API doesn't currently support bulk submission |

Where recency genuinely matters, anchor it to something that stays true: a date, a version, or a release. "Bulk submission is out of scope for Phase 1" beats "bulk submission isn't supported yet".

Release notes, incident reports, and status updates are exempt. They are meant to be read as of a date.

## Inclusive language

| Instead of | Write |
|------------|-------|
| whitelist / blacklist | allowlist / blocklist |
| master (branch, node) | main, primary, controller |
| slave | replica, secondary, worker |
| sanity check | completeness check, validation |
| dummy value | placeholder, sample value |
| man-hours | person-hours |
| manned | staffed |
| mankind | humanity, people |
| grandfathered | legacy, pre-existing |
| native speaker | fluent speaker |
| crazy, insane, mad | surprising, unexpected, baffling |
| dumb, lame | limited, unhelpful |
| blind to | unaware of, doesn't account for |
| cripples, hobbles | slows, limits |
| hangs | stops responding |
| hit (a button) | click, select |

Use they/them for anyone whose pronouns you do not know, including in worked examples. Never infer pronouns from a name.

## Words that mark a machine wrote it

Moved. The `writing-clearly` skill is the single home for machine-written tells, in `references/ai-tells.md`: banned vocabulary, throat-clearing, agency dodging, participial padding, negative parallelism, triads, and vague attribution.

Keeping a second copy here would mean two lists loading together on every wiki page, drifting apart the first time one is updated.

## Team vocabulary

These terms have a precise meaning here. Use them consistently, and capitalise them consistently.

| Term | Meaning |
|------|---------|
| Work | The conceptual grouping of all editions of a book, identified by a Biblio Work ID |
| Edition | One format-specific manifestation of a Work, with its own Edition ID and ISBN-13 |
| ISBN-13 | Always hyphenated in prose. The identifier itself is 13 digits, unhyphenated |
| Biblio | The Virtusales bibliographic system |
| Zembla | The internal search and discovery app |
| Plainview | The summarisation pipeline |
| GDH | Global Data Hub, the US-operated AWS and Snowflake estate |
| DSA | Data Science and Analytics, this team |
| Division | A publishing house within PRH |
| Imprint | A brand within a division |
| Frontlist / backlist | Newly published titles. A frontlist is usually defined by what's been published in the preceding 52 weeks / previously published titles over 52 weeks old |
| Gold example/standard | Curated high-quality copy used for few-shot prompting |
| HITL | Human in the loop. Expand on first use |
| DLQ | Dead-letter queue. Expand on first use |
| ONIX | The book trade metadata standard |
| Thema | The subject classification scheme |

Two things to keep straight, because getting them wrong changes the meaning: a Work is not an Edition, and a division is not an imprint.
