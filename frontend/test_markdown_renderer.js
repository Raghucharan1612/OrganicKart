import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MarkdownRenderer, { renderInlineMarkdown } from "./src/components/ai/MarkdownRenderer.js";

const h = React.createElement;

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (!condition) {
    console.error(`❌ FAILED: ${message}`);
    failed++;
    throw new Error(message);
  } else {
    console.log(`✅ PASSED: ${message}`);
    passed++;
  }
}

console.log("==================================================");
console.log("RUNNING MARKDOWN RENDERER REGRESSION TESTS");
console.log("==================================================");

// Test 1: Literal <br> in tables is normalized into HTML line breaks
const tableWithBrs = `
| Order ID | Items | Status |
|---|---|---|
| #101 | 1x Organic Apples<br>2x Farm Eggs | Confirmed<br />Paid |
| #102 | 1x Whole Milk</br>1x Butter | Delivered |
`;

const tableHtml = renderToStaticMarkup(h(MarkdownRenderer, { content: tableWithBrs }));
assert(tableHtml.includes("<table"), "Table HTML should contain <table> element");
assert(tableHtml.includes("<th"), "Table HTML should contain <th> elements");
assert(tableHtml.includes("1x Organic Apples<br/>2x Farm Eggs"), "Table cell <br> should be normalized to <br/> element");
assert(tableHtml.includes("Confirmed<br/>Paid"), "Table cell <br /> should be normalized to <br/> element");
assert(tableHtml.includes("1x Whole Milk<br/>1x Butter"), "Table cell </br> should be normalized to <br/> element");
assert(!tableHtml.includes("&lt;br&gt;"), "Table HTML should not render literal &lt;br&gt; text");
assert(!tableHtml.includes("&lt;br/&gt;"), "Table HTML should not render literal &lt;br/&gt; text");

// Test 2: Literal <br> in lists is normalized into HTML line breaks
const listWithBrs = `
- Item 1: Organic Honey<br>Produced locally in Coorg
- Item 2: Fresh Tomatoes<br />Harvested yesterday
* Item 3: A2 Desi Ghee</br>Pure & grass-fed
`;

const listHtml = renderToStaticMarkup(h(MarkdownRenderer, { content: listWithBrs }));
assert(listHtml.includes("<ul"), "List HTML should contain <ul> element");
assert(listHtml.includes("<li"), "List HTML should contain <li> elements");
assert(listHtml.includes("Item 1: Organic Honey<br/>Produced locally in Coorg"), "List item <br> should be normalized to <br/>");
assert(listHtml.includes("Item 2: Fresh Tomatoes<br/>Harvested yesterday"), "List item <br /> should be normalized to <br/>");
assert(listHtml.includes("Item 3: A2 Desi Ghee<br/>Pure"), "List item </br> should be normalized to <br/>");

// Test 3: Code block preserves <br> and raw formatting verbatim
const codeBlockContent = `
Here is some code:
\`\`\`html
<div>
  <span>Line 1</span><br>
  <span>Line 2</span>
</div>
\`\`\`
`;

const codeHtml = renderToStaticMarkup(h(MarkdownRenderer, { content: codeBlockContent }));
assert(codeHtml.includes("<pre"), "Code block should contain <pre> element");
assert(codeHtml.includes("<code"), "Code block should contain <code> element");
assert(codeHtml.includes("&lt;span&gt;Line 1&lt;/span&gt;&lt;br&gt;"), "Code block must preserve literal <br> as escaped code text, NOT execute as <br/> element");
assert(!codeHtml.includes("Line 1</span><br>"), "Code block must not execute raw html tags");

// Test 4: Inline code preserves `<br>` verbatim
const inlineCodeContent = "To insert a break in HTML, use the `<br>` tag or `<br/>`.";
const inlineCodeHtml = renderToStaticMarkup(h(MarkdownRenderer, { content: inlineCodeContent }));
assert(inlineCodeHtml.includes("<code"), "Inline code should contain <code> element");
assert(inlineCodeHtml.includes("&lt;br&gt;"), "Inline code must preserve literal <br> inside code element");
assert(!inlineCodeHtml.includes("use the <br/> tag"), "Inline code must not convert <br> to an actual break");

// Test 5: Raw HTML execution prevention (XSS protection)
const maliciousContent = "Hello <script>alert('xss')</script> <img src=x onerror=alert(1)> normal text.";
const maliciousHtml = renderToStaticMarkup(h(MarkdownRenderer, { content: maliciousContent }));
assert(!maliciousHtml.includes("<script>"), "Raw <script> tag must not be injected into DOM");
assert(!maliciousHtml.includes("<img"), "Raw <img> tag must not be injected into DOM");
assert(maliciousHtml.includes("&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"), "Script tag should be safely string-escaped");
assert(maliciousHtml.includes("&lt;img src=x onerror=alert(1)&gt;"), "Img tag should be safely string-escaped");

// Test 6: Headings and Paragraphs
const generalMarkdown = `
# Organic Order Status
Your order #55 has been dispatched.
Tracking details are below.

## Details
- Status: Dispatched<br>In Transit
`;
const genHtml = renderToStaticMarkup(h(MarkdownRenderer, { content: generalMarkdown }));
assert(genHtml.includes("<h1"), "Should render <h1> for #");
assert(genHtml.includes("<h2"), "Should render <h2> for ##");
assert(genHtml.includes("Your order #55 has been dispatched.<br/>Tracking details are below."), "Paragraph with newline should render line break");

console.log("==================================================");
console.log(`TOTAL: ${passed} passed, ${failed} failed.`);
console.log("==================================================");

if (failed > 0) {
  process.exit(1);
}
