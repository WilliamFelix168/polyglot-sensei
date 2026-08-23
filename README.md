# Mentor Bahasa Inggris Virtual

AI-powered English tutor for Indonesian beginners. Classifies learning intent, generates exercises across four skills (reading, writing, speaking, listening), evaluates submissions, and produces PDF progress reports — all via Google Gemini.

## Features

- **Exercise generation** — reading, writing, speaking, and listening tasks tailored for beginners
- **Writing evaluation** — grammar corrections with explanations in Bahasa Indonesia
- **Speaking evaluation** — pronunciation scoring from voice notes (OGG), with phonetic feedback
- **Listening exercises** — multi-speaker TTS dialog (male/female voices) + comprehension questions
- **Learning reports** — PDF summary of progress over a date range
- **Chat persistence** — full conversation history stored in Supabase

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| LLM / TTS | Google Gemini (`google-genai`) |
| Persistence | Supabase (PostgreSQL) |
| PDF generation | `markdown-pdf` + PyMuPDF |
| Interface | CLI (Telegram bot planned) |

## Getting Started

### Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- Google Gemini API key
- Supabase project

### Installation

```bash
git clone <repo-url>
cd mentor_bahasa_inggris_and_japan_virtual
uv sync
```

### Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.5-flash
GEMINI_MODEL_TTS=gemini-2.5-flash-preview-tts
SUPABASE_URL=https://<ref>.supabase.co
SUPABASE_KEY=<anon-or-service-role-jwt>
```

### Run

```bash
uv run main.py
```

Type a message to start a session. Use `/exit` to quit.

## Project Structure

```
main.py                          # entry point
src/
  app_cli.py                     # CLI REPL
  app.py                         # Telegram bot (planned)
  agents/
    lead.py                      # orchestrator agent
    services.py                  # sub-agent functions (exercises, evaluation, report)
    instructions/                # system prompts (.md) — one per agent role
  core/
    env.py                       # env var loading; fails fast if any key is missing
    llm.py                       # Gemini client singleton
    supabase.py                  # Supabase client singleton
    schemas.py                   # Pydantic schemas for structured LLM responses
    artifacts.py                 # per-request artifact side-channel (contextvars)
    prompts.py                   # instruction file loader (LRU-cached)
    format.py                    # Telegram MarkdownV2 formatter
  repository/
    chat_repository.py           # Supabase I/O: chat_histories, chat_users tables
  output/                        # generated files: .wav audio, .pdf reports
```

## Architecture

Single-orchestrator pipeline. `LeadAgent` classifies intent via Gemini function-calling, then dispatches to the appropriate sub-agent.

```
User input
  └─► LeadAgent
        ├─ skill_type_classification → writing / reading / speaking / listening exercise
        ├─ evaluate_writing          → grammar corrections
        └─ get_learning_tip          → random study tip

Voice input  → evaluate_speaking → pronunciation score + feedback
Report request → generate_report → LearningReportSchema → PDF
```

All agent instructions are external Markdown files under `src/agents/instructions/`, swappable without code changes.

## Author

William Felix — william.felix059@gmail.com
