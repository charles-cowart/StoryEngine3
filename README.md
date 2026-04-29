# StoryEngine3

Interactive story-writing CLI using local Ollama models, llamaIndex retrieval over local story files, append-only transcript logging, and YAML session persistence.

This project is for educational and experimental purposes. Specifically, it is an educational and experimental exploration of building
RAG-based storytelling systems using public domain works.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Make sure Ollama is installed and running locally.

## Run

Start a new session (defaults to `gpt-oss:20b`):

```bash
python main.py
```

Choose model:

```bash
python main.py --model gpt-oss:20b
```

Resume an existing YAML session:

```bash
python main.py --resume sessions/my_session.yaml
```

Set output path for a new or resumed session:

```bash
python main.py --output sessions/my_session.yaml
```

Quit with `/quit`, `/exit`, `quit`, or `exit`. The session is automatically saved on quit or Ctrl+C.

## Design notes

- `Session` stores every user/assistant message in an append-only `messages` list.
- Summaries are stored in `summaries` and never replace raw messages.
- Rolling summarization window size is 10 messages:
  - While unsummarized messages are `<= 10`, they are sent raw.
  - When unsummarized messages become `> 10`, the oldest 10 are folded into a new rolling summary.
  - Future model calls send system prompt + rolling summary + remaining unsummarized messages.
- YAML persistence includes metadata and enough state to reconstruct context boundaries.

## Example YAML shape

```yaml
session_id: 9df4f350-4acc-42ef-89f4-eb7f1145af77
model: gpt-oss:20b
created_at: '2026-04-27T03:00:00.000000+00:00'
updated_at: '2026-04-27T03:05:00.000000+00:00'
ended_at: '2026-04-27T03:05:00.000000+00:00'
status: closed
messages:
  - index: 1
    role: user
    content: Let's start with a haunted lighthouse.
    timestamp: '2026-04-27T03:00:10.000000+00:00'
  - index: 2
    role: assistant
    content: Great choice. On a storm-bent coast...
    timestamp: '2026-04-27T03:00:12.000000+00:00'
summaries:
  - index: 1
    covers_messages: [1, 10]
    content: The story centers on...
    timestamp: '2026-04-27T03:03:00.000000+00:00'
rolling_summary: The story centers on...
summarized_through_message: 10
unsummarized_message_indexes: [11, 12]
```


## Story bible indexing (llamaIndex)

- On startup, StoryEngine3 indexes files in `data/` using llamaIndex.
- Retrieval runs before each assistant response and injects relevant canon context into the prompt.
- The selected `--model` is used for both generation and the Ollama-backed llamaIndex LLM/embeddings.

Sample Peter Pan corpus files are included in `data/` to provide initial story canon.
