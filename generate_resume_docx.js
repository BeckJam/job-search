#!/usr/bin/env node

/**
 * Standalone resume DOCX generator.
 * Converts a markdown resume (using the project's formatting conventions) into an ATS-friendly DOCX.
 *
 * Usage: node generate_resume_docx.js <input.md> <output.docx> [optionsJson]
 *
 * Options (as JSON string in argv[4]):
 *   accentColor  - Hex color for name/headers (default: "#1B3A5C")
 *   font         - Primary font (default: "Aptos")
 *   fontFallback - Fallback font (default: "Calibri")
 *   margins      - Margins in inches (default: 0.7)
 */

const fs = require("fs");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  TabStopPosition,
  TabStopType,
  AlignmentType,
  LevelFormat,
  convertInchesToTwip,
  BorderStyle,
} = require("docx");

const inputPath = process.argv[2];
const outputPath = process.argv[3];
const optionsJson = process.argv[4] || "{}";

if (!inputPath || !outputPath) {
  console.error(
    "Usage: node generate_resume_docx.js <input.md> <output.docx> [optionsJson]"
  );
  console.error(
    'Example: node generate_resume_docx.js ./resume.md ./resume.docx \'{"accentColor":"#1B3A5C"}\''
  );
  process.exit(1);
}

if (!fs.existsSync(inputPath)) {
  console.error(`Error: Input file not found: ${inputPath}`);
  process.exit(1);
}

const options = JSON.parse(optionsJson);
const ACCENT_COLOR = (options.accentColor || "#1B3A5C").replace("#", "");
const FONT = options.font || "Aptos";
const FONT_FALLBACK = options.fontFallback || "Calibri";
const MARGIN_INCHES = options.margins || 0.7;

const PAGE_WIDTH_TWIP = 12240;
const MARGIN = convertInchesToTwip(MARGIN_INCHES);
const USABLE = PAGE_WIDTH_TWIP - 2 * MARGIN;

const src = fs.readFileSync(inputPath, "utf-8");
const lines = src.split("\n");

const children = [];

function makeRun(text, opts = {}) {
  return new TextRun({
    text,
    font: { name: FONT, fallback: FONT_FALLBACK },
    size: (opts.size || 10.5) * 2, // half-points
    bold: opts.bold || false,
    italics: opts.italics || false,
    color: opts.color || "000000",
  });
}

function parseBoldSegments(text, baseSize) {
  const runs = [];
  const regex = /\*\*(.+?)\*\*/g;
  let last = 0;
  let m;
  while ((m = regex.exec(text)) !== null) {
    if (m.index > last) {
      runs.push(makeRun(text.slice(last, m.index), { size: baseSize }));
    }
    runs.push(makeRun(m[1], { size: baseSize, bold: true }));
    last = m.index + m[0].length;
  }
  if (last < text.length) {
    runs.push(makeRun(text.slice(last), { size: baseSize }));
  }
  return runs;
}

let i = 0;
let isFirstH1 = true;
let isFirstPipeLine = true;

while (i < lines.length) {
  const line = lines[i].trim();

  // Skip horizontal rules
  if (/^---+$/.test(line)) {
    i++;
    continue;
  }

  // Skip empty lines
  if (line === "") {
    i++;
    continue;
  }

  // # Name (H1) — 18pt bold, centered, accent color
  if (/^# /.test(line)) {
    const name = line.replace(/^# /, "");
    children.push(
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 0, line: 240 },
        children: [
          makeRun(name, { size: 18, bold: true, color: ACCENT_COLOR }),
        ],
      })
    );
    isFirstH1 = false;
    i++;
    continue;
  }

  // ## Section headers — 12pt bold, ALL CAPS, accent color, bottom border
  if (/^## /.test(line)) {
    const header = line.replace(/^## /, "").toUpperCase();
    children.push(
      new Paragraph({
        spacing: { before: 200, after: 80, line: 240 },
        border: {
          bottom: {
            style: BorderStyle.SINGLE,
            size: 2,
            color: ACCENT_COLOR,
          },
        },
        children: [
          makeRun(header, { size: 12, bold: true, color: ACCENT_COLOR }),
        ],
      })
    );
    i++;
    continue;
  }

  // ### Company | Location | Dates — 11pt bold, dates right-aligned
  if (/^### /.test(line)) {
    const content = line.replace(/^### /, "");
    const parts = content.split("|").map((s) => s.trim());
    const company = parts[0] || "";
    const location = parts.length > 1 ? parts[1] : "";
    const dates = parts.length > 2 ? parts[2] : "";
    const leftText = location ? `${company} | ${location}` : company;

    children.push(
      new Paragraph({
        spacing: { before: 120, after: 20, line: 240 },
        tabStops: [
          {
            type: TabStopType.RIGHT,
            position: USABLE,
          },
        ],
        children: [
          makeRun(leftText, { size: 11, bold: true }),
          new TextRun({
            text: "\t",
            font: { name: FONT, fallback: FONT_FALLBACK },
          }),
          makeRun(dates, { size: 11, bold: true }),
        ],
      })
    );
    i++;
    continue;
  }

  // **Job Title** lines — 10.5pt bold italic
  if (/^\*\*(.+)\*\*$/.test(line)) {
    const title = line.replace(/^\*\*/, "").replace(/\*\*$/, "");
    children.push(
      new Paragraph({
        spacing: { after: 20, line: 240 },
        children: [makeRun(title, { size: 10.5, bold: true, italics: true })],
      })
    );
    i++;
    continue;
  }

  // Bullet points
  if (/^- /.test(line)) {
    const text = line.replace(/^- /, "");
    const runs = parseBoldSegments(text, 10.5);
    children.push(
      new Paragraph({
        spacing: { after: 40, line: 240 },
        numbering: { reference: "bullets", level: 0 },
        children: runs,
      })
    );
    i++;
    continue;
  }

  // Contact line (first pipe-separated line after name) — 10pt centered, accent bottom border
  if (line.includes("|") && !line.startsWith("#") && isFirstPipeLine) {
    isFirstPipeLine = false;
    children.push(
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 0, line: 240 },
        border: {
          bottom: {
            style: BorderStyle.SINGLE,
            size: 2,
            color: ACCENT_COLOR,
          },
        },
        children: [makeRun(line, { size: 10 })],
      })
    );
    i++;
    continue;
  }

  // Headline line (pipe-separated, after contact) — 11pt italic centered
  if (line.includes("|") && !line.startsWith("#")) {
    children.push(
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 40, line: 240 },
        children: [makeRun(line, { size: 11, italics: true })],
      })
    );
    i++;
    continue;
  }

  // Default: body text with bold parsing
  const runs = parseBoldSegments(line, 10.5);
  children.push(
    new Paragraph({
      spacing: { after: 40, line: 240 },
      children: runs,
    })
  );
  i++;
}

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "\u2022",
            alignment: AlignmentType.LEFT,
            style: {
              paragraph: {
                indent: {
                  left: convertInchesToTwip(0.25),
                  hanging: convertInchesToTwip(0.25),
                },
              },
              run: {
                font: { name: FONT, fallback: FONT_FALLBACK },
              },
            },
          },
        ],
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: {
            width: 12240,
            height: 15840,
          },
          margin: {
            top: MARGIN,
            bottom: MARGIN,
            left: MARGIN,
            right: MARGIN,
          },
        },
      },
      children,
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outputPath, buffer);
  console.log("Resume DOCX written to:", outputPath);
  console.log("Size:", buffer.length, "bytes");
});
