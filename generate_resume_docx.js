#!/usr/bin/env node

/**
 * Standalone resume DOCX generator.
 * Converts a markdown resume (using the project's formatting conventions) into an ATS-friendly DOCX.
 *
 * Usage: node generate_resume_docx.js <input.md> <output.docx>
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

if (!inputPath || !outputPath) {
  console.error("Usage: node generate_resume_docx.js <input.md> <output.docx>");
  console.error("Example: node generate_resume_docx.js ./resume.md ./resume.docx");
  process.exit(1);
}

if (!fs.existsSync(inputPath)) {
  console.error(`Error: Input file not found: ${inputPath}`);
  process.exit(1);
}

const src = fs.readFileSync(inputPath, "utf-8");
const lines = src.split("\n");

// Page width in twips: 12240 total, minus 2 * 0.7" margins = 12240 - 2016 = 10224 usable
const PAGE_WIDTH_TWIP = 12240;
const MARGIN = convertInchesToTwip(0.7);
const USABLE = PAGE_WIDTH_TWIP - 2 * MARGIN;

const FONT = "Calibri";
const SPACING = { after: 40, line: 240 }; // 2pt after, single line spacing (240 = single)

const children = [];

function makeRun(text, opts = {}) {
  return new TextRun({
    text,
    font: FONT,
    size: (opts.size || 10.5) * 2, // half-points
    bold: opts.bold || false,
    italics: opts.italics || false,
  });
}

function parseBoldSegments(text, baseSize) {
  // Parse **bold** segments mixed with regular text
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

  // # Name (H1)
  if (/^# /.test(line)) {
    const name = line.replace(/^# /, "");
    children.push(
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 40, line: 240 },
        children: [makeRun(name, { size: 16, bold: true })],
      })
    );
    i++;
    continue;
  }

  // ## Section headers
  if (/^## /.test(line)) {
    const header = line.replace(/^## /, "").toUpperCase();
    children.push(
      new Paragraph({
        spacing: { before: 120, after: 40, line: 240 },
        border: {
          bottom: {
            style: BorderStyle.SINGLE,
            size: 1, // 0.5pt = 1 half-pt
            color: "999999",
          },
        },
        children: [makeRun(header, { size: 12, bold: true })],
      })
    );
    i++;
    continue;
  }

  // ### Company | Location | Dates
  if (/^### /.test(line)) {
    const content = line.replace(/^### /, "");
    const parts = content.split("|").map((s) => s.trim());
    const company = parts[0] || "";
    const location = parts.length > 1 ? parts[1] : "";
    const dates = parts.length > 2 ? parts[2] : "";
    const leftText = location ? `${company} | ${location}` : company;

    children.push(
      new Paragraph({
        spacing: { after: 20, line: 240 },
        tabStops: [
          {
            type: TabStopType.RIGHT,
            position: USABLE,
          },
        ],
        children: [
          makeRun(leftText, { size: 11, bold: true }),
          new TextRun({ text: "\t", font: FONT }),
          makeRun(dates, { size: 11, bold: true }),
        ],
      })
    );
    i++;
    continue;
  }

  // **Job Title** lines (bold italic)
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

  // Contact line (pipes, no heading prefix)
  if (line.includes("|") && !line.startsWith("#")) {
    children.push(
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 40, line: 240 },
        children: [makeRun(line, { size: 10.5 })],
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
                font: FONT,
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
  console.log("DOCX written to:", outputPath);
  console.log("Size:", buffer.length, "bytes");
});