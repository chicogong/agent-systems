# Aimake Knowledge Vault — Agent Protocol (`AGENTS.md`)

This local-first Markdown vault combines Aimake LLM Wiki budgets, `@lwc/core` proposal governance, and Qingyan Vault epistemic conventions. Humans own intent, source selection, and final acceptance; AI Agents retrieve, draft, and check within explicit permission boundaries.

## Vault Structure

- `raw/`: Immutable ingested source snapshots with SHA-256 provenance.
- `wiki/`: Synthesized long-term knowledge pages (`wiki/index.md` <= 3,000 tokens; `wiki/log.md` operations log).
- `personas/`: Compact Style DNA profiles (`<= 800 tokens` per persona).
- `outputs/`: Compounded deliverable records linked back to vault provenance.
- `.lwc/drafts/` & `.lwc/proposals/`: Isolated staging area for source-bound drafts and human-reviewable proposals.
- `Overview.base`: Obsidian Bases table view over vault folders.

## Permission Hierarchy (R0–R3)

- **R0 (Read-Only Default)**: Inspect files, compile graph/lint diagnostics, extract 0–2 hop context bundles, and verify citations. Never modify vault files.
- **R1 (Isolated Draft & Proposal Staging)**: Stage source-bound drafts and proposals only under `.lwc/drafts/`, `.lwc/proposals/`, or `Agent/草稿/`. Never write directly to formal `wiki/` knowledge pages.
- **R2 (Single-File Human-Reviewed Write)**: Apply a reviewed proposal affecting one formal knowledge file only after explicit human review (`human:<name>`) and exact proposal-ID confirmation.
- **R3 (Multi-File / Structural Write)**: Apply multi-file or structural knowledge changes only after explicit human review and confirmation.

## Epistemic Separation Rules

Every drafted or synthesized knowledge note MUST separate evidence from interpretation using these headings:

- `## 核心事实 (Facts)` — Direct, verifiable claims linked to vault sources (`raw/` or SHA-256 provenance).
- `## 推断 (Inferences)` — Model synthesis or reasoning explicitly tagged `[推断]`.
- `## 待验证 (Unverified)` — Open questions or claims lacking source evidence explicitly tagged `[待验证]`.

## Portability & Hygiene

- Use relative WikiLinks, standard Markdown, YAML frontmatter, and open JSON Canvas; never write machine-absolute paths or secrets.
- Keep `wiki/index.md <= 3,000 tokens` and `personas/*.md <= 800 tokens`.
- Never auto-approve proposals with autonomous identities (`agent:*`, `bot:*`, `llm:*`, `model:*`, `ai:*`).
