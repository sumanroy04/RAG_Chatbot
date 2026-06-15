const HOTLINES: { name: string; detail: string; alt?: boolean }[] = [
  { name: "Tele-MANAS", detail: "14416 | 24/7" },
  { name: "KIRAN", detail: "1800-599-0019 | 24/7", alt: true },
  { name: "Vandrevala", detail: "9999 666 555 | 24/7" },
  { name: "iCALL", detail: "9152987821 | Mon-Sat, 10 AM-8 PM", alt: true },
];

/**
 * Ports crisis.py's get_crisis_html_card to JSX. Styling for both light and
 * dark mode lives in global.css under `.crisis-card`.
 */
export default function CrisisCard() {
  return (
    <div className="crisis-card">
      <div className="crisis-title">🆘 Crisis Support Resources</div>
      <p>
        You are <strong>not alone</strong>, and help is available.
      </p>
      <p className="crisis-emergency">
        🚨 In immediate danger? Call <span>112</span>
      </p>
      <table>
        <tbody>
          {HOTLINES.map((line) => (
            <tr key={line.name} className={line.alt ? "crisis-row-alt" : undefined}>
              <td className="crisis-name">{line.name}</td>
              <td className="crisis-detail">{line.detail}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
