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

## Phase 0: Readiness Check

Phase 0 is a cascading readiness check. Each step only fires if the previous one passes.

### Step 1: MemPalace Check

Check if MemPalace MCP tools are available (try calling `mempalace_status`).

**If MemPalace is NOT available:**
- Ask the user: "Would you like to enable enhanced memory with MemPalace? It provides semantic search across your career data, compressed context loading, and a knowledge graph. Installation takes about a minute."
- **If yes:** Run `pip install mempalace` and `mempalace init --yes .` via Bash. Then register the MCP server: `claude mcp add mempalace -- python3 -m mempalace.mcp_server`. Tell the user they need to restart Claude Code for the MCP server to activate, then proceed in file mode for this session.
- **If no:** Proceed in **file mode** (current behavior, master reference file). Set memory mode to "file" for all subsequent phases.

**If MemPalace IS available:**
- Set memory mode to "mempalace" for all subsequent phases.

### Step 2: Onboarding Check

Check if `config.md` exists in the project root.

**If `config.md` does NOT exist (first-run onboarding):**

1. Tell the user: "Welcome! This is your first time running the job search skill. Let's get you set up."
2. Read `config.example.md` from the project root as the template.
3. Ask the user for the following information:
   - Full name
   - Phone number
   - Email address
   - LinkedIn URL (just the path, e.g., `linkedin.com/in/yourprofile`)
   - City and state (e.g., "Seattle, WA")
   - Where they want to store their master reference file (suggest `./master-reference.md` as default)
4. **Seed from existing documents:** Ask: "Do you have existing resumes or cover letters you'd like to use as a starting point? Provide the file paths (drag and drop works) and I'll extract your career history, skills, and achievements automatically."

   **If the user provides files:**
   a. Read the agent prompt from `.claude/commands/agents/reference-seeder.md`
   b. **If mempalace mode:** Spawn the reference seeder agent, passing: the file paths, the user's personal info. The agent returns structured career data and config suggestions. Use MemPalace MCP tools (`mempalace_add_drawer`) to store the career data directly into the palace (career wing: identity, star-projects, experience, strengths, education rooms). No master reference file is created.
   c. **If file mode:** Copy `templates/master-reference-template.md` to the user's chosen master reference path. Spawn the reference seeder agent to populate the master reference file.
   d. Present the config suggestions to the user for review and editing.
   e. Create `config.md` using the approved suggestions plus the user's personal info and defaults from the example.
   f. Tell the user their career data has been stored. They may proceed to a job application. Do NOT stop.

   **If the user declines or has no documents:**
   a. Ask for their identity framing: "In 1-2 sentences, how would you describe yourself professionally? This anchors every cover letter and resume headline."
   b. Create `config.md` populated with the user's answers and defaults from the example.
   c. **If file mode:** Copy `templates/master-reference-template.md` to the user's chosen master reference path. Tell the user to fill in their master reference before running an application. **STOP.**
   d. **If mempalace mode:** Store the identity framing in the palace via `mempalace_add_drawer` (career/identity). Tell the user to add their career history by running the seeder again with documents, or by using `/job-search` which will build their palace over time. **STOP.**

**If `config.md` exists:** Proceed to Step 3.

### Step 3: Migration Check (mempalace mode only)

If memory mode is "mempalace", check if the palace has data (call `mempalace_status` and check total drawer count).

**If palace is empty but config.md exists:**
- This is an existing user who just installed MemPalace. Run the migration: `python3 scripts/migrate-to-mempalace.py` via Bash.
- Report what was imported to the user.
- Proceed to Step 4.

**If palace has data:** Proceed to Step 4.

### Step 4: Load Context

1. Read `config.md` and extract all settings (personal info, file paths, identity framing, standing preferences, banned/preferred phrases, employer consolidation rules, DOCX styling).
2. **If mempalace mode:** Use `mempalace_search` to load identity context from the career/identity room. The full career data is NOT loaded here; it will be retrieved on-demand in Phase 4 when the specific job is known.
3. **If file mode:** Read the master reference at the path specified in config. **Empty master reference check:** If the master reference still contains placeholder text or is under 500 characters, warn the user.
4. Store all config values in context for passing to sub-agents.
5. Proceed to Phase 1.

---

## Phase 1: Memory Ready

**If mempalace mode:** Identity and critical rules are loaded from Phase 0. Detailed career content will be retrieved on-demand in subsequent phases. No full master reference load needed.

**If file mode:** The master reference file was read in Phase 0 Step 4. Hold it in context for the interactive phases. Note the file path; writing agents will read it themselves.

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

When the user provides a new job description (or a URL to one), follow these phases in order.

### Phase 2: Folder Creation + JD Capture

**This is always the first action after receiving a JD.** Before any analysis or interaction.

#### URL Detection

If the user provides a URL instead of (or along with) job description text:

1. Run `node scripts/scrape-jd.js "<url>"` via the Bash tool
2. The script extracts the main content from the page using Mozilla's Readability algorithm
3. Present the extracted job title and first few lines to the user for confirmation: "I scraped this JD from the URL — does this look right?"
4. If the user confirms, use the extracted text as the job description for all subsequent phases
5. If scraping fails (network error, login-walled page, no readable content), ask the user to paste the JD text manually

#### Create the Application Folder

Once you have the JD text (from paste or confirmed scrape), immediately:

1. Create the application folder in the current working directory:
   ```
   YYYY-MM-DD_Company-Name_Job-Title/
   ```
   Rules:
   - Use today's date
   - Sanitize company name and job title: spaces become hyphens, remove special characters
   - Example: `2026-03-26_Acme-Corp_Senior-Software-Engineer`

2. Save the full job description text as `jd.txt` in the application folder. If a URL was provided, include it as the first line of the file followed by a blank line, then the full JD text.

This folder is now the working directory for this application. All subsequent outputs go here.

### Phase 3: Parallel Analysis

Spawn two agents **simultaneously** using the Agent tool:

**Agent 1: ATS Keyword Analysis**
- Read the prompt from `.claude/commands/agents/ats-keyword-analysis.md`
- Pass the full job description text
- Also pass the standing preferences (banned/preferred phrases) from config
- Agent returns: prioritized keyword list grouped by thematic clusters

**Agent 2: Company Research**
- Read the prompt from `.claude/commands/agents/company-research.md`
- Pass the company name and role title
- **If mempalace mode:** Use `mempalace_search` to retrieve a compressed career summary from the career/identity room (~500 tokens). Pass this summary to the agent.
- **If file mode:** Pass a brief summary of the user's background from the master reference.
- Agent returns: research summary with narrative hooks

Launch both agents in a single response using two Agent tool calls. Wait for both to return before proceeding.

### Phase 4: Interactive Discovery (in main conversation)

With both agent results in hand:

**Step A Review**: Present the ATS keyword analysis to the user for review. Ask if any keywords should be added or deprioritized.

**Step B: Company Research Summary**: Present ONLY the one-paragraph strategy summary from the company research agent. This paragraph covers what was found, how it impacts resume/cover letter strategy, and ends with the likely hiring manager or recruiter. The full research still flows to writing agents.

**Step C: Two Questions** (this replaces a full experience discovery interview):
1. "What's the angle you want to take on this one?"
2. "Anything new not in your master reference?"

Wait for the user's answers before proceeding. These two questions are all that's needed; the master reference already has the stories.

**Step D: Narrative Development**: Identify the centerpiece story, the single most compelling reason the user is the right candidate.

**If mempalace mode:** Use `mempalace_search` with deliberately broad queries to find relevant content:
1. Search career/star-projects for STAR projects matching the JD keywords and user's stated angle (run 2-3 searches with different query angles)
2. Search career/narrative-framings for proven framings matching this role type, industry, or company context
3. Search career/application-tracker for past applications to similar roles
4. Assemble a **career context package**: the specific STAR projects, framings, metrics, and experience sections relevant to THIS application. This package (typically 2,000-4,000 tokens) replaces having sub-agents read the full master reference.
5. Present the selected STAR projects and framings to the user for review. The user is the safety net for missed content.

**If file mode:** Use the master reference already in context.

Then map:
- What do they lead with?
- What requirements still need creative framing?
- Which STAR projects are most relevant?
- Which new assets from the interview should be front and center?
- What proven narrative framings apply?

**Voice Brief**: As part of the narrative strategy, define a **voice brief** that both writing agents will follow. The voice brief specifies:
- **Tone**: e.g., confident and warm, technically authoritative, mission-driven
- **Register**: e.g., executive peer-to-peer, senior IC to hiring manager, leader-to-leader
- **Storytelling approach**: e.g., lead with transformation narrative, lead with technical depth, lead with scale/impact
- **Key phrases/language**: specific terms or phrasings that should thread through both documents for consistency

Present the narrative strategy (including voice brief) and get the user's input before writing. This becomes the **focus guide** passed to both writing agents.

### Phase 5: Document Generation (Parallel)

Spawn both writing agents **simultaneously** using two Agent tool calls. The voice brief ensures consistent voice across both documents without requiring sequential execution.

Read the **Writing Iterations** count from `config.md` (default: 3). Pass this count to both agents.

**Agent 3: Cover Letter Writer**
- Read the prompt from `.claude/commands/agents/cover-letter-writer.md`
- Pass to the agent:
  - **If mempalace mode:** The curated career context package assembled in Step D (relevant STAR projects, framings, metrics, experience sections as text)
  - **If file mode:** Master reference file path (agent will Read it)
  - The focus guide / narrative strategy from Step D (including voice brief)
  - New assets from the interview
  - ATS keywords from Step A
  - Company research summary
  - Full job description text
  - Application folder path for saving `cover-letter.md`
  - All config values: standing preferences, banned/preferred phrases, identity framing, personal info
  - Writing iterations count from config
- Agent returns: final cover letter saved to folder

**Agent 4: Resume Writer**
- Read the prompt from `.claude/commands/agents/resume-writer.md`
- Pass to the agent:
  - **If mempalace mode:** The curated career context package assembled in Step D (relevant STAR projects, framings, metrics, experience sections as text)
  - **If file mode:** Master reference file path (agent will Read it)
  - The focus guide / narrative strategy from Step D (including voice brief)
  - New assets from the interview
  - ATS keywords from Step A
  - Company research summary
  - Full job description text
  - Application folder path for saving `resume.md`
  - All config values: standing preferences, banned/preferred phrases, employer consolidation rules, identity framing, personal info
  - Writing iterations count from config
- Agent returns: final resume saved to folder

Launch both agents in a single response. Wait for both to return before proceeding.

### Phase 6: Post-Writing (Parallel)

After both documents are complete:

**Agent 5: ATS Review**
- Read the prompt from `.claude/commands/agents/ats-review.md`
- Pass: resume file path, full job description text, ATS keyword analysis from Phase 3, and screening questions if available
- Agent returns: parse simulation, red flags, keyword coverage score, and top 3 recommended changes

**Memory Update (runs in parallel with ATS Review):**

**If mempalace mode (orchestrator-direct, no agent needed):**
Use MemPalace MCP tools directly to store new content:
1. `mempalace_add_drawer` to add new narrative framings to career/narrative-framings
2. `mempalace_add_drawer` to add new STAR project entries or updates to career/star-projects (if any)
3. `mempalace_add_drawer` to add application-specific context (narrative strategy, voice brief, ATS keywords, company research) to applications/[company-role] room
4. `mempalace_kg_add` to add knowledge graph relationships (e.g., "Jim Beck" applied_to "Company, Role")

**If file mode:**
- Spawn Agent 6: Master Reference Update
- Read the prompt from `.claude/commands/agents/master-reference-updater.md`
- Pass: master reference file path (from config), new assets, new framings, application tracker row data (date, company, role, status, folder path)

Launch ATS Review agent and memory update simultaneously.

### Phase 7: Review and Approval

Present a summary of what was created:
- Cover letter highlights (centerpiece story, key evidence used)
- Resume highlights (summary framing, leading bullets)
- ATS review results: keyword coverage score and any red flags or recommended changes
- What was added to the master reference

If the ATS review flagged critical issues (red flags or low keyword coverage), highlight them and offer to revise the resume before proceeding.

**Ask for approval**: "Review the cover letter and resume in the application folder. Let me know if you'd like any changes, or say 'approved' to generate the final DOCX files."

### Phase 8: DOCX Production (on approval only)

**DOCX files are only generated after the user explicitly approves the markdown documents.** Do not generate DOCX at any earlier stage.

Once the user approves:

Spawn the DOCX producer agent to generate **both** resume and cover letter DOCX files:

- Read the prompt from `.claude/commands/agents/docx-producer.md`
- **Resume DOCX**: Pass file path to `resume.md`, application folder path, company name and role title, user's name from config, DOCX styling values from config
- **Cover Letter DOCX**: Pass file path to `cover-letter.md`, application folder path, company name and role title, user's name from config, DOCX styling values from config

Report both DOCX file paths to the user. These are the final ATS-ready deliverables.

---

## On-Demand Tasks

These are triggered by specific requests, not part of the standard workflow.

### DOCX Production

When the user requests DOCX generation for any document outside the standard workflow:
- Read the prompt from `.claude/commands/agents/docx-producer.md`
- Pass: file path to the markdown source, application folder path, company name and role title, user's name from config, DOCX styling from config

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
