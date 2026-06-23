"""MCP server exposing offline word tools backed by the system wordlist.

A single stdio tool, ``anagrams``, returns every dictionary word that can be
formed from the letters of an input word. The wordlist (/usr/share/dict/words,
installed in the agent image) lives on the server, not in the model — which is
exactly the kind of capability an MCP is for.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("wordtools")

DICTIONARY = Path("/usr/share/dict/words")
MIN_LENGTH = 2


def _load_words() -> list[str]:
    if not DICTIONARY.exists():
        return []
    words: list[str] = []
    with DICTIONARY.open(encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            candidate = line.strip().lower()
            if len(candidate) >= MIN_LENGTH and candidate.isalpha():
                words.append(candidate)
    return words


_WORDS = _load_words()


@mcp.tool()
def anagrams(word: str) -> list[str]:
    """List dictionary words that can be formed from the letters of ``word``.

    Each returned word uses only letters available in ``word`` (respecting how
    many times each letter appears), sorted by length then alphabetically.

    Args:
        word: The source word, e.g. "listen".
    """
    pool = Counter(letter for letter in word.strip().lower() if letter.isalpha())
    if not pool:
        return []
    results: list[str] = []
    for candidate in _WORDS:
        candidate_counts = Counter(candidate)
        if all(pool.get(letter, 0) >= needed for letter, needed in candidate_counts.items()):
            results.append(candidate)
    results.sort(key=lambda entry: (len(entry), entry))
    return results


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
