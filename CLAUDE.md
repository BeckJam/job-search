# Job Search CLI

## Skill

`/job-search` — native Claude Code slash command at `.claude/commands/job-search.md`

## Architecture

The `/job-search` skill uses an orchestrator + sub-agent pattern:

- **Orchestrator** (`.claude/commands/job-search.md`): Handles interactive steps (experience discovery interview, narrative development, user approvals) and spawns focused sub-agents for isolated work.
- **Sub-agent prompts** (`.claude/commands/agents/*.md`): Prompt templates for ATS analysis, company research, cover letter writing, resume writing, DOCX production, master reference updates, compensation research, and Workday formatting. These are NOT slash commands; the orchestrator reads them and passes their content to the Agent tool.

**Why sub-agents?** Writing agents (cover letter, resume) receive only the context they need instead of the full conversation history. This eliminates ~15-30KB of conversation noise and improves writing quality.

**Parallelism:** Three parallel stages: (1) ATS keyword analysis + company research, (2) cover letter + resume writing (voice brief ensures consistency), (3) ATS review + memory update. DOCX is only generated after user approves the markdown drafts.

## Memory System (Dual-Mode)

The tool supports two memory modes, detected automatically in Phase 0:

**MemPalace mode** (optional, recommended): Career data is stored in a local semantic search database. The orchestrator loads ~170 tokens of identity context at startup and retrieves relevant STAR projects and framings on-demand via `mempalace_search`. Writing agents receive a curated career context package (~2,000-4,000 tokens) instead of the full master reference. New framings and application data are saved directly via MemPalace MCP tools. See `docs/mempalace-setup.md` for setup.

**File mode** (default): Career data lives in a master reference markdown file. The full file (~17,000 tokens) is loaded into context each session. Writing agents read the file themselves. New content is appended by the master-reference-updater agent.

**Critical constraint:** Sub-agents do NOT have MCP tool access. Only the orchestrator can call MemPalace tools. All career data for sub-agents must be retrieved by the orchestrator and passed as text in the agent prompt.

## Configuration

All personal information, preferences, and styling options are stored in `config.md` (created during first-run onboarding from `config.example.md`). In file mode, the master reference file path is also specified in `config.md`.

## Application Folder Convention

Each application gets its own folder in this directory:
```
YYYY-MM-DD_Company-Name_Job-Title/
```
Contains `jd.txt`, `resume.md`, and `cover-letter.md`. DOCX files generated only after user approval.