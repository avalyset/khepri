# AI use in this project

## Principle

The owner decides and verifies. ADRs are written before the computation they govern, and
every released number is checked against primary sources by the owner. AI tools draft; they
do not decide.

- **Claude Code** — drafts code and prose, runs tests, reports what it measured.
- **Claude in chat** — analysis and fact-checking against files on disk.
- **A separate reviewing pass** — voice and register on outward-facing text.

No tool is fine-tuned or trained on project data. Nothing ships unread.

## Models used per release

| Release | Models |
|---|---|
| v1.4 (2026-09-09) | Opus 4.8, Opus 5, Sonnet 4.6 — per commit; 12 of 42 carry none |
| next (planned) | Opus 5 for repository work; Fable 5.1 in chat |

All Anthropic Claude. Strings are recorded as the session reports them, not from memory.
