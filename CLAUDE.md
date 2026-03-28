# Job Search CLI

## Skill

`/job-search` — native Claude Code slash command at `.claude/commands/job-search.md`

## Architecture

The `/job-search` skill uses an orchestrator + sub-agent pattern:

- **Orchestrator** (`.claude/commands/job-search.md`): Handles interactive steps (experience discovery interview, narrative development, user approvals) and spawns focused sub-agents for isolated work.
- **Sub-agent prompts** (`.claude/commands/agents/*.md`): Prompt templates for ATS analysis, company research, cover letter writing, resume writing, DOCX production, master reference updates, compensation research, and Workday formatting. These are NOT slash commands; the orchestrator reads them and passes their content to the Agent tool.

**Why sub-agents?** Writing agents (cover letter, resume) receive only the context they need (master reference + focus guide + JD + keywords) instead of the full conversation history. This eliminates ~15-30KB of conversation noise and improves writing quality.

**Parallelism:** ATS keyword analysis and company research run in parallel. Cover letter then resume run sequentially (cover letter establishes narrative voice).

## Configuration

All personal information, preferences, and styling options are stored in `config.md` (created during first-run onboarding from `config.example.md`). The master reference file path is specified in `config.md`.

## Application Folder Convention

Each application gets its own folder in this directory:
```
YYYY-MM-DD_Company-Name_Job-Title/
```
Contains `resume.md` and `cover-letter.md` by default. DOCX generated automatically for resumes.