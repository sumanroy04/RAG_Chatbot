function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/** Converts **bold** markers into <strong> tags. Input must already be escaped. */
function inlineFormat(text: string): string {
  return text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}

/**
 * Turns plain-text LLM output into simple HTML: paragraphs, <br> for blank
 * lines, "- "/"* "/"• " bullets become <ul><li>, and **bold** becomes
 * <strong>. Mirrors render_message_text() in app.py.
 */
export function formatMessageHtml(text: string): string {
  const escaped = escapeHtml(text ?? "");
  const rawLines = escaped.split(/\r?\n/);
  const lines = rawLines.length ? rawLines : [""];

  const parts: string[] = [];
  let inList = false;

  for (const raw of lines) {
    const line = raw.trim();
    const isBullet = line.startsWith("- ") || line.startsWith("* ") || line.startsWith("• ");

    if (isBullet) {
      if (!inList) {
        parts.push("<ul>");
        inList = true;
      }
      parts.push(`<li>${inlineFormat(line.slice(2).trim())}</li>`);
      continue;
    }

    if (inList) {
      parts.push("</ul>");
      inList = false;
    }

    if (!line) {
      parts.push("<br>");
    } else {
      parts.push(`<p>${inlineFormat(line)}</p>`);
    }
  }

  if (inList) parts.push("</ul>");

  return parts.join("");
}
