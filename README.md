# Kite 🪁

A lightweight Python coding agent powered by Google Gemini.

## Features

- **Gemini Integration**: Supports model completions and streaming using Gemini models.
- **Tool Execution**: Equipped with robust tools for reading files, editing, searching, shell execution, and workspace management.
- **Interactive Agent**: Step-by-step agent loop with conversation history and confirmation prompts for sensitive operations.

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- A Google Gemini API Key

### Installation

1. Clone the repository and navigate into the project directory:
   ```bash
   git clone https://github.com/goesbyabhi/kite.git
   cd kite
   ```

2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```

### Configuration

Create a `.env` file in the root directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

### Running the Agent

Run the main agent module:

```bash
uv run python -m src.kite
```

### Running Tests

Run the test suite using `pytest`:

```bash
uv run pytest
```
