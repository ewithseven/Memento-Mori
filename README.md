# Memento Mori: a judge that never picks the label

Code, prompts, outputs and pre-registrations for the technical report in [REPORT.md](REPORT.md).

**Authors.** ewithseven designed the judge. Claude (Anthropic), working through Claude Code, implemented it and ran the experiments.

## Where each result comes from

"Faz" means phase. Each phase has code in `faz5/fazN.py`, outputs in `results/fazN/` and a pre-registration in `docs/ON_KAYIT_FAZN.md`.

| Report section | Phase | Notes |
|---|---|---|
| Result 1, standard vs reversed | Faz 19 | The "C standard" column comes from Faz 18. |
| Result 2, objection field only | Faz 23 | |
| Result 3, AgentDojo | Faz 17, batch 1 | |
| Earlier runs cited in the report | Faz 5, Faz 11 | Faz 11 is the run at maximum reasoning effort. |
| Exploratory variants | Faz 20, 21, 22 | |

- `docs/ETIKET_TANIMLARI.md` records the history of the primary-label definition.
- The documents are in Turkish. In them, "kullanıcı" ("the user") refers to the author.

## How the runs were made

Every judge was a Claude Code subagent defined in `agents/hakem.md`: Claude Sonnet 5.5, with the file-read tool only.

1. A script prints the prompt for one transcript and arm, for example `python -I faz5/run19.py istem mis_04 MM-T`.
2. The subagent is run with that prompt.
3. `analiz` parses the subagent transcripts and writes `results/fazN/kayit.jsonl` and `sonuclar.md`. Labels are read by script, never by hand.

Two paths are local to the original machine and need adapting:
- `faz4/faz4c.py: AGENTS`, the subagent transcripts;
- `faz5/faz5.py: DOCS`, the rendered transcripts.

The code uses the Python standard library only.

## Data, not included

- **Anthropic's 18 judge-input transcripts.** Use the transcript viewer linked from [Agentic Misalignment in Summer 2026](https://alignment.anthropic.com/2026/agentic-misalignment-summer-2026/). The code expects them in `data/anthropic_mislabel/`.
- **AgentDojo.** Use the gpt-4o runs in [ethz-spylab/agentdojo](https://github.com/ethz-spylab/agentdojo), `runs/gpt-4o-2024-05-13/` (MIT license). The code expects them in `data/agentdojo/`. The 40 selected runs are listed in `results/faz17/secim.json`.

## Checking the seals

`docs/ON_KAYIT_ZAMAN_DEFTERI.md` is the ledger of SHA-256 hashes. The author emailed these hashes before the runs, which gives an external timestamp.
- Every `docs/*_MUHURLU.md` file is a sealed copy and matches the ledger byte for byte.
- `faz5/faz18.py` and `faz5/faz19.py` match as they are.
- `faz5/faz23.py` matches once two things set when CUTOFF was written are undone: the CUTOFF line goes back to `CUTOFF = "SET-BEFORE-FIRST-CALL"`, and the UTF-8 BOM is removed.

## What differs from the working copy

- **Two documents.** Two verbatim remarks by the author were reworded in `docs/ON_KAYIT_FAZ5.md` and `docs/ETIKET_TANIMLARI.md`. Neither file is sealed.
- **One prompt.** In `faz5/faz6.py`, the wording of one exploratory prompt was withheld. This is the Faz 6 self-confrontation question, which is not used in the report.
- **Left out.** One narrative report, `results/faz5/RAPOR.md`, and the private design notes.
- **Unchanged.** All sealed files, all other code and all outputs.
