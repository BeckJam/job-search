# Job Search CLI

An AI-powered job application toolkit built as a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) slash command. Paste a job description and get a tailored resume, cover letter, and ATS-optimized DOCX, all generated from your career master reference document.

Built for Claude Code, but the architecture (orchestrator + sub-agent prompts in markdown) could be adapted for [OpenClaw](https://github.com/AiCodingBattle/openclaw) or any agent framework that supports multi-agent orchestration.

## What It Does

1. **Creates** an application folder and saves the JD immediately
2. **Analyzes** the job description for ATS keywords and researches the company (in parallel)
3. **Interviews** you with two focused questions to find your angle
4. **Develops** a narrative strategy with a voice brief for consistent tone across documents
5. **Writes** a tailored cover letter and resume in parallel through configurable progressive iterations
6. **Reviews** the resume against ATS parsing rules and keyword coverage
7. **Updates** your master reference with new framings for future applications
8. **Generates** ATS-clean DOCX files for both resume and cover letter after you approve the drafts

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and configured (see [installation guide](https://docs.anthropic.com/en/docs/claude-code/getting-started))
- Node.js 18+ (for DOCX generation and JD scraping)
- Python 3 (optional, for the standalone ATS scan script)

## Installation

### 1. Install Claude Code

If you don't have Claude Code yet:

```bash
npm install -g @anthropic-ai/claude-code
```

You'll need an Anthropic API key or a Claude Pro/Max subscription. See the [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code/getting-started) for full setup instructions.

### 2. Clone and install

```bash
git clone https://github.com/BeckJam/job-search-cli.git
cd job-search-cli
npm install
```

### 3. Launch Claude Code from the project directory

```bash
claude
```

This is important: Claude Code reads the `.claude/commands/` directory to register slash commands. You must launch it from the project root.

### 4. Run the slash command

```
/job-search
```

On first run, the onboarding flow will:
- Ask for your name, contact info, and LinkedIn URL
- Offer to seed your master reference from existing resumes/cover letters (drag and drop file paths)
- If you provide documents: automatically extract your career history, STAR projects, skills, and writing preferences
- If you don't have documents: create a blank template for you to fill in manually

See `templates/example-master-reference.md` for what a completed master reference looks like.

### 5. Apply for a job

Run `/job-search` again and either paste a job description or provide a URL to the job posting. The scraper automatically extracts JD content from most job board URLs (Greenhouse, Lever, Workday, etc.).

## How It Works

This is a Claude Code [slash command](https://docs.anthropic.com/en/docs/claude-code/slash-commands) that uses an orchestrator + sub-agent architecture. The orchestrator lives at `.claude/commands/job-search.md` and handles interactive steps (interviews, approvals). It spawns focused sub-agents from `.claude/commands/agents/` for writing and research. Each sub-agent receives only the context it needs, which produces better output than dumping the full conversation.

```
/job-search
    |
    v
Phase 0: Config check (first-run onboarding if needed)
    |
    v
Phase 1: Load master reference
    |
    v
Phase 2: Create application folder + save JD
         (URL detection and scraping if needed)
    |
    v
Phase 3: ATS keyword analysis + company research (parallel)
    |
    v
Phase 4: Two-question interview + narrative strategy + voice brief
    |
    v
Phase 5: Cover letter + resume writing (parallel, voice brief keeps them consistent)
    |
    v
Phase 6: ATS review + master reference update (parallel)
    |
    v
Phase 7: Review with you, apply any edits
    |
    v
Phase 8: DOCX generation (resume + cover letter, after your approval)
```

## Configuration

All personal settings live in `config.md` (gitignored, created from `config.example.md`).

| Section | What It Controls |
|---|---|
| Personal Information | Name, phone, email, LinkedIn, location |
| File Paths | Master reference location |
| Identity Framing | Your core positioning statement |
| Standing Preferences | Writing rules applied to every document |
| Banned/Preferred Phrases | Term substitutions and blacklist |
| Employer Consolidation Rules | How multi-title tenures are presented |
| Writing Agent Settings | Number of progressive iterations (default: 3) |
| DOCX Styling | Accent color, font, margins |

## Master Reference

Your master reference is the single source of truth for all applications. It should include:

- **Professional Summary**: Your core positioning (2-3 sentences)
- **Career History**: Every role with achievements and metrics
- **STAR Projects**: Detailed Situation/Task/Action/Result stories (5-15)
- **Proven Narrative Framings**: Phrases that have worked in past applications
- **Skills & Technologies**: Comprehensive list (20-30 items)
- **Education & Certifications**
- **Applications Tracker**: Auto-updated after each application

The more detail you provide, the better your tailored documents will be. See `templates/example-master-reference.md` for what a filled-in master reference looks like.

## On-Demand Tools

Beyond the main application workflow, you can ask for:

- **DOCX Generation**: "Generate DOCX files for this application"
- **Compensation Research**: "What does this role pay?"
- **Workday Formatter**: "Format the resume for Workday fields"

## Standalone Scripts

### JD Scraper

```bash
node scripts/scrape-jd.js "https://boards.greenhouse.io/company/jobs/12345"
```

Extracts job description text from a URL using Mozilla's Readability algorithm (the same one behind Firefox Reader View). Works with most job boards: Greenhouse, Lever, Workday, company career pages, etc. Pages that require JavaScript rendering or login may not work.

### DOCX Generators

```bash
# Resume
node generate_resume_docx.js <input.md> <output.docx> '[optionsJson]'

# Cover Letter
node generate_cover_letter_docx.js <input.md> <output.docx> '[optionsJson]'
```

Both scripts accept an optional JSON string for styling: `accentColor`, `font`, `fontFallback`, `margins`. The cover letter script also accepts `userName` and `role`. The DOCX producer agent calls these automatically, but they work as standalone tools too.

### ATS Scanner

```bash
python3 scripts/ats_scan.py <resume.md>
```

Scans a resume for common ATS compatibility issues.

## Project Structure

```
job-search-cli/
├── .claude/commands/
│   ├── job-search.md              # Orchestrator (slash command)
│   └── agents/
│       ├── ats-keyword-analysis.md
│       ├── ats-review.md
│       ├── company-research.md
│       ├── compensation-research.md
│       ├── cover-letter-writer.md
│       ├── docx-producer.md
│       ├── master-reference-updater.md
│       ├── reference-seeder.md
│       ├── resume-writer.md
│       └── workday-formatter.md
├── templates/
│   ├── master-reference-template.md   # Blank template
│   └── example-master-reference.md    # Filled-in example
├── scripts/
│   ├── scrape-jd.js                   # JD URL scraper
│   └── ats_scan.py                    # Standalone ATS scanner
├── config.example.md                  # Config template
├── generate_resume_docx.js            # Resume DOCX generator
├── generate_cover_letter_docx.js      # Cover letter DOCX generator
├── CLAUDE.md
├── package.json
└── README.md
```

## Contributing

Contributions welcome! Please open an issue or pull request.

## License

CC BY-NC-SA 4.0 — See [LICENSE](LICENSE) for details.
