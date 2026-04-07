#!/usr/bin/env python3
"""
Migrate job-search-cli memory into MemPalace.

Reads:
  - config.md (personal info, standing preferences, identity framing)
  - Master reference file (STAR projects, framings, experience, metrics)
  - Flat-file memories (~/.claude/projects/*/memory/*.md)

Creates palace structure:
  - career wing: identity, strengths, star-projects, experience, education, metrics, narrative-framings, application-tracker
  - preferences wing: writing-rules, feedback, employer-rules
  - applications wing: (empty, populated per-application going forward)

Populates knowledge graph with entity relationships.
"""

import os
import re
import sys
import glob
import json

def find_config():
    """Find config.md in the project root."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(project_root, "config.md")
    if not os.path.exists(config_path):
        print(f"ERROR: config.md not found at {config_path}")
        sys.exit(1)
    return config_path, project_root


def parse_config(config_path):
    """Extract key values from config.md."""
    with open(config_path, "r") as f:
        content = f.read()

    config = {}

    # Master reference path
    match = re.search(r"\*\*Master Reference\*\*:\s*(.+)", content)
    if match:
        config["master_ref_path"] = match.group(1).strip()

    # Identity framing (paragraph after ## Identity Framing)
    match = re.search(r"## Identity Framing\n\n(.+?)(?:\n\n##|\Z)", content, re.DOTALL)
    if match:
        config["identity_framing"] = match.group(1).strip()

    # Standing preferences (list items after ## Standing Preferences)
    match = re.search(r"## Standing Preferences\n\n(.+?)(?:\n\n##|\Z)", content, re.DOTALL)
    if match:
        config["standing_preferences"] = match.group(1).strip()

    # Banned phrases
    match = re.search(r"## Banned Phrases\n\n(.+?)(?:\n\n##|\Z)", content, re.DOTALL)
    if match:
        config["banned_phrases"] = match.group(1).strip()

    # Preferred phrases
    match = re.search(r"## Preferred Phrases\n\n(.+?)(?:\n\n##|\Z)", content, re.DOTALL)
    if match:
        config["preferred_phrases"] = match.group(1).strip()

    # Employer consolidation rules
    match = re.search(r"## Employer Consolidation Rules\n\n(.+?)(?:\n\n##|\Z)", content, re.DOTALL)
    if match:
        config["employer_rules"] = match.group(1).strip()

    return config


def parse_master_reference(filepath):
    """Parse master reference into discrete sections."""
    with open(filepath, "r") as f:
        content = f.read()

    sections = {}

    # Executive summary
    match = re.search(r"## EXECUTIVE SUMMARY\n+---\n\n(.+?)(?:\n---\n|\n## )", content, re.DOTALL)
    if not match:
        match = re.search(r"## EXECUTIVE SUMMARY\n\n(.+?)(?:\n---\n|\n## )", content, re.DOTALL)
    if match:
        sections["executive_summary"] = match.group(1).strip()

    # Core strengths
    match = re.search(r"## CORE STRENGTHS & SKILLS\n\n(.+?)(?:\n---\n\n## )", content, re.DOTALL)
    if match:
        sections["core_strengths"] = match.group(1).strip()

    # STAR projects: split by ### N. pattern
    star_match = re.search(r"## STAR PROJECT LIBRARY\n\n(.+?)(?:\n## EXPERIENCE BY ROLE)", content, re.DOTALL)
    if star_match:
        star_text = star_match.group(1).strip()
        # Split on ### followed by a number and period
        projects = re.split(r"\n---\n\n(?=### \d+\.)", star_text)
        # Clean up: first element might have preamble text
        star_projects = []
        for p in projects:
            p = p.strip()
            if p.startswith("### ") or p.startswith("Core achievements"):
                star_projects.append(p)
        sections["star_projects"] = star_projects

    # Experience by role type
    exp_match = re.search(r"## EXPERIENCE BY ROLE TYPE & LEVEL\n\n(.+?)(?:\n## ADDITIONAL PROFESSIONAL|\n## EDUCATION)", content, re.DOTALL)
    if exp_match:
        exp_text = exp_match.group(1).strip()
        # Split by ### heading (role type)
        role_sections = re.split(r"\n---\n\n(?=### )", exp_text)
        sections["experience_sections"] = [s.strip() for s in role_sections if s.strip()]

    # Additional experience
    add_match = re.search(r"## ADDITIONAL PROFESSIONAL EXPERIENCE\n\n(.+?)(?:\n---\n\n## )", content, re.DOTALL)
    if add_match:
        sections["additional_experience"] = add_match.group(1).strip()

    # Education
    edu_match = re.search(r"## EDUCATION & CERTIFICATIONS\n\n(.+?)(?:\n---\n\n## )", content, re.DOTALL)
    if edu_match:
        sections["education"] = edu_match.group(1).strip()

    # Key metrics
    metrics_match = re.search(r"## KEY METRICS — QUICK REFERENCE\n\n(.+?)(?:\n---\n\n## )", content, re.DOTALL)
    if metrics_match:
        sections["metrics"] = metrics_match.group(1).strip()

    # Narrative framings: split by ### heading
    framings_match = re.search(r"## NARRATIVE FRAMINGS DEVELOPED\n\n(.+?)(?:\n---\n\n## |\Z)", content, re.DOTALL)
    if framings_match:
        framings_text = framings_match.group(1).strip()
        framings = re.split(r"\n\n(?=### )", framings_text)
        sections["narrative_framings"] = [f.strip() for f in framings if f.strip()]

    # Applications tracker
    apps_match = re.search(r"## APPLICATIONS COMPLETED\n\n(.+?)(?:\n---\n|\Z)", content, re.DOTALL)
    if apps_match:
        sections["applications"] = apps_match.group(1).strip()

    return sections


def find_flat_memories(project_root):
    """Find flat-file memory .md files."""
    # Check common locations for Claude project memory
    home = os.path.expanduser("~")
    patterns = [
        os.path.join(home, ".claude", "projects", "*", "memory", "*.md"),
    ]

    memories = []
    for pattern in patterns:
        for filepath in glob.glob(pattern):
            basename = os.path.basename(filepath)
            if basename == "MEMORY.md":
                continue
            memories.append(filepath)

    return memories


def parse_memory_file(filepath):
    """Parse a flat-file memory with frontmatter."""
    with open(filepath, "r") as f:
        content = f.read()

    result = {"filepath": filepath, "filename": os.path.basename(filepath)}

    # Parse frontmatter
    fm_match = re.match(r"^---\n(.+?)\n---\n\n?(.+)", content, re.DOTALL)
    if fm_match:
        frontmatter = fm_match.group(1)
        body = fm_match.group(2).strip()

        for line in frontmatter.split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                result[key.strip()] = val.strip()

        result["body"] = body
    else:
        result["body"] = content.strip()

    return result


def migrate():
    """Run the full migration."""
    from mempalace.mcp_server import tool_add_drawer, tool_status, KnowledgeGraph

    config_path, project_root = find_config()
    config = parse_config(config_path)

    print("=" * 60)
    print("  MemPalace Migration for job-search-cli")
    print("=" * 60)
    print()

    # Check current palace status
    status = tool_status()
    total_existing = status.get("total_drawers", 0)
    if total_existing > 0:
        print(f"  Palace already has {total_existing} drawers.")
        print("  Skipping migration to avoid duplicates.")
        print("  To re-migrate, clear the palace first.")
        return

    counts = {
        "star_projects": 0,
        "framings": 0,
        "experience": 0,
        "feedback": 0,
        "kg_triples": 0,
        "other": 0,
    }

    # ── CAREER WING ──────────────────────────────────────────

    print("  [1/5] Importing career data from master reference...")

    master_ref_path = config.get("master_ref_path")
    if not master_ref_path or not os.path.exists(master_ref_path):
        print(f"  WARNING: Master reference not found at {master_ref_path}")
        print("  Skipping career data import.")
    else:
        sections = parse_master_reference(master_ref_path)

        # Identity: executive summary + identity framing
        identity_content = ""
        if config.get("identity_framing"):
            identity_content += f"Identity Framing:\n{config['identity_framing']}\n\n"
        if sections.get("executive_summary"):
            identity_content += f"Executive Summary:\n{sections['executive_summary']}"
        if identity_content:
            result = tool_add_drawer("career", "identity", identity_content, source_file="master-reference")
            if result.get("success"):
                counts["other"] += 1

        # Core strengths
        if sections.get("core_strengths"):
            result = tool_add_drawer("career", "strengths", sections["core_strengths"], source_file="master-reference")
            if result.get("success"):
                counts["other"] += 1

        # STAR projects: one drawer per project
        for project in sections.get("star_projects", []):
            if project.startswith("Core achievements"):
                continue
            # Extract project name from ### N. Title
            name_match = re.match(r"### \d+\.\s*(.+?)(?:\n|$)", project)
            source = f"star-project: {name_match.group(1)}" if name_match else "star-project"
            result = tool_add_drawer("career", "star-projects", project, source_file=source)
            if result.get("success"):
                counts["star_projects"] += 1
            elif result.get("reason") == "duplicate":
                print(f"    Skipped duplicate: {source}")

        # Experience sections
        for section in sections.get("experience_sections", []):
            name_match = re.match(r"### (.+?)(?:\n|$)", section)
            source = f"experience: {name_match.group(1)}" if name_match else "experience"
            result = tool_add_drawer("career", "experience", section, source_file=source)
            if result.get("success"):
                counts["experience"] += 1

        # Additional experience
        if sections.get("additional_experience"):
            result = tool_add_drawer("career", "experience", sections["additional_experience"], source_file="additional-experience")
            if result.get("success"):
                counts["experience"] += 1

        # Education
        if sections.get("education"):
            result = tool_add_drawer("career", "education", sections["education"], source_file="master-reference")
            if result.get("success"):
                counts["other"] += 1

        # Metrics
        if sections.get("metrics"):
            result = tool_add_drawer("career", "metrics", sections["metrics"], source_file="master-reference")
            if result.get("success"):
                counts["other"] += 1

        # Narrative framings: one drawer per framing
        for framing in sections.get("narrative_framings", []):
            name_match = re.match(r"### (.+?)(?:\n|$)", framing)
            source = f"framing: {name_match.group(1)}" if name_match else "framing"
            result = tool_add_drawer("career", "narrative-framings", framing, source_file=source)
            if result.get("success"):
                counts["framings"] += 1

        # Application tracker
        if sections.get("applications"):
            result = tool_add_drawer("career", "application-tracker", sections["applications"], source_file="master-reference")
            if result.get("success"):
                counts["other"] += 1

        print(f"    {counts['star_projects']} STAR projects")
        print(f"    {counts['framings']} narrative framings")
        print(f"    {counts['experience']} experience sections")
        print(f"    {counts['other']} other sections (identity, strengths, education, metrics, tracker)")

    # ── PREFERENCES WING ─────────────────────────────────────

    print("  [2/5] Importing standing preferences from config...")

    # Writing rules: standing preferences + banned + preferred phrases
    writing_rules = ""
    if config.get("standing_preferences"):
        writing_rules += f"Standing Preferences:\n{config['standing_preferences']}\n\n"
    if config.get("banned_phrases"):
        writing_rules += f"Banned Phrases:\n{config['banned_phrases']}\n\n"
    if config.get("preferred_phrases"):
        writing_rules += f"Preferred Phrases:\n{config['preferred_phrases']}"
    if writing_rules:
        result = tool_add_drawer("preferences", "writing-rules", writing_rules.strip(), source_file="config.md")
        if result.get("success"):
            print("    Writing rules imported")

    # Employer consolidation rules
    if config.get("employer_rules"):
        result = tool_add_drawer("preferences", "employer-rules", config["employer_rules"], source_file="config.md")
        if result.get("success"):
            print("    Employer rules imported")

    # ── FLAT-FILE MEMORIES ───────────────────────────────────

    print("  [3/5] Importing flat-file memories...")

    memories = find_flat_memories(project_root)
    for mem_path in memories:
        mem = parse_memory_file(mem_path)
        result = tool_add_drawer("preferences", "feedback", mem["body"], source_file=mem["filename"])
        if result.get("success"):
            counts["feedback"] += 1
        elif result.get("reason") == "duplicate":
            print(f"    Skipped duplicate: {mem['filename']}")

    print(f"    {counts['feedback']} feedback memories imported")

    # ── KNOWLEDGE GRAPH ──────────────────────────────────────

    print("  [4/5] Populating knowledge graph...")

    kg = KnowledgeGraph()

    # Core entity relationships
    kg_triples = [
        ("Jim Beck", "works_at", "Blue Origin", "2020-02", "2026-01"),
        ("Jim Beck", "works_at", "Cru", "2016-08", "2019-05"),
        ("Jim Beck", "works_at", "Disney", "2019-05", "2019-07"),
        ("Jim Beck", "works_at", "Ballistiq", "2019-09", "2020-02"),
        ("Jim Beck", "works_at", "Chinook Fire Protection", "2009-01", "2010-01"),
        ("Jim Beck", "works_at", "Lydig Construction", "2007-01", "2009-01"),
        ("Jim Beck", "has_degree", "MBA, University of Washington Foster School of Business", "2020", None),
        ("Jim Beck", "has_degree", "BS Construction Management, Central Washington University", "2007", None),
        ("Jim Beck", "has_cert", "Scrum Certified Product Owner", None, None),
        ("Jim Beck", "presented_at", "Dreamforce 2023", "2023", None),
        ("Blue Origin", "product", "Live Streaming Infrastructure (IVS)"),
        ("Blue Origin", "product", "Salesforce CRM Platform"),
        ("Blue Origin", "product", "Operational Technology Platform"),
        ("Blue Origin", "product", "Customer Onboarding Platform"),
        ("Blue Origin", "product", "Competitive Intelligence LLM Agent"),
        ("Blue Origin", "product", "blueorigin.com (CMS)"),
        ("Blue Origin", "product", "MCP for Salesforce"),
        ("Blue Origin", "product", "Broadcast Efficiency Agents"),
        ("Cru", "product", "MPDX CRM Platform"),
        ("Jim Beck", "built", "Live Streaming Infrastructure (IVS)"),
        ("Jim Beck", "built", "Salesforce CRM Platform"),
        ("Jim Beck", "built", "Operational Technology Platform"),
        ("Jim Beck", "built", "MPDX CRM Platform"),
        ("Jim Beck", "built", "Competitive Intelligence LLM Agent"),
        ("Jim Beck", "built", "MCP for Salesforce"),
        ("Jim Beck", "built", "Broadcast Efficiency Agents"),
        ("Jim Beck", "lives_in", "Gig Harbor, WA"),
    ]

    for triple in kg_triples:
        subject, predicate, obj = triple[0], triple[1], triple[2]
        valid_from = triple[3] if len(triple) > 3 else None
        valid_to = triple[4] if len(triple) > 4 else None
        try:
            kg.add_triple(subject, predicate, obj, valid_from=valid_from, valid_to=valid_to)
            counts["kg_triples"] += 1
        except Exception as e:
            print(f"    KG error: {e}")

    print(f"    {counts['kg_triples']} knowledge graph triples created")

    # ── AAAK COMPRESSION ─────────────────────────────────────

    print("  [5/5] Running AAAK compression...")
    try:
        from subprocess import run as subprocess_run
        result = subprocess_run(["mempalace", "compress"], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("    Compression complete")
        else:
            print(f"    Compression skipped: {result.stderr.strip()[:100]}")
    except Exception as e:
        print(f"    Compression skipped: {e}")

    # ── SUMMARY ──────────────────────────────────────────────

    print()
    print("=" * 60)
    print("  Migration Complete")
    print("=" * 60)
    print(f"  STAR projects:       {counts['star_projects']}")
    print(f"  Narrative framings:  {counts['framings']}")
    print(f"  Experience sections: {counts['experience']}")
    print(f"  Feedback memories:   {counts['feedback']}")
    print(f"  KG triples:          {counts['kg_triples']}")
    print(f"  Other sections:      {counts['other']}")
    total = sum(counts.values())
    print(f"  Total items:         {total}")
    print()
    print("  Original files are untouched. Archive them after validation.")
    print("  Run 'mempalace status' to verify.")
    print()


if __name__ == "__main__":
    migrate()
