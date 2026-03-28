#!/usr/bin/env node

/**
 * Job Description URL Scraper
 *
 * Fetches a job posting URL and extracts the main content.
 * Uses targeted selectors for known job boards (Greenhouse, Lever, etc.)
 * and falls back to Mozilla Readability for unknown sites.
 *
 * Usage: node scripts/scrape-jd.js <url>
 * Output: Title on the first line, then the extracted text content.
 */

const { Readability } = require("@mozilla/readability");
const { JSDOM } = require("jsdom");

const url = process.argv[2];

if (!url) {
  console.error("Usage: node scripts/scrape-jd.js <url>");
  console.error('Example: node scripts/scrape-jd.js "https://boards.greenhouse.io/company/jobs/12345"');
  process.exit(1);
}

try {
  new URL(url);
} catch {
  console.error(`Error: Invalid URL: ${url}`);
  process.exit(1);
}

const parsed = new URL(url);
if (parsed.hostname.includes("linkedin.com")) {
  console.error("Error: LinkedIn requires authentication and blocks automated scraping.");
  console.error("Try one of these instead:");
  console.error("  1. Click 'Apply' on the LinkedIn posting to find the company's job board URL (e.g., Greenhouse, Lever, Workday) and provide that URL instead.");
  console.error("  2. Copy the job description text from the LinkedIn page and paste it directly.");
  process.exit(1);
}

/**
 * Job board-specific extraction rules.
 * Each entry: { match: hostname pattern, selectors: CSS selectors to try in order, titleSelector: optional }
 */
const JOB_BOARD_RULES = [
  {
    name: "Greenhouse",
    match: (host) => host.includes("greenhouse.io"),
    selectors: [".job__description", ".job-post__content", ".job-post"],
    titleSelector: ".job__title, .app-title",
  },
  {
    name: "Lever",
    match: (host) => host.includes("lever.co"),
    selectors: [".section-wrapper.page-full-width", ".posting-page .content"],
    titleSelector: ".posting-headline h2",
  },
  {
    name: "Workday",
    match: (host) => host.includes("myworkdayjobs.com") || host.includes("workday.com"),
    selectors: ['[data-automation-id="jobPostingDescription"]', ".job-description"],
    titleSelector: '[data-automation-id="jobPostingHeader"]',
  },
  {
    name: "Ashby",
    match: (host) => host.includes("ashbyhq.com"),
    selectors: [".ashby-job-posting-description", "main"],
    titleSelector: "h1",
  },
];

function cleanText(text) {
  return text
    .split("\n")
    .map((line) => line.trim())
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

async function scrape(url) {
  const response = await fetch(url, {
    headers: {
      "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
      Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9",
    },
    redirect: "follow",
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const html = await response.text();
  const dom = new JSDOM(html, { url });
  const doc = dom.window.document;
  const hostname = new URL(url).hostname;

  // Try job board-specific extraction first
  for (const rule of JOB_BOARD_RULES) {
    if (!rule.match(hostname)) continue;

    for (const selector of rule.selectors) {
      const el = doc.querySelector(selector);
      if (el && el.textContent.trim().length > 100) {
        let title = "Untitled";
        if (rule.titleSelector) {
          const titleEl = doc.querySelector(rule.titleSelector);
          if (titleEl) title = titleEl.textContent.trim();
        }
        if (title === "Untitled") {
          const h1 = doc.querySelector("h1");
          if (h1) title = h1.textContent.trim();
        }
        if (title === "Untitled") {
          title = doc.title || "Untitled";
        }

        console.log(`TITLE: ${title}`);
        console.log("---");
        console.log(cleanText(el.textContent));
        return;
      }
    }
    // Matched the board but no selector worked — fall through to Readability
  }

  // Fallback: Mozilla Readability
  const reader = new Readability(doc);
  const article = reader.parse();

  if (!article || !article.textContent.trim()) {
    throw new Error("Could not extract readable content from the page. The page may require JavaScript or login.");
  }

  const title = article.title || doc.title || "Untitled";
  console.log(`TITLE: ${title}`);
  console.log("---");
  console.log(cleanText(article.textContent));
}

scrape(url).catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});