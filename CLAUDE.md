# CLAUDE.md

Guidance for Claude Code working in this repo.

## Project

Virtual AI mentor for learning English and Japanese. Python, agent-based architecture, early scaffold.

## Stack

- Python >= 3.14, package/build via `uv`
- Supabase for persistence
- Gemini (`GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_MODEL_TTS`) for LLM/TTS

## Structure

```
main.py                        entry point
src/
  agents/
    lead.py                    lead/orchestrator agent
    services.py                 agent services
    instructions/               agent instruction sets
  core/
    artifacts.py                artifact handling
    env.py                      env/config loading (required env vars)
    format.py                   formatting helpers
    llm.py                       LLM client/integration
    prompt.py                    prompt building
    schemas.py                    data schemas
    supabase.py                   Supabase client
  repository/
    chat_repository.py            chat data access
  app.py                            app entry (web)
  app_cli.py                         CLI entry
```

## Commands

```bash
uv sync          # install deps
uv run main.py   # run
```

## Env

Required vars (see `src/core/env.py`): `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_MODEL_TTS`, `SUPABASE_URL`, `SUPABASE_KEY`. Keep them in `.env` (gitignored, never commit).

## Conventions

- Some docstrings/comments in Bahasa Indonesia — match existing file's language when editing it.
- No test suite yet.

## Git workflow

Use `/cp <note>` to fetch latest, stage, generate a caveman-style commit message, commit, and push in one step. See `.claude/commands/cp.md`.
