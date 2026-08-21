---
name: writing-clearly
description: This skill should be used when writing or editing prose a person will read - documentation, commit messages, merge request descriptions, release notes, Teams and Slack posts, error messages, docstrings, reports. Also use when a draft reads as stiff, wordy, abstract, or machine-written. Triggers on "make this read better", "tidy this up", "write a summary", "draft a message", "improve this wording", "does this sound like AI".
---

# Writing clearly

Sentence-level craft, from Joseph Williams' *Style: Lessons in Clarity and Grace*. It applies to any prose a person reads: a commit message, a release note, a Teams post, a wiki page.

Most unclear writing is not caused by long words. It is caused by sentences whose grammar does not match their story. Fix the architecture and the vocabulary usually fixes itself.

For the vocabulary and phrasing that mark machine-written prose, read `references/ai-tells.md`. Bring it in when revising anything that will be read outside the team.

## Every sentence tells a story

A clear sentence puts its main character in the subject and that character's action in the verb. Everything below follows from this.

| | |
|---|---|
| Buried | That records were skipped when the API timed out was one of the findings of the analysis. |
| Clear | The analysis found that records were skipped when the API timed out. |

A character need not be a person. An analysis, a pipeline, a policy can all act. Ask who or what is doing something, and make that the subject.

## Name the agent

Passive voice hides the character. Sometimes that is what you want, and sometimes it leaves the reader unable to act.

| | |
|---|---|
| Hidden | The number of attempts can be configured in the settings file. |
| Named | You set the number of attempts in `settings.yaml`. |
| Hidden | No configuration changes are needed on your side. |
| Named | You do not need to change anything. |

Use the passive deliberately: when the agent is genuinely unknown, when it is obvious and dull, or when naming it would break the topic string. Never use it to avoid saying who is responsible.

## Put actions in verbs

A nominalisation is a verb turned into a noun: `calibrate` becomes `calibration`, `decide` becomes `decision`. Each one buries an action and drags in a weak verb to carry the sentence.

| | |
|---|---|
| The mass spectrometer managed the measurement and identification of the proteins. | The mass spectrometer measured and identified the proteins. |
| Our lack of data prevented us from making a prediction about the outcome. | Because we lacked data, we could not predict the outcome. |
| The intention of the committee is to improve morale. | The committee intends to improve morale. |

The same defect wearing a different coat is the elaborate copula. `serves as`, `stands as`, `represents`, `constitutes`, `functions as` are nearly always `is`.

> The library serves as a central store for prompts. → The library stores prompts.

Look for nouns ending `-tion`, `-sion`, `-ment`, `-ness`, `-ity`, `-ance`, `-ence`. Ask whether the noun was once a verb. If it was, turn it back. Common pairs: `make a decision` is `decide`, `perform an analysis` is `analyse`, `provide assistance` is `help`, `conduct an investigation` is `investigate`.

**Keep the nominalisation when it is the subject itself.** `Nominalisation` in linguistics, `alienation` in Marx, `classification` when the classification is the thing you are discussing. The rule targets unnecessary ones.

## Old information first, new information last

Readers understand a sentence by hooking its opening to something they already know. Open on the familiar, close on the unfamiliar.

Disorienting, because every sentence opens on something never seen before:

> Three little pigs lived in a wood. Scrappy, Sparky and Spanky were their names. Bricklaying is difficult, but Scrappy was good at it.

Clear:

> Three little pigs lived in a wood. The pigs were called Scrappy, Sparky and Spanky. Scrappy was a bricklayer. Bricklaying is difficult, but Scrappy was good at it.

Each sentence reaches back before it reaches forward.

## Keep the topic steady

Run your eye down the first few words of consecutive sentences. If they name four different things, the paragraph will feel scattered even when every individual sentence is clean.

| | |
|---|---|
| Scattered | **The team** added a retry. **The number of attempts** is configurable. **The operations team** reviews the logs daily. **The change** reduces manual work. |
| Steady | **The pipeline** now retries a failed call three times. **It** reads the attempt count from `settings.yaml`. **It** logs every retry, so **the operations team** can see failures the next morning. |

This is the single most common defect in otherwise competent technical writing.

**Repairing a topic string means changing sentence boundaries, not swapping words.** Merge the sentences that share a subject, and demote the odd one out into a clause. Expect the number of sentences to drop. If you revise a scattered paragraph and it comes out with the same number of sentences opening on the same number of subjects, you have edited the wording and left the defect in place.

## End on the point

The last few words of a sentence carry the most weight. Put the thing you want remembered there, and never let it trail off into a subordinate clause.

| | |
|---|---|
| Buried | The pipeline rides out short-lived errors and completes normally, which has cut overnight failures. |
| Stressed | The pipeline now rides out short-lived errors, and overnight failures have dropped by half. |
| Buried | The ability to read a patient's symptoms in context is one of the most important skills a doctor develops. |
| Stressed | One of the most important skills a doctor develops is reading a patient's symptoms in context. |

Never end a sentence on `something`, `things`, `aspects`, `factors`, `it`, `this`, or `that`. The strongest position in the sentence deserves your most specific word. When you introduce a technical term, build the sentence so the term lands last.

## Keep subject and verb together

Words wedged between a subject and its verb force the reader to hold everything in memory while waiting for the point.

| | |
|---|---|
| Split | The retry logic, although it does not fire for authentication errors, since those will never succeed on a second attempt, and only applies to the Biblio client, adds up to three attempts. |
| Together | The retry logic adds up to three attempts. It skips authentication errors, which will never succeed on a second attempt, and it applies only to the Biblio client. |

Put the main clause first. Let the qualifications trail behind it, where the reader can absorb them one at a time. If a sentence runs past about 30 words with several clauses stacked mid-way, split it.

## Cut what carries no meaning

| Wordy | Concise |
|-------|---------|
| due to the fact that | because |
| in the event that | if |
| at this point in time | now |
| has the ability to | can |
| it is possible that | may |
| on a daily basis | daily |
| a large number of | many |
| in order to | to |
| for the purpose of | to |
| full and complete | complete |

Also cut, almost always without loss: `kind of`, `really`, `basically`, `actually`, `virtually`, `in a sense`, `certain`, `particular`, `individual`, `given`, `various`.

## Shape the paragraph

A coherent paragraph states its point in the first sentence or two, and every sentence after that advances it. If you can delete a sentence and lose nothing, it did not belong.

You write a first draft to work out what you think. That draft is organised around your thinking, and your reader does not care how you got there. Revising is not polishing the sentences you have. It is reorganising the piece around what the reader needs to know and in what order.

## Rhythm

Use parallel construction for parallel ideas. Vary sentence length, and follow a long sentence with a short one. Three sentences of near-identical length in a row read as a drone. Read it aloud: where you stumble, the reader will too.

End on strength. The last word of a sentence, the last sentence of a paragraph and the last paragraph of a document all carry more weight than their position suggests.

## Red flags

- Four consecutive sentences opening on four different subjects
- A sentence ending in `this`, `it`, `things`, or `aspects`
- `is`, `are`, `was` carrying a sentence whose real action sits in a `-tion` noun
- `can be configured`, `is required`, `will be reviewed` with no one named
- The most important fact in the paragraph sitting in a `which` clause
- More than about 30 words before reaching the main verb

## The revision pass

Revising is not the same as tidying. Tidying changes words and leaves the sentences where they are. Revising is allowed to move them, and usually has to.

Read the draft once looking only at structure, and list the first three words of every sentence. If that list does not name a steady topic, or if an opening does not hook back to something already said, the paragraph needs reordering rather than rewording. Reorder it first, then read again for words.

Then read `references/ai-tells.md` and strip what it lists.
