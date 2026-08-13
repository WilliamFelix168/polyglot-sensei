# Mentor Bahasa Inggris and Japan Virtual

Virtual AI mentor project for learning English and Japanese. Built in Python with an agent-based architecture.

## Status

Early scaffold — project structure in place, implementation in progress.

## Tech Stack

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/) for build/package management
- Supabase (planned, for persistence)

## Project Structure

```
main.py                        # entry point
src/
  agents/
    lead.py                    # lead/orchestrator agent
    services.py                 # agent services
    instructions/               # agent instruction sets
  core/
    artifacts.py                # artifact handling
    env.py                      # environment/config loading
    format.py                   # formatting helpers
    llm.py                       # LLM client/integration
    prompt.py                    # prompt building
    schemas.py                    # data schemas
    supabase.py                   # Supabase client
  repository/
    chat_repository.py            # chat data access
  docs/                            # project docs
  app.py                            # app entry (web?)
  app_cli.py                         # CLI entry
```

## Getting Started

Requires Python 3.14+ and `uv`.

```bash
uv sync
uv run main.py
```

Configure environment variables in `.env` (see `src/core/env.py` for required keys).

## Author

William Felix — william.felix059@gmail.com
