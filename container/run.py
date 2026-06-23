#!/usr/bin/env python3
"""Step 2 (analyze): deterministic word stats — no LLM.

Reads {"word": ...} from /output/input.json (the human step's output), computes
basic stats, and writes them to /workspace/state.json (shared with later steps)
and /output/result.json (this step's own output).
"""

from __future__ import annotations

import json
from pathlib import Path

OUTPUT_DIR = Path("/output")
WORKSPACE_DIR = Path("/workspace")
VOWELS = set("aeiou")


def read_input_word() -> str:
    input_path = OUTPUT_DIR / "input.json"
    step_input = json.loads(input_path.read_text(encoding="utf-8")) if input_path.exists() else {}
    word = step_input.get("word")
    if not isinstance(word, str) or not word.strip():
        raise SystemExit("No 'word' found in /output/input.json — the human step must provide one.")
    return word.strip().lower()


def main() -> None:
    word = read_input_word()
    letters = [character for character in word if character.isalpha()]
    stats = {
        "word": word,
        "length": len(letters),
        "vowel_count": sum(1 for character in letters if character in VOWELS),
        "consonant_count": sum(1 for character in letters if character not in VOWELS),
        "sorted_letters": "".join(sorted(letters)),
        "distinct_letters": len(set(letters)),
    }

    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    (WORKSPACE_DIR / "state.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "result.json").write_text(
        json.dumps({"status": "success", **stats}, indent=2), encoding="utf-8"
    )

    print(f"Analyzed {word!r}: {stats}")


if __name__ == "__main__":
    main()
