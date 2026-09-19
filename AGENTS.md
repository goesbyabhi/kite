# AGENTS.md

Kite: an interactive coding-agent CLI that lets Google Gemini call local tools (read/edit/search files, run shell commands) inside a sandboxed workspace. Python 3.14, dependency-managed with `uv`.

## Commands

- Install: `uv sync` (installs runtime deps + dev group: `pytest`, `ruff`, `python-lsp-server`)
- Run agent: `uv run python -m kite` (or `-m src.kite`) — requires `GEMINI_API_KEY` in a root `.env` (loaded via `load_dotenv()`)
- Tests: `uv run pytest` — 29 tests; no network or mocked Gemini needed except `test_shell.py`, which spawns real `powershell.exe`
- Lint: `uv run ruff check .`
- `uv run python -m kite.list_models` style scripts aside: `src/kite/list_models.py` is a standalone "print all model ids" script (needs `.env`)

## Structure

- `src/kite/agent.py` — the step loop (system prompt, max 10 `max_steps`, tool-result loop). Reads confirmation answers with plain `input()`.
- `src/kite/gemini.py` — `Model` implementation over the REST API: non-streaming `generateContent` plus SSE `streamGenerateContent`, function calling, thought signatures. Default model is `gemini-3.5-flash-lite`, hardcoded in `__main__.py`.
- `src/kite/workspace.py` — sandbox root: `resolve()` raises `PermissionError` for any path escaping the root.
- `src/kite/tools/` — `Tool` ABC (`base.py`) + `ToolRegistry` (`registry.py`); the 6 default tools are wired in `tools/__init__.py:default_tools()`. Read-only tools (read/list/search) need no confirmation; `shell`, `write_file`, `edit_file` set `requires_confirmation=True`.
- `tests/` — one pytest module per component; tools are tested against `tmp_path` fixtures.

## Gotchas

- On Windows, redirecting/piping stdout of `python -m kite` crashes with `UnicodeEncodeError` on the 🪁 emoji (cp1252 codec). Set `$env:PYTHONIOENCODING='utf-8'` first.
- `__main__.py:29` writes `except EOFError, KeyboardInterrupt:` — valid Python 3, but binds the caught exception to the *name* `KeyboardInterrupt`; a real Ctrl+C is NOT caught (traceback, not clean exit). Only stdin EOF exits the REPL.
- `shell` hardcodes `powershell.exe -NoProfile -NonInteractive`, a 30s timeout, and 20k-char output truncation; it is unrelated to the current OS shell. `test_shell.py::test_shell_timeout` asserts the fixed string "timed out after 30 seconds." even though it passes `timeout=1` to the tool.
- `.env*` files are blocked from read/write/edit via `SENSITIVE_FILES` and ignored by search/list filesystem walks — tool tests assert these raise `PermissionError`/are skipped, so don't "fix" that behavior.
- The system prompt in `agent.py` explicitly tells the model not to run tests/linters/builds unless asked; `ToolRegistry` guards against duplicate tool calls. Don't silently change either.