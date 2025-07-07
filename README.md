# Simple DB MCP Server

A lightweight MCP (Model Context Protocol) server built in Python for performing CRUD operations on a local SQLite database. Designed for fast iteration, Claude Desktop integration, and AI agent control via Ollama using the tool-calling-capable `qwen:14b` model.

---

## 🚀 Features

- MCP-compliant Python server
- SQLite database (`mcp_ecommerce.db`)
- Compatible with Claude Desktop via `uv run mcp install`
- Client script for testing local interactions
- Ollama-compatible with tool-calling enabled via `qwen:14b`
- Managed cleanly with `uv` and `pyproject.toml` — no pip required

---

## 📁 Project Structure

```plaintext
simple-db-mcp-server/
├── db.py             # SQLite utility functions
├── server.py         # MCP server logic
├── client.py         # Example MCP client
├── mcp_ecommerce.db  # Sample database
├── pyproject.toml    # Project & dependency config
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚙️ Requirements

- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv)
- [`Ollama`](https://ollama.com/) (local AI inference engine)
- [`qwen:14b`](https://ollama.com/library/qwen) model (supports tool calling)
- [Claude Desktop](https://claude.ai/) (optional)

---

## 🧠 Setting Up Ollama & Qwen

Make sure you have [Ollama](https://ollama.com/) installed and running before starting the server or interacting via an agent.

### 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Or download it from: [https://ollama.com/download](https://ollama.com/download)

### 2. Pull the Tool-Calling Model: `qwen:14b`

```bash
ollama pull qwen:14b
```

> `qwen:14b` is a powerful open-source LLM that supports function/tool calling, required for AI agents to invoke this MCP server.

---

## ⚙️ Project Setup with `uv`

### 1. Install `uv`

```bash
curl -Ls https://astral.sh/uv/install.sh | bash
```

---

### 2. Clone and Navigate

```bash
git clone https://github.com/RaviMehta90/simple-db-mcp-server.git
cd simple-db-mcp-server
```

---

### 3. Create and Activate a Virtual Environment

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

---

### 4. Install Dependencies

```bash
uv sync
```

---

## 🖥️ Register the Server with Claude Desktop

```bash
uv run mcp install server.py
```

### ✅ Output Example

```
[07/07/25 21:35:38] INFO     Added server 'ecommerce-sqlite' to Claude config
                    INFO     Successfully installed ecommerce-sqlite in Claude app
```

---

## 🧪 Running the Client

To interact with the MCP server via command-line client:

```bash
uv run client.py
```

---

## 🗃️ Sample Database

The SQLite file `mcp_ecommerce.db` contains prepopulated tables (e.g. users, products). You can explore it with any SQLite viewer or use:

```bash
sqlite3 mcp_ecommerce.db
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋 Support

Questions, ideas, or contributions welcome!  
Contact [@RaviMehta90](https://github.com/RaviMehta90) or open an issue.
