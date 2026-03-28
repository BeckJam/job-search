#!/usr/bin/env python3
"""
ATS Keyword Scanner — Compare a resume against a job description.

Usage:
    python3 ats_scan.py <resume.md> <job_description.txt>
    python3 ats_scan.py <resume.md> <job_description.txt> --json
    python3 ats_scan.py <resume.md> <job_description.txt> --missing-only

Examples:
    python3 scripts/ats_scan.py \
        2026-03-26_SitusAMC_Head-of-Product-Corporate-Applications/resume.md \
        2026-03-26_SitusAMC_Head-of-Product-Corporate-Applications/jd.txt
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


# ---------------------------------------------------------------------------
# Keyword extraction
# ---------------------------------------------------------------------------

# Common words to ignore when extracting keywords
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "need",
    "must", "that", "this", "these", "those", "it", "its", "they", "them",
    "their", "we", "our", "you", "your", "he", "she", "his", "her", "who",
    "which", "what", "where", "when", "how", "all", "each", "every", "both",
    "few", "more", "most", "other", "some", "such", "no", "not", "only",
    "same", "so", "than", "too", "very", "just", "about", "above", "after",
    "again", "also", "any", "because", "before", "between", "come", "also",
    "into", "through", "during", "here", "there", "then", "once", "further",
    "if", "while", "up", "out", "off", "over", "under", "own", "able",
    "including", "across", "e.g.", "e.g", "etc", "within", "well", "new",
    "looking", "join", "team", "role", "company", "candidate", "position",
    "responsibilities", "requirements", "qualifications", "required",
    "preferred", "experience", "years", "year", "work", "working", "strong",
    "excellent", "proven", "demonstrated", "ability", "skills", "knowledge",
    "understanding", "ensure", "drive", "driving", "driven", "develop",
    "developing", "manage", "managing", "lead", "leading", "build",
    "building", "establish", "create", "define", "promote", "champion",
    "implement", "support", "serve", "provide", "include", "level",
    "based", "related", "relevant", "success", "successful", "clear",
    "key", "major", "primary", "us", "get", "like", "whether", "per",
    "along", "among", "around", "upon", "toward", "towards", "without",
    # JD boilerplate filler
    "passionate", "careers", "career", "realize", "potential", "amazing",
    "someone", "yourself", "advocate", "nimble", "dream", "think", "act",
    "local", "global", "start", "stay", "overview", "essential",
    "responsible", "requires", "applicable", "appropriate", "closely",
    "facilitate", "discussions", "communicate", "interface", "translate",
    "embed", "embedded", "institutionalize", "propositions", "criteria",
    "tied", "time", "near-term", "executive-level", "cases", "utilize",
    "utilization", "exposure", "familiarity", "background", "partnership",
    "relationships", "reporting", "engagement", "others", "everyone",
    "people", "together", "proudly", "unique", "match", "one", "big",
    "stand", "job", "client", "businesses", "industry", "veteran",
    "technologist", "estate", "real", "solutions", "unstructured",
    "units", "standards", "value-driven", "secure", "compliant",
    "advanced", "progressive", "mid-to-large", "platform-based",
    "technology-enabled", "high-growth", "third-party", "acquired",
    "ecosystems", "environments", "operate", "head", "track",
    "dependencies", "optimization",
}

# Multi-word phrases to look for (domain-specific)
# These get checked first before single-word extraction
KNOWN_PHRASES = [
    # Product
    "product management", "product manager", "product owner",
    "product vision", "product strategy", "product roadmap",
    "product operating model", "product delivery", "product design",
    "product discovery", "product validation", "product governance",
    "product lifecycle", "lifecycle management",
    "product-based", "project-based",
    "project-to-product",
    # Enterprise / corporate
    "corporate applications", "enterprise platforms", "enterprise systems",
    "business systems", "enterprise architecture", "enterprise integration",
    "digital transformation", "change management", "risk management",
    "vendor management", "stakeholder management",
    "cross-functional leadership", "cross-functional",
    "executive communication", "executive stakeholder",
    # Technology
    "cloud-native", "cloud native", "api-driven", "api driven",
    "workflow automation", "data governance", "data strategy",
    "data-driven", "data driven", "data accuracy",
    "ai enablement", "ai-enabled", "ai enabled",
    "machine learning", "natural language",
    "user experience", "self-service", "self service",
    # Business
    "financial acumen", "investment portfolio",
    "private equity", "pe-backed", "pe backed",
    "business strategy", "business outcomes",
    "cost center", "strategic enabler",
    "value realization", "outcome measurement",
    "funding model", "investment model",
    "backlog governance", "quarterly planning",
    "intake and demand", "demand management",
    "agile product delivery", "agile delivery",
    "iterative release",
    # Platforms
    "sales cloud", "experience cloud", "govcloud",
    "help desk",
    # Specific terms
    "saas", "erp", "hris", "crm", "fp&a",
    "okr", "kpi",
]


def normalize(text: str) -> str:
    """Lowercase and normalize whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def extract_phrases(text: str) -> dict[str, int]:
    """Extract known multi-word phrases from text with counts."""
    norm = normalize(text)
    found = {}
    for phrase in KNOWN_PHRASES:
        p = normalize(phrase)
        count = len(re.findall(re.escape(p), norm))
        if count > 0:
            found[p] = count
    return found


def extract_single_keywords(text: str, min_len: int = 3) -> Counter:
    """Extract meaningful single keywords from text."""
    norm = normalize(text)
    # Remove markdown syntax
    norm = re.sub(r"[#*_\[\]()>`~|]", " ", norm)
    # Split on non-alphanumeric (keep hyphens and ampersands within words)
    tokens = re.findall(r"[a-z][a-z0-9&-]*[a-z0-9]|[a-z]", norm)
    keywords = [t for t in tokens if t not in STOP_WORDS and len(t) >= min_len]
    return Counter(keywords)


def extract_all_keywords(text: str) -> dict[str, int]:
    """Extract both phrases and single keywords, phrases taking priority."""
    phrases = extract_phrases(text)
    singles = extract_single_keywords(text)
    # Merge: phrases first, then singles not already covered by phrases
    all_kw = dict(phrases)
    phrase_words = set()
    for p in phrases:
        phrase_words.update(p.split())
    for word, count in singles.items():
        if word not in phrase_words:
            all_kw[word] = count
    return all_kw


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_keyword(keyword: str, count: int, jd_text: str) -> int:
    """
    Score a keyword 1-10 based on frequency, position, and context.
    """
    norm_jd = normalize(jd_text)
    score = min(count * 2, 6)  # frequency: max 6 points

    # Boost if in first 500 chars (title/intro area)
    first_chunk = norm_jd[:500]
    if keyword in first_chunk:
        score += 2

    # Boost if in a "required" or "qualifications" section
    req_section = ""
    for marker in ["qualifications", "requirements", "required", "must have"]:
        idx = norm_jd.find(marker)
        if idx >= 0:
            req_section = norm_jd[idx:]
            break
    if req_section and keyword in req_section:
        score += 2

    return min(score, 10)


def check_resume_match(keyword: str, resume_text: str) -> str:
    """
    Check if keyword appears in resume. Returns:
    'exact', 'variant', or 'missing'.
    """
    norm = normalize(resume_text)

    # Exact match
    if re.search(r"(?<![a-z-])" + re.escape(keyword) + r"(?![a-z-])", norm):
        return "exact"

    # Variant matching: check for related forms
    # Hyphenated vs spaced (e.g., "cloud-native" vs "cloud native")
    if "-" in keyword:
        spaced = keyword.replace("-", " ")
        if spaced in norm:
            return "variant"
    else:
        hyphenated = keyword.replace(" ", "-")
        if hyphenated in norm:
            return "variant"

    # Plural/singular
    if keyword.endswith("s"):
        singular = keyword[:-1]
        if len(singular) >= 3 and singular in norm:
            return "variant"
    else:
        plural = keyword + "s"
        if plural in norm:
            return "variant"

    # Gerund/base form
    if keyword.endswith("ing"):
        base = keyword[:-3]
        if len(base) >= 3 and re.search(r"(?<![a-z])" + re.escape(base), norm):
            return "variant"
    elif keyword.endswith("tion"):
        base = keyword[:-4]
        if len(base) >= 3 and re.search(r"(?<![a-z])" + re.escape(base), norm):
            return "variant"

    return "missing"


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(jd_path: str, resume_path: str) -> dict:
    """Generate the full ATS scan report."""
    jd_text = Path(jd_path).read_text(encoding="utf-8")
    resume_text = Path(resume_path).read_text(encoding="utf-8")

    # Extract JD keywords
    jd_keywords = extract_all_keywords(jd_text)

    # Score and check each keyword
    results = []
    for kw, count in jd_keywords.items():
        importance = score_keyword(kw, count, jd_text)
        match_status = check_resume_match(kw, resume_text)
        results.append({
            "keyword": kw,
            "jd_count": count,
            "importance": importance,
            "match": match_status,
        })

    # Sort by importance descending, then alphabetical
    results.sort(key=lambda x: (-x["importance"], x["keyword"]))

    # Calculate scores
    total = len(results)
    exact = sum(1 for r in results if r["match"] == "exact")
    variant = sum(1 for r in results if r["match"] == "variant")
    missing = sum(1 for r in results if r["match"] == "missing")

    high_priority = [r for r in results if r["importance"] >= 7]
    hp_total = len(high_priority)
    hp_matched = sum(1 for r in high_priority if r["match"] != "missing")

    report = {
        "total_keywords": total,
        "exact_matches": exact,
        "variant_matches": variant,
        "missing": missing,
        "total_coverage_pct": round((exact + variant) / total * 100, 1) if total else 0,
        "exact_coverage_pct": round(exact / total * 100, 1) if total else 0,
        "high_priority_total": hp_total,
        "high_priority_matched": hp_matched,
        "high_priority_coverage_pct": round(hp_matched / hp_total * 100, 1) if hp_total else 0,
        "keywords": results,
    }
    return report


def print_report(report: dict, missing_only: bool = False):
    """Print a formatted text report."""
    print()
    print("=" * 70)
    print("  ATS KEYWORD SCAN REPORT")
    print("=" * 70)
    print()

    # Summary scores
    print(f"  Total keywords extracted:     {report['total_keywords']}")
    print(f"  Exact matches:                {report['exact_matches']}")
    print(f"  Variant matches:              {report['variant_matches']}")
    print(f"  Missing:                       {report['missing']}")
    print()
    print(f"  Total coverage:               {report['total_coverage_pct']}%")
    print(f"  Exact match rate:             {report['exact_coverage_pct']}%")
    print(f"  High-priority coverage:       {report['high_priority_coverage_pct']}% ({report['high_priority_matched']}/{report['high_priority_total']})")
    print()

    # Overall grade
    pct = report["total_coverage_pct"]
    if pct >= 90:
        grade = "A"
    elif pct >= 80:
        grade = "B+"
    elif pct >= 70:
        grade = "B"
    elif pct >= 60:
        grade = "C"
    else:
        grade = "D"
    print(f"  Overall grade:                {grade}")
    print()
    print("-" * 70)

    if missing_only:
        print()
        print("  MISSING KEYWORDS (sorted by importance)")
        print()
        missing_kws = [r for r in report["keywords"] if r["match"] == "missing"]
        if not missing_kws:
            print("  None! All keywords matched.")
        else:
            print(f"  {'Keyword':<40} {'Importance':>10} {'JD Count':>10}")
            print(f"  {'-'*40} {'-'*10} {'-'*10}")
            for r in missing_kws:
                print(f"  {r['keyword']:<40} {r['importance']:>10} {r['jd_count']:>10}")
    else:
        # Full keyword table
        print()
        print(f"  {'Keyword':<40} {'Score':>6} {'Match':>10} {'JD#':>5}")
        print(f"  {'-'*40} {'-'*6} {'-'*10} {'-'*5}")

        for r in report["keywords"]:
            match_display = r["match"].upper()
            if r["match"] == "missing":
                match_display = "** MISS **"
            elif r["match"] == "variant":
                match_display = "variant"
            else:
                match_display = "exact"
            print(f"  {r['keyword']:<40} {r['importance']:>6} {match_display:>10} {r['jd_count']:>5}")

    print()
    print("-" * 70)

    # Action items: top missing keywords
    missing_high = [r for r in report["keywords"] if r["match"] == "missing" and r["importance"] >= 5]
    if missing_high:
        print()
        print("  TOP MISSING KEYWORDS TO ADDRESS:")
        print()
        for r in missing_high[:10]:
            print(f"    [{r['importance']}/10]  {r['keyword']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="ATS Keyword Scanner: compare resume against job description"
    )
    parser.add_argument("resume", help="Path to resume file (markdown or text)")
    parser.add_argument("jd", help="Path to job description file (text)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--missing-only", action="store_true", help="Show only missing keywords")

    args = parser.parse_args()

    if not Path(args.resume).exists():
        print(f"Error: resume file not found: {args.resume}", file=sys.stderr)
        sys.exit(1)
    if not Path(args.jd).exists():
        print(f"Error: JD file not found: {args.jd}", file=sys.stderr)
        sys.exit(1)

    report = generate_report(args.jd, args.resume)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report, missing_only=args.missing_only)


if __name__ == "__main__":
    main()
