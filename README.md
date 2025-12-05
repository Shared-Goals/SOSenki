# SOSenki

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Shared-Goals/SOSenki)

**Shared property management system for small communities** — Telegram bot + Mini App for tracking bills, balances, and service periods.

## Vision

A lightweight, self-hosted solution for 20-100 users managing shared property expenses. Built with YAGNI/KISS principles: SQLite database, Python/FastAPI backend, Telegram as the only UI.

### Current State (v1)

```text
┌─────────────────────────────────────────────────────────────────┐
│                    Telegram Bot + Mini App                       │
│  Commands: /start, /request, /bills, /periods                   │
│  Mini App: Visual bills/transactions for owners                 │
│  Admin: Create periods, generate electricity bills              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                               │
│  Webhook endpoint, Mini App API, Static files                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQLite Database                               │
│  Users, Properties, Bills, Transactions, Service Periods        │
└─────────────────────────────────────────────────────────────────┘
```

### Target State (v2) — MCP + AI Agent

Replace manual admin commands with natural language interface. Users query data conversationally; admins manage entities through AI agent with confirmation prompts.

```text
┌─────────────────────────────────────────────────────────────────┐
│                    Telegram Bot (enhanced)                       │
│  Existing commands + /ask for natural language queries          │
│  Agent routes: user queries → read tools, admin → write tools   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI Agent (Ollama + llama3.2:3b)               │
│  - Receives natural language from bot                            │
│  - Calls LLM with MCP tools (function calling)                  │
│  - Role-based access: user=read, admin=read+write               │
│  - Confirmation prompts for write operations                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Server (FastAPI router)                   │
│  Query tools: get_balance, list_bills, get_period_info          │
│  Admin tools: create_period, generate_bills, update_reading     │
│  Auth: telegram_id → user role verification                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQLite Database (unchanged)                   │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment

**Target platform:** Home server (AIBOX-3588, Ubuntu, 16GB RAM)

- **SSL termination:** Caddy with auto Let's Encrypt
- **Process manager:** systemd
- **LLM:** Ollama with llama3.2:3b (~2GB RAM)

## Development

```bash
make install      # Install dependencies via uv
make serve        # Run bot + mini app (ngrok tunnel for dev)
make test         # Run all tests
make coverage     # Generate coverage report
```

See `make help` for full command reference.

## Documentation

Auto-generated documentation: [DeepWiki](https://deepwiki.com/Shared-Goals/SOSenki)

