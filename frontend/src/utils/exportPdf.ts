import { jsPDF } from "jspdf";
import type { ChatMessage } from "../types";

// Mirrors main.py's remove_emojis().
const EMOJI_REGEX =
  /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2500}-\u{2BEF}\u{2702}-\u{27B0}\u{24C2}-\u{1F251}\u{1F926}-\u{1F937}\u{10000}-\u{10FFFF}\u{2640}-\u{2642}\u{2600}-\u{2B55}\u{200D}\u{23CF}\u{23E9}\u{231A}\u{FE0F}\u{3030}]/gu;

export function removeEmojis(text: string): string {
  return text.replace(EMOJI_REGEX, "");
}

function timestamp(): string {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return (
    `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_` +
    `${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`
  );
}

/**
 * Builds a simple PDF transcript of the conversation and triggers a download.
 * Ports the structure of export_chat_pdf() in app.py.
 */
export function exportChatToPdf(messages: ChatMessage[]): void {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 15;
  const maxWidth = pageWidth - margin * 2;
  let y = 20;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.text("Patronus AI - Conversation History", pageWidth / 2, y, { align: "center" });
  y += 8;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(11);
  doc.text(`Date: ${new Date().toLocaleString()}`, pageWidth / 2, y, { align: "center" });
  y += 12;

  const ensureSpace = (lineHeight: number) => {
    if (y + lineHeight > pageHeight - margin) {
      doc.addPage();
      y = 20;
    }
  };

  for (const msg of messages) {
    ensureSpace(8);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(10);
    doc.text(msg.role === "user" ? "User" : "Assistant", margin, y);
    y += 7;

    doc.setFont("helvetica", "normal");
    const lines = doc.splitTextToSize(removeEmojis(msg.content), maxWidth);
    for (const line of lines) {
      ensureSpace(6);
      doc.text(line, margin, y);
      y += 6;
    }
    y += 3;
  }

  doc.save(`patronus_chat_${timestamp()}.pdf`);
}
