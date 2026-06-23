---
name: word-poem
description: "Write a short, playful 4-line poem about a given word, weaving in one of its anagrams. Use this skill for the final stage of the Word Explorer workflow: when /workspace/state.json (the analyzed word) and /workspace/anagrams.json (words formable from its letters) exist and a creative summary is wanted. Triggers: 'write a poem', 'word poem', 'final creative step'."
---

# Word Poem

## Purpose

Produce a short, fun 4-line poem about a word, using one of its anagrams as a twist.

## Inputs

- `/workspace/state.json` — `{ word, length, vowel_count, ... }` from the analyze step.
- `/workspace/anagrams.json` — `{ word, anagrams: [...] }` from the MCP step (the list may be empty).

## Workflow

1. Read `word` from `/workspace/state.json`.
2. Read the `anagrams` list from `/workspace/anagrams.json`.
3. Write a 4-line poem about `word`. If the anagrams list is non-empty, weave in at least
   one anagram (a different word made from the same letters).
4. Save the poem to `/output/poem.md` (markdown, the poem only). Files written to
   `/output` — other than control files like `result.json` — become downloadable
   Output Files on this step, so this is the deliverable the user downloads.
5. Also write `/output/result.json` as
   `{ "status": "success", "word": <word>, "poem": <the poem text> }`.

## Constraints

- Exactly 4 lines. Keep it playful and clean.
- Do not invent anagrams — only use entries from `anagrams.json`.
