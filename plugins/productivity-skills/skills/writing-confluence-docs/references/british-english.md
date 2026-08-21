# British English

We write in British English. The house preference is `-ise`, not the Oxford `-ize`, even though both are correct in British usage. Consistency inside a page matters more than either choice, and `-ise` is what the wiki already uses.

## What never changes

This list matters more than the spellings below. Getting it wrong breaks code or misquotes someone.

Leave American spelling exactly as written in:

- **Code identifiers**: `serialize()`, `normalize_text`, `ALLOWED_TAGS`, `MarketingCopyOutput`
- **API fields and JSON keys**: `"organization_id"`, `"color"`
- **CSS properties and values**: `color`, `text-align: center`
- **Config keys, environment variables, and CLI flags**: `--optimize-level`, `DAGSTER_COLOR`
- **Library, product, and service names**: AWS `Analyzer`, DOMPurify, Datadog, `dagster-resource-config`
- **File and directory paths**
- **Anything inside a code block or an inline code span**
- **Quoted text from elsewhere**: error messages, log lines, third-party documentation, someone else's words

Rule of thumb: if changing the spelling would break something or misquote someone, don't change it.

The failure this prevents is real. One page on this wiki says "HTML is sanitized at two layers" in prose two lines above "DOMPurify sanitises before save requests". Both are prose, so both should be `sanitised`. The `ALLOWED_TAGS` constant a paragraph later stays exactly as the code has it.

## Spellings

### -ise, -isation

| British | American |
|---------|----------|
| summarise, summarisation | summarize, summarization |
| normalise | normalize |
| sanitise, sanitisation | sanitize, sanitization |
| serialise, deserialise | serialize, deserialize |
| organise, organisation | organize, organization |
| prioritise, prioritisation | prioritize |
| initialise | initialize |
| authorise, authorisation | authorize |
| optimise, optimisation | optimize |
| minimise, maximise | minimize, maximize |
| categorise, standardise | categorize, standardize |
| synchronise | synchronize |
| visualise | visualize |
| customise, parameterise | customize, parameterize |
| tokenise, containerise | tokenize, containerize |
| centralise, decentralise | centralize |
| recognise, realise, emphasise | recognize, realize, emphasize |
| specialise, generalise | specialize, generalize |

### -yse

`analyse`, `catalyse`, `paralyse`. The nouns do not change: `analysis`, `analyses`, `analytics`, `analyst`.

### -our

`behaviour`, `colour`, `favour`, `flavour`, `labour`, `honour`, `neighbour`, `rumour`. Derivatives keep the `u` when the ending is added directly: `behavioural`, `colourful`, `favourite`.

### -re

`centre`, `metre`, `litre`, `theatre`, `fibre`, `kilometre`. A device that measures is still a `meter`: a flow meter, a smart meter.

### -ce noun, -se verb

| Noun | Verb |
|------|------|
| licence | license |
| practice | practise |
| defence | (no verb form differs) |

"We hold a licence" but "Snowflake licenses the warehouse". "Our practice is to review first" but "practise the runbook before an incident".

### Doubled consonants

`modelling`, `modelled`, `labelling`, `labelled`, `travelling`, `cancelled`, `signalling`, `levelling`, `fuelled`, `totalled`.

`focused` keeps one `s` in both varieties.

### Other words that come up

| British | Not |
|---------|-----|
| artefact | artifact |
| catalogue | catalog |
| dialogue | dialog (except the UI element `dialog`, and the HTML `<dialog>` tag) |
| grey | gray (but CSS `gray` and hex names stay) |
| enquiry (a question) | inquiry (reserve for a formal investigation) |
| draft (a document) | draught (that is the beer and the cold air) |
| programme (a scheme, a broadcast) | but a computer `program` stays `program` |
| storey (a floor of a building) | story (that is the narrative) |

### Words to simplify rather than translate

`whilst` reads as archaic. Use `while`. `amongst` reads the same way. Use `among`. `utilise` is `use`. `commence` is `start`. `in order to` is `to`. Google's global-audience guidance applies here: plainer words survive translation and non-native readers better, and they read faster for everyone.
