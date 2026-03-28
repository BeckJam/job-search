# Job Search CLI

An AI-powered job application toolkit built on [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Paste a job description and get a tailored resume, cover letter, and ATS-optimized DOCX, all generated from your career master reference document.

## What It Does

1. **Analyzes** the job description for ATS keywords and researches the company
2. **Interviews** you with two focused questions to find your angle
3. **Writes** a tailored cover letter and resume through 5 progressive iterations each
4. **Generates** an ATS-clean DOCX ready for upload
5. **Reviews** the resume against ATS parsing rules and keyword coverage
6. **Updates** your master reference with new framings for future applications

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and configured
- Node.js 18+ (for DOCX generation)
- Python 3 (optional, for the standalone ATS scan script)

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/job-search-cli.git
cd job-search-cli

# 2. Install dependencies
npm install

# 3. Open Claude Code
claude

# 4. Run the skill
/job-search
```

On first run, the onboarding flow will:
- Ask for your name, contact info, and LinkedIn URL
- Create your `config.md` with preferences and styling defaults
- Create a blank master reference template

**Before your first application**, fill in your master reference with your career history, STAR projects, and skills. See `templates/example-master-reference.md` for a detailed example.

Then run `/job-search` again and paste a job description to generate your first application.

## How It Works

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
Phase 2: ATS keyword analysis + company research (parallel)
    |
    v
Phase 3: Two-question interview + narrative strategy
    |
    v
Phase 4: Create application folder (YYYY-MM-DD_Company_Role/)
    |
    v
Phase 5: Cover letter -> Resume -> DOCX -> ATS review (sequential)
    |
    v
Phase 6: Update master reference with new framings
    |
    v
Phase 7: Review with you
```

The orchestrator (`.claude/commands/job-search.md`) handles interactive steps and spawns focused sub-agents for writing and research. Each sub-agent receives only the context it needs, which produces better output than dumping the full conversation.

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

- **Cover Letter DOCX**: "Generate a DOCX for the cover letter"
- **Compensation Research**: "What does this role pay?"
- **Workday Formatter**: "Format the resume for Workday fields"

## Standalone Scripts

### DOCX Generator

```bash
node generate_resume_docx.js <input.md> <output.docx>
```

Converts a markdown resume into a DOCX using the project's formatting conventions. Useful as a manual fallback.

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
│       ├── resume-writer.md
│       └── workday-formatter.md
├── templates/
│   ├── master-reference-template.md   # Blank template
│   └── example-master-reference.md    # Filled-in example
├── scripts/
│   └── ats_scan.py
├── config.example.md                  # Config template
├── generate_resume_docx.js            # Standalone DOCX tool
├── CLAUDE.md
├── package.json
└── README.md
```

## Contributing

Contributions welcome! Please open an issue or pull request.

## License

MIT