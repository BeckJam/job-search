#!/usr/bin/env node

/**
 * Job Description URL Scraper
 *
 * Fetches a job posting URL and extracts the main content using
 * Mozilla's Readability algorithm (the same one behind Firefox Reader View).
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
  const reader = new Readability(dom.window.document);
  const article = reader.parse();

  if (!article || !article.textContent.trim()) {
    throw new Error("Could not extract readable content from the page. The page may require JavaScript or login.");
  }

  // Clean up whitespace: collapse multiple blank lines, trim lines
  const cleaned = article.textContent
    .split("\n")
    .map((line) => line.trim())
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  const title = article.title || "Untitled";
  console.log(`TITLE: ${title}`);
  console.log("---");
  console.log(cleaned);
}

scrape(url).catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});