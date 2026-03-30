#!/usr/bin/env node

/**
 * Standalone cover letter DOCX generator.
 * Converts a markdown cover letter into an ATS-friendly DOCX.
 *
 * Usage: node generate_cover_letter_docx.js <input.md> <output.docx> [options]
 *
 * Options (as JSON string in argv[4]):
 *   accentColor, font, fontFallback, margins, userName, company, role
 */

const fs = require("fs");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  AlignmentType,
  convertInchesToTwip,
  BorderStyle,
} = require("docx");

const inputPath = process.argv[2];
const outputPath = process.argv[3];
const optionsJson = process.argv[4] || "{}";

if (!inputPath || !outputPath) {
  console.error(
    "Usage: node generate_cover_letter_docx.js <input.md> <output.docx> [optionsJson]"
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
const MARGIN_INCHES = options.margins || 1.0;
const USER_NAME = options.userName || "Your Name";
const ROLE = options.role || "Role Title";

const MARGIN = convertInchesToTwip(MARGIN_INCHES);

const src = fs.readFileSync(inputPath, "utf-8");
const lines = src.split("\n");

const children = [];

function makeRun(text, opts = {}) {
  return new TextRun({
    text,
    font: { name: FONT, fallback: FONT_FALLBACK },
    size: (opts.size || 11) * 2, // half-points
    bold: opts.bold || false,
    color: opts.color || "000000",
  });
}

// Parse the markdown
// Expected structure:
//   # Name
//   contact | info | line
//   ---
//   body paragraphs...

let i = 0;
let contactLine = null;
let bodyParagraphs = [];
let foundHR = false;
let foundName = false;

while (i < lines.length) {
  const line = lines[i].trim();

  // # Name
  if (/^# /.test(line) && !foundName) {
    foundName = true;
    i++;
    continue;
  }

  // Horizontal rule
  if (/^---+$/.test(line)) {
    foundHR = true;
    i++;
    continue;
  }

  // Contact line (pipe-separated, before HR)
  if (!foundHR && line.includes("|") && !line.startsWith("#")) {
    contactLine = line;
    i++;
    continue;
  }

  // Skip empty lines
  if (line === "") {
    i++;
    continue;
  }

  // Everything after HR is body
  if (foundHR && line !== "") {
    bodyParagraphs.push(line);
  }

  i++;
}

// --- Build DOCX paragraphs ---

// 1. Name: 18pt bold, centered, accent color
children.push(
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 0, line: 276 }, // 1.15 line spacing = 276 twips
    children: [makeRun(USER_NAME, { size: 18, bold: true, color: ACCENT_COLOR })],
  })
);

// 2. Contact line: 10pt regular, centered, black, pipe-separated
if (contactLine) {
  children.push(
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 0, line: 276 },
      border: {
        bottom: {
          style: BorderStyle.SINGLE,
          size: 2, // 1pt
          color: ACCENT_COLOR,
        },
      },
      children: [makeRun(contactLine, { size: 10 })],
    })
  );
}

// 3. Spacer after rule
children.push(
  new Paragraph({
    spacing: { after: 120, line: 276 },
    children: [],
  })
);

// 4. Re: line - 11pt bold, left-aligned, 12pt space after
children.push(
  new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { after: 240, line: 276 }, // 12pt = 240 twips
    children: [makeRun(`Re: ${ROLE}`, { size: 11, bold: true })],
  })
);

// 5. Greeting
children.push(
  new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { after: 200, line: 276 }, // 10pt
    children: [makeRun("Dear Hiring Manager,", { size: 11 })],
  })
);

// 6. Body paragraphs: 11pt regular, 10pt after each
for (const para of bodyParagraphs) {
  children.push(
    new Paragraph({
      alignment: AlignmentType.LEFT,
      spacing: { after: 200, line: 276 }, // 10pt = 200 twips
      children: [makeRun(para, { size: 11 })],
    })
  );
}

// 7. Closing: "Sincerely," with 18pt space above
children.push(
  new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { before: 360, after: 200, line: 276 }, // 18pt = 360 twips
    children: [makeRun("Sincerely,", { size: 11 })],
  })
);

// 8. Signature: bold
children.push(
  new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { after: 0, line: 276 },
    children: [makeRun(USER_NAME, { size: 11, bold: true })],
  })
);

// Build document
const doc = new Document({
  sections: [
    {
      properties: {
        page: {
          size: {
            width: 12240, // US Letter
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
  console.log("Cover letter DOCX written to:", outputPath);
  console.log("Size:", buffer.length, "bytes");
});
