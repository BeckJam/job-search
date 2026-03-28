---
description: >
  Use this skill for ALL job search and application work. Triggers whenever the user pastes a job description, asks to apply for a role, needs a cover letter or resume tailored to a specific job, wants to research a company, needs interview prep, or asks about compensation for a role. Also triggers for requests to update the master reference document or review which applications are in progress. Use this skill proactively — if job application work is implied at all, invoke this skill.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - WebSearch
  - WebFetch
  - Agent
  - Grep
---

# Job Search Skill (Orchestrator)

This skill orchestrates job application work by handling interactive steps directly and delegating heavy writing/research to focused sub-agents via the Agent tool. Sub-agent prompts live in `.claude/commands/agents/`.

---

## Phase 0: Configuration Check

Before anything else, check if `config.md` exists in the project root.

### If `config.md` does NOT exist (first-run onboarding):

1. Tell the user: "Welcome! This is your first time running the job search skill. Let's get you set up."
2. Read `config.example.md` from the project root as the template.
3. Ask the user for the following information:
   - Full name
   - Phone number
   - Email address
   - LinkedIn URL (just the path, e.g., `linkedin.com/in/yourprofile`)
   - City and state (e.g., "Seattle, WA")
   - Where they want to store their master reference file (suggest `./master-reference.md` as default)
4. Ask the user for their identity framing: "In 1-2 sentences, how would you describe yourself professionally? This anchors every cover letter and resume headline."
5. Create `config.md` in the project root, populated with the user's answers and the defaults from the example.
6. Copy `templates/master-reference-template.md` to the user's chosen master reference path.
7. Tell the user:
   - "Your config and master reference template have been created."
   - "Before running your first application, fill in your master reference with your career history, STAR projects, and skills."
   - "Look at `templates/example-master-reference.md` for a detailed example of what a good master reference looks like."
8. **STOP.** Do not proceed to the job application workflow until the master reference is filled in.

### If `config.md` exists:

1. Read `config.md` and extract all settings (personal info, file paths, identity framing, standing preferences, banned/preferred phrases, employer consolidation rules, DOCX styling).
2. Read the master reference at the path specified in config.
3. **Empty master reference check:** If the master reference still contains placeholder text (e.g., "Your Name", "Company Name", "Achievement with specific metric") or is under 500 characters, warn the user: "Your master reference appears to still be a template. Please fill it in with your real career data before running an application. See `templates/example-master-reference.md` for guidance."
4. Store all config values in context for passing to sub-agents.
5. Proceed to Phase 1.

---

## Phase 1: Load Master Reference

Read the master reference file at the path specified in `config.md`. This file is the single source of truth. Hold it in context for the interactive phases. Note the file path; writing agents will read it themselves.

---

## Standing Preferences

Read standing preferences, banned phrases, preferred phrases, and employer consolidation rules from `config.md`. These are injected verbatim into every writing agent prompt alongside the agent's own instructions.

When passing context to writing agents, always include:
- The standing preferences block from config
- The banned phrases list from config
- The preferred phrases list from config
- The employer consolidation rules from config
- The identity framing from config
- The user's personal information (name, contact details) from config

---

## Workflow: New Job Application

When the user provides a new job description, follow these phases in order.

### Phase 2: Parallel Analysis

Spawn two agents **simultaneously** using the Agent tool:

**Agent 1: ATS Keyword Analysis**
- Read the prompt from `.claude/commands/agents/ats-keyword-analysis.md`
- Pass the full job description text
- Also pass the standing preferences (banned/preferred phrases) from config
- Agent returns: prioritized keyword list grouped by thematic clusters

**Agent 2: Company Research**
- Read the prompt from `.claude/commands/agents/company-research.md`
- Pass the company name and role title
- Also pass a brief summary of the user's background from the master reference so the agent can identify connections
- Agent returns: research summary with narrative hooks

Launch both agents in a single response using two Agent tool calls. Wait for both to return before proceeding.

### Phase 3: Interactive Discovery (in main conversation)

With both agent results in hand:

**Step A Review**: Present the ATS keyword analysis to the user for review. Ask if any keywords should be added or deprioritized.

**Step B: Company Research Summary**: Present ONLY the one-paragraph strategy summary from the company research agent. This paragraph covers what was found, how it impacts resume/cover letter strategy, and ends with the likely hiring manager or recruiter. The full research still flows to writing agents.

**Step C: Two Questions** (this replaces a full experience discovery interview):
1. "What's the angle you want to take on this one?"
2. "Anything new not in your master reference?"

Wait for the user's answers before proceeding. These two questions are all that's needed; the master reference already has the stories.

**Step D: Narrative Development**: Identify the centerpiece story, the single most compelling reason the user is the right candidate. Then map:
- What do they lead with?
- What requirements still need creative framing?
- Which STAR projects from the master reference are most relevant?
- Which new assets from the interview should be front and center?
- What proven narrative framings from the master reference apply?

Present the narrative strategy and get the user's input before writing. This narrative strategy becomes the **focus guide** passed to writing agents.

### Phase 4: Folder Creation

Create the application folder in the current working directory:

```
YYYY-MM-DD_Company-Name_Job-Title/
```

Rules:
- Use today's date
- Sanitize company name and job title: spaces become hyphens, remove special characters
- Example: `2026-03-26_Acme-Corp_Senior-Software-Engineer`

### Phase 5: Document Generation (Sequential)

Spawn writing agents **sequentially** (cover letter first, then resume). The cover letter establishes narrative voice; the resume follows.

**Agent 3: Cover Letter Writer**
- Read the prompt from `.claude/commands/agents/cover-letter-writer.md`
- Pass to the agent:
  - Master reference file path (agent will Read it)
  - The focus guide / narrative strategy from Step D
  - New assets from the interview
  - ATS keywords from Step A
  - Company research summary from Step C
  - Full job description text
  - Application folder path for saving `cover-letter.md`
  - All config values: standing preferences, banned/preferred phrases, identity framing, personal info
- Agent returns: final cover letter saved to folder

**Agent 4: Resume Writer** (after cover letter completes)
- Read the prompt from `.claude/commands/agents/resume-writer.md`
- Pass to the agent:
  - Master reference file path (agent will Read it)
  - The focus guide / narrative strategy from Step D
  - New assets from the interview
  - ATS keywords from Step A
  - Company research summary from Step C
  - Full job description text
  - Application folder path for saving `resume.md`
  - All config values: standing preferences, banned/preferred phrases, employer consolidation rules, identity framing, personal info
- Agent returns: final resume saved to folder

**Agent 5: DOCX Producer** (after resume completes)
- Read the prompt from `.claude/commands/agents/docx-producer.md`
- Pass: file path to the saved `resume.md`, application folder path, company name and role title, user's name from config, DOCX styling values from config
- Agent produces ATS-optimized resume DOCX in the application folder
- Report the DOCX file path in Phase 7 review

**Agent 6: ATS Review** (after DOCX producer completes)
- Read the prompt from `.claude/commands/agents/ats-review.md`
- Pass: resume file path, full job description text, ATS keyword analysis from Step A, and screening questions if available
- Agent returns: parse simulation, red flags, keyword coverage score, screening question check, and top 3 recommended changes
- Present results in Phase 7 review. If critical red flags or low keyword coverage, flag for the user's attention before finalizing.

### Phase 6: Master Reference Update

After both documents are complete, spawn the master reference updater agent:

- Read the prompt from `.claude/commands/agents/master-reference-updater.md`
- Pass: master reference file path (from config), new assets, new framings, application tracker row data (date, company, role, status, folder path)

### Phase 7: Review with User

Present a summary of what was created:
- Cover letter highlights (centerpiece story, key evidence used)
- Resume highlights (summary framing, leading bullets)
- DOCX resume file path (ready for ATS upload)
- What was added to the master reference
- Offer to generate cover letter DOCX if needed

---

## On-Demand Tasks

These are triggered by specific requests, not part of the standard workflow.

### Cover Letter DOCX Production

Resume DOCX is generated automatically in Phase 5. When the user requests a cover letter DOCX:
- Read the prompt from `.claude/commands/agents/docx-producer.md`
- Pass: file path to cover-letter.md, application folder path, company name and role title, user's name from config, DOCX styling from config

### Compensation Research

When the user asks about compensation:
- Read the prompt from `.claude/commands/agents/compensation-research.md`
- Pass: role title, company name, location
- Agent returns structured compensation analysis

### Workday / ATS Entry Format

When the user needs to enter resume content into a Workday or ATS form:
- Read the prompt from `.claude/commands/agents/workday-formatter.md`
- Pass: final resume.md content or file path
- Agent returns copy-paste ready fields for each role
