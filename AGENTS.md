# Repository Guidelines

## Project Overview

Virtual English mentor for Indonesian beginners. Users send text or voice; the app classifies the learning intent, generates exercises (reading/writing/speaking/listening), evaluates submissions, and produces PDF progress reports. Powered by Google Gemini LLM + TTS with Supabase persistence. Current interface: CLI REPL. Telegram bot delivery is planned (`src/app.py` is empty placeholder). Japanese support is in the project title but not yet implemented — only English agents and instructions exist.

## Architecture & Data Flow

Single-orchestrator multi-agent pipeline. `LeadAgent` receives all input and delegates to sub-agents via Gemini function-calling tools or direct calls.

```
User input (stdin / future: Telegram)
  └─► LeadAgent.handle_send_message()
        ├─ ChatRepository.save_message(role='user')          → Supabase chat_histories
        ├─ ChatRepository.load_history_by_user_id()          → full history as Gemini Contents
        ├─ artifacts.start()                                 → reset per-request artifact basket
        ├─ Gemini generate_content (agent-lead + 3 tools)
        │    ├─ TOOL: skill_type_classification(text)
        │    │    ├─ Gemini(agent-skill-type-classifier) → EvaluateUserIntentionSchema
        │    │    └─ generate_exercise(skill_type)
        │    │         ├─ writing_exercise  → Gemini(agent-writing-exercise)  → markdown
        │    │         ├─ reading_exercise  → Gemini(agent-reading-exercise)  → markdown
        │    │         ├─ speaking_exercise → Gemini(agent-speaking-exercise) → markdown
        │    │         └─ listening_exercise
        │    │              ├─ Gemini(agent-generate-script) → ListeningExerciseSchema JSON
        │    │              ├─ Gemini TTS (multi-speaker: Puck=male, Kore=female) → PCM bytes
        │    │              ├─ _write_wave_file() → src/output/listening-<ts>.wav
        │    │              └─ artifacts.add(path, kind='audio')
        │    ├─ TOOL: evaluate_writing(text)
        │    │    └─ Gemini(agent-evaluate-writing) → markdown grammar corrections
        │    └─ TOOL: get_learning_tip()
        │         └─ random.choice(hardcoded list of 5 strings)
        ├─ artifacts.collect() → ChatRepository.save_artifact()
        ├─ ChatRepository.save_message(role='model')
        └─ return {text: str, artifacts: QueryResult}

Voice path (wired in Telegram, not CLI):
  LeadAgent.handle_send_voice(ogg_path)
    └─ evaluate_speaking() → upload OGG → Gemini(agent-evaluate-speaking) → EvaluateSpeakingSchema

Report path (wired in Telegram, not CLI):
  LeadAgent.handle_report(user_id, username, start_date, end_date)
    └─ generate_report() → Gemini(agent-report) → LearningReportSchema → markdown-pdf → .pdf
```

**Everything is synchronous** — no `async`/`await` anywhere in the codebase.

## Key Directories

| Path | Purpose |
|------|---------|
| `src/agents/` | `lead.py` (orchestrator), `services.py` (all sub-agent functions), `instructions/` (Markdown system prompts) |
| `src/core/` | Singletons and utilities: `env.py`, `llm.py`, `supabase.py`, `schemas.py`, `artifacts.py`, `prompts.py`, `format.py` |
| `src/repository/` | `chat_repository.py` — all Supabase table access |
| `src/agents/instructions/` | One `.md` per agent role; loaded at runtime by `prompts.load_instruction(name)` |
| `src/output/` | Runtime-generated files: `listening-<ts>.wav`, `laporan-belajar-<ts>.pdf` (not committed) |
| `src/docs/` | Static reference documents for agents |

## Development Commands

```bash
# Install dependencies
uv sync

# Run CLI
uv run main.py

# Exit CLI
/exit
```

No build, lint, or test commands are configured.

## Code Conventions & Common Patterns

### Singletons via `@lru_cache`
Gemini and Supabase clients are process-level singletons. Never instantiate them directly; always call the getter.

```python
# src/core/llm.py
client = llm.get_gemini_client()

# src/core/supabase.py
db = supabase.get_supabase_client()
```

### Structured LLM Outputs
All sub-agents that return structured data use Pydantic v2 schemas passed as `response_json_schema` to Gemini. Parse with `model.model_validate(json.loads(response.text))`.

```python
schema = EvaluateUserIntentionSchema.model_json_schema()
response = gemini_client.models.generate_content(..., config=types.GenerateContentConfig(response_json_schema=schema))
result = EvaluateUserIntentionSchema.model_validate(json.loads(response.text))
```

Schemas live in `src/core/schemas.py`:
- `EvaluateUserIntentionSchema` — `skill_types: Literal['reading','speaking','writing','listening']`
- `ListeningExerciseSchema` — `speaker_one`, `speaker_two`, `script`, `questions: list[str]`
- `EvaluateSpeakingSchema` — `correction`, `score: str` (0–100), `summary`
- `LearningReportSchema` — `start_date`, `end_date`, `username`, `global_score`, `skill_types: list[LearningSkillTypesSchema]`, `markdown_content`

### Gemini Tool Registration
Only three functions are registered as Gemini tools on `LeadAgent`: `skill_type_classification`, `evaluate_writing`, `get_learning_tip`. `evaluate_speaking` and `generate_report` are called **directly** by `LeadAgent` methods, not via tool-calling.

### Artifact Side-Channel
Use `artifacts` (from `src/core/artifacts.py`) to pass generated file paths from sub-agents back to the delivery layer without threading them through return values.

```python
artifacts.start()          # call once per request
artifacts.add(path, kind='audio', caption=None)
result = artifacts.collect()   # call after all sub-agents finish
```

### Agent Instructions
Every agent role has a corresponding `.md` file in `src/agents/instructions/`. Load with:

```python
from src.core.prompts import load_instruction
instruction = load_instruction("agent-lead")   # reads agent-lead.md, LRU-cached
```

Naming pattern: `agent-<role>.md` — e.g., `agent-evaluate-writing.md`, `agent-generate-script.md`.

### Language
All agent instruction files and docstrings/comments in `services.py` and `chat_repository.py` are written in **Bahasa Indonesia**. Match the existing language of each file when editing.

### Error Handling
Minimal by design. `_required_env()` raises `RuntimeError` on missing env vars (fails at import time). `evaluate_speaking` raises `ValueError` if Gemini file upload reports `FAILED`. No try/except elsewhere in `LeadAgent` or `services.py`.

### Telegram Formatting
`src/core/format.py` exposes `to_telegram_markdown(text)` for converting LLM Markdown to Telegram MarkdownV2. Not used by the CLI layer — reserved for `src/app.py` (future Telegram bot).

## Important Files

| File | Role |
|------|------|
| `main.py` | Entry point; `__main__` guard calls `app.run()` |
| `src/app_cli.py` | CLI REPL loop; `lead_agent` instantiated at module level |
| `src/app.py` | Empty — future Telegram bot entry point |
| `src/agents/lead.py` | `LeadAgent` — single orchestrator class |
| `src/agents/services.py` | All sub-agent functions (tools + direct-call handlers) |
| `src/repository/chat_repository.py` | All Supabase I/O; tables: `chat_histories`, `chat_users` |
| `src/core/env.py` | Config; fails fast if any of 5 required env vars is absent |
| `src/core/schemas.py` | Pydantic schemas for all structured Gemini responses |
| `src/agents/instructions/agent-lead.md` | System prompt for the lead orchestrator |

## Runtime/Tooling Preferences

- **Python:** 3.12 (pinned in `.python-version`; `pyproject.toml` requires `>=3.12`)
- **Package manager:** `uv` — use `uv sync` to install, `uv run` to execute
- **Build backend:** `uv_build` (`>=0.12.1,<0.13.0`)
- **No CI/CD, no Docker** — local dev only
- **Required env vars** (all mandatory; app raises `RuntimeError` at startup if missing):

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (`AIzaSy…` format) |
| `GEMINI_MODEL` | Text model name (e.g. `gemini-2.5-flash`) |
| `GEMINI_MODEL_TTS` | TTS model name (e.g. `gemini-2.5-flash-preview-tts`) |
| `SUPABASE_URL` | Project URL (`https://<ref>.supabase.co`) |
| `SUPABASE_KEY` | Anon/service-role JWT |

No `.env.example` exists — document required keys above when onboarding.

## Testing & QA

**No tests.** Zero test files, no pytest config, no coverage, no linting config (no ruff, mypy, black, flake8 in `pyproject.toml` or at root).

When adding tests: use `pytest` (already present as a transitive dep in `.venv`). Add config under `[tool.pytest.ini_options]` in `pyproject.toml`. Dev deps go under `[tool.uv.dev-dependencies]`.

### Known Bugs (not yet fixed)
- `EvaluateSpeakingSchema` defined twice in `schemas.py`; second definition shadows the first.
- `services.timestamp` set once at module import — all output files in a session share the same timestamp.
- `LeadAgent._load_history()` builds malformed `Content` objects (incorrect `Part` nesting); history replay to Gemini may misbehave.
- CLI passes `user_id=''` (empty string) to all repository calls — no user isolation in CLI mode.

## Git Workflow

Use `/cp <note>` to pull latest, stage all, generate a caveman-style Conventional Commit message, commit, and push in one step.

```bash
/cp fix chat history bug
```

See `.claude/commands/cp.md` for implementation. Never commit `.env`.
