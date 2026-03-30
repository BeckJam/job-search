# Job Search CLI

## Skill

`/job-search` — native Claude Code slash command at `.claude/commands/job-search.md`

## Architecture

The `/job-search` skill uses an orchestrator + sub-agent pattern:

- **Orchestrator** (`.claude/commands/job-search.md`): Handles interactive steps (experience discovery interview, narrative development, user approvals) and spawns focused sub-agents for isolated work.
- **Sub-agent prompts** (`.claude/commands/agents/*.md`): Prompt templates for ATS analysis, company research, cover letter writing, resume writing, DOCX production, master reference updates, compensation research, and Workday formatting. These are NOT slash commands; the orchestrator reads them and passes their content to the Agent tool.

**Why sub-agents?** Writing agents (cover letter, resume) receive only the context they need (master reference + focus guide + JD + keywords) instead of the full conversation history. This eliminates ~15-30KB of conversation noise and improves writing quality.

**Parallelism:** Three parallel stages: (1) ATS keyword analysis + company research, (2) cover letter + resume writing (voice brief ensures consistency), (3) ATS review + master reference update. DOCX is only generated after user approves the markdown drafts.

## Configuration

All personal information, preferences, and styling options are stored in `config.md` (created during first-run onboarding from `config.example.md`). The master reference file path is specified in `config.md`.

## Application Folder Convention

Each application gets its own folder in this directory:
```
YYYY-MM-DD_Company-Name_Job-Title/
```
Contains `jd.txt`, `resume.md`, and `cover-letter.md`. DOCX files generated only after user approval.