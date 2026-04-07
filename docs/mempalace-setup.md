# MemPalace Integration (Optional)

MemPalace is an optional enhancement that replaces the flat-file memory system and master reference with semantic search, knowledge graph, and compressed context loading.

## What It Does

Without MemPalace (file mode), the tool reads your entire master reference (~17,000 tokens) into context every session, and writing agents read the full file themselves.

With MemPalace, the orchestrator loads only identity context (~170 tokens) at startup, then uses semantic search to find the specific STAR projects, framings, and experience sections relevant to each application. Writing agents receive a curated career context package (~2,000-4,000 tokens) instead of the full file.

## Automatic Setup

The next time you run `/job-search`, Phase 0 will ask if you want to enable MemPalace. If you say yes, it will:

1. Install MemPalace (`pip install mempalace`)
2. Initialize the palace structure
3. Register the MCP server with Claude Code
4. Migrate your existing master reference and flat-file memories into the palace
5. Report what was imported

You will need to restart Claude Code after the MCP server is registered.

## Manual Setup

If you prefer to set up manually:

```bash
pip install mempalace
mempalace init --yes .
claude mcp add mempalace -- python3 -m mempalace.mcp_server
python3 scripts/migrate-to-mempalace.py
```

Restart Claude Code for the MCP server to activate.

## Palace Structure

After migration, your data is organized into:

- **career wing**: identity, strengths, star-projects (one per project), experience, education, metrics, narrative-framings (one per framing), application-tracker
- **preferences wing**: writing-rules, feedback (one per memory), employer-rules
- **applications wing**: populated per-application with narrative strategy, voice brief, and research

## Verification

```bash
mempalace status          # Shows all wings, rooms, and drawer counts
mempalace search "query"  # Test semantic search
```

## Fallback

If MemPalace is not installed or the MCP server is unavailable, the tool automatically falls back to file mode (reading the master reference file from config.md). No data is lost.

## Uninstalling

To revert to file mode:

1. Remove the MCP server: edit `~/.claude.json` and remove the mempalace entry
2. Optionally uninstall: `pip uninstall mempalace`

Your master reference file is untouched throughout. The palace data lives in `~/.mempalace/palace/`.
