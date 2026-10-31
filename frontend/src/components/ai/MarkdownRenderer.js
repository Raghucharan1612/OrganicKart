import React from "react";

const h = React.createElement;

/**
 * Safely parse inline Markdown text into React elements:
 * - Preserves code inside backticks `...` verbatim (literal <br> inside code is preserved)
 * - Replaces <br>, </br>, <br/>, <br /> (case-insensitive) with <br /> elements
 * - Handles **bold** or __bold__
 * - Handles *italic*
 * - Handles [links](url) safely (validating http/https)
 * - Escapes and prevents execution of any other raw HTML
 *
 * @param {string} text
 * @returns {React.ReactNode[]}
 */
export function renderInlineMarkdown(text) {
  if (!text) return null;

  const tokens = [];
  let remaining = text;
  let keyIndex = 0;

  // Regex matches:
  // - `code` (group 1)
  // - </?br\s*/?> (group 2)
  // - **bold** (group 3)
  // - *italic* (group 4)
  // - [text](url) (group 5: text, group 6: url)
  const inlineRegex = /(?:`([^`]+)`)|(?:(<\/?br\s*\/?>))|(?:\*\*([^*]+)\*\*)|(?:\*([^*]+)\*)|(?:\[([^\]]+)\]\((https?:\/\/[^\s)]+)\))/i;

  while (remaining.length > 0) {
    const match = inlineRegex.exec(remaining);
    if (!match) {
      tokens.push(remaining);
      break;
    }

    const matchIndex = match.index;
    if (matchIndex > 0) {
      tokens.push(remaining.substring(0, matchIndex));
    }

    if (match[1] !== undefined) {
      // inline code: preserve verbatim (including any <br> text inside)
      tokens.push(
        h(
          "code",
          {
            key: `code-${keyIndex++}`,
            className: "rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[12px] text-slate-800",
          },
          match[1]
        )
      );
    } else if (match[2] !== undefined) {
      // <br> variant: normalize to visual line break
      tokens.push(h("br", { key: `br-${keyIndex++}` }));
    } else if (match[3] !== undefined) {
      // bold
      tokens.push(
        h(
          "strong",
          {
            key: `bold-${keyIndex++}`,
            className: "font-semibold text-slate-900",
          },
          renderInlineMarkdown(match[3])
        )
      );
    } else if (match[4] !== undefined) {
      // italic
      tokens.push(
        h(
          "em",
          {
            key: `italic-${keyIndex++}`,
            className: "italic",
          },
          renderInlineMarkdown(match[4])
        )
      );
    } else if (match[5] !== undefined && match[6] !== undefined) {
      // safe link
      tokens.push(
        h(
          "a",
          {
            key: `link-${keyIndex++}`,
            href: match[6],
            target: "_blank",
            rel: "noopener noreferrer",
            className: "text-primary-700 underline hover:text-primary-800",
          },
          match[5]
        )
      );
    }

    remaining = remaining.substring(matchIndex + match[0].length);
  }

  return tokens;
}

/**
 * Check if a trimmed line is a markdown table row (starts and ends with '|')
 */
function isTableRow(line) {
  const trimmed = line.trim();
  return trimmed.startsWith("|") && trimmed.endsWith("|") && trimmed.length > 1;
}

/**
 * Check if a table row is an alignment delimiter row (e.g. |---|:---:|---:|)
 */
function isTableDelimiter(line) {
  if (!isTableRow(line)) return false;
  const cells = line
    .trim()
    .slice(1, -1)
    .split("|")
    .map((c) => c.trim());
  return cells.length > 0 && cells.every((c) => /^:?-+:?$/.test(c));
}

/**
 * Parse Markdown blocks:
 * - Fenced code blocks (``` ... ```)
 * - Markdown tables (| header | header | ... |---|... | cell | cell |)
 * - Headings (#, ##, ###)
 * - Unordered lists (- item, * item, • item)
 * - Ordered lists (1. item)
 * - Paragraphs with natural line breaks
 *
 * @param {object} props
 * @param {string} props.content
 * @param {string} [props.className]
 * @returns {React.ReactNode}
 */
export default function MarkdownRenderer({ content, className = "" }) {
  if (!content) return null;

  const lines = content.split("\n");
  const blocks = [];
  let i = 0;
  let blockKey = 0;

  while (i < lines.length) {
    const line = lines[i];

    // 1. Fenced Code Block
    if (line.trim().startsWith("```")) {
      const lang = line.trim().slice(3).trim();
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      if (i < lines.length) i++; // consume closing ```
      blocks.push(
        h(
          "div",
          {
            key: `codeblock-${blockKey++}`,
            className: "my-2 overflow-x-auto rounded-lg bg-slate-900 p-3 text-slate-100",
          },
          lang ? h("div", { className: "mb-1 text-[10px] uppercase tracking-wider text-slate-400" }, lang) : null,
          h("pre", { className: "font-mono text-xs leading-normal" }, h("code", null, codeLines.join("\n")))
        )
      );
      continue;
    }

    // 2. Markdown Table
    if (isTableRow(line) && i + 1 < lines.length && isTableDelimiter(lines[i + 1])) {
      const headerCells = line
        .trim()
        .slice(1, -1)
        .split("|")
        .map((c) => c.trim());
      i += 2; // skip header and delimiter

      const bodyRows = [];
      while (i < lines.length && isTableRow(lines[i])) {
        const cells = lines[i]
          .trim()
          .slice(1, -1)
          .split("|")
          .map((c) => c.trim());
        while (cells.length < headerCells.length) {
          cells.push("");
        }
        bodyRows.push(cells);
        i++;
      }

      blocks.push(
        h(
          "div",
          {
            key: `table-${blockKey++}`,
            className: "my-2.5 overflow-x-auto rounded-lg border border-slate-200",
          },
          h(
            "table",
            { className: "min-w-full divide-y divide-slate-200 text-left text-xs" },
            h(
              "thead",
              { className: "bg-slate-50 font-semibold text-slate-700" },
              h(
                "tr",
                null,
                headerCells.map((header, idx) =>
                  h("th", { key: `th-${idx}`, className: "px-3 py-2" }, renderInlineMarkdown(header))
                )
              )
            ),
            h(
              "tbody",
              { className: "divide-y divide-slate-100 bg-white text-slate-800" },
              bodyRows.map((row, rIdx) =>
                h(
                  "tr",
                  { key: `tr-${rIdx}`, className: rIdx % 2 === 1 ? "bg-slate-50/50" : "" },
                  row.map((cell, cIdx) =>
                    h("td", { key: `td-${rIdx}-${cIdx}`, className: "px-3 py-2 align-top" }, renderInlineMarkdown(cell))
                  )
                )
              )
            )
          )
        )
      );
      continue;
    }

    // 3. Headings (#, ##, ###)
    const headingMatch = line.match(/^(#{1,3})\s+(.+)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const text = headingMatch[2];
      const tag = level === 1 ? "h1" : level === 2 ? "h2" : "h3";
      const headingClass =
        level === 1
          ? "mt-3 mb-1.5 text-base font-bold text-slate-900"
          : level === 2
          ? "mt-2.5 mb-1 text-sm font-bold text-slate-900"
          : "mt-2 mb-1 text-sm font-semibold text-slate-800";

      blocks.push(
        h(tag, { key: `h-${blockKey++}`, className: headingClass }, renderInlineMarkdown(text))
      );
      i++;
      continue;
    }

    // 4. Unordered Lists (- , * , • )
    const bulletMatch = line.match(/^(\s*)[-*•]\s+(.+)$/);
    if (bulletMatch) {
      const listItems = [];
      while (i < lines.length) {
        const itemMatch = lines[i].match(/^(\s*)[-*•]\s+(.+)$/);
        if (!itemMatch) break;
        listItems.push(itemMatch[2]);
        i++;
      }
      blocks.push(
        h(
          "ul",
          {
            key: `ul-${blockKey++}`,
            className: "my-1.5 space-y-1 pl-4 list-disc marker:text-emerald-600",
          },
          listItems.map((item, idx) =>
            h("li", { key: `li-${idx}`, className: "text-xs leading-relaxed" }, renderInlineMarkdown(item))
          )
        )
      );
      continue;
    }

    // 5. Ordered Lists (1. )
    const orderedMatch = line.match(/^(\s*)\d+\.\s+(.+)$/);
    if (orderedMatch) {
      const listItems = [];
      while (i < lines.length) {
        const itemMatch = lines[i].match(/^(\s*)\d+\.\s+(.+)$/);
        if (!itemMatch) break;
        listItems.push(itemMatch[2]);
        i++;
      }
      blocks.push(
        h(
          "ol",
          {
            key: `ol-${blockKey++}`,
            className: "my-1.5 space-y-1 pl-4 list-decimal marker:text-emerald-700",
          },
          listItems.map((item, idx) =>
            h("li", { key: `oli-${idx}`, className: "text-xs leading-relaxed" }, renderInlineMarkdown(item))
          )
        )
      );
      continue;
    }

    // 6. Blank line
    if (!line.trim()) {
      i++;
      continue;
    }

    // 7. Regular paragraph (accumulate consecutive text lines)
    const paraLines = [];
    while (
      i < lines.length &&
      lines[i].trim() &&
      !lines[i].trim().startsWith("```") &&
      !(isTableRow(lines[i]) && i + 1 < lines.length && isTableDelimiter(lines[i + 1])) &&
      !lines[i].match(/^#{1,3}\s+/) &&
      !lines[i].match(/^(\s*)[-*•]\s+/) &&
      !lines[i].match(/^(\s*)\d+\.\s+/)
    ) {
      paraLines.push(lines[i]);
      i++;
    }

    if (paraLines.length > 0) {
      const paraChildren = [];
      paraLines.forEach((pLine, idx) => {
        if (idx > 0) {
          paraChildren.push(h("br", { key: `pbr-${idx}` }));
        }
        paraChildren.push(renderInlineMarkdown(pLine));
      });
      blocks.push(
        h(
          "p",
          {
            key: `p-${blockKey++}`,
            className: "my-1 leading-relaxed",
          },
          paraChildren
        )
      );
    }
  }

  return h("div", { className: `space-y-1 text-xs sm:text-sm ${className}` }, blocks);
}
