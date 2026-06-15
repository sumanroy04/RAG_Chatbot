interface Props {
  recentChats: string[];
  mood: string | null;
  topic: string | null;
  canExport: boolean;
  isExporting: boolean;
  onNewChat: () => void;
  onExportPdf: () => void;
}

export default function Sidebar({
  recentChats,
  mood,
  topic,
  canExport,
  isExporting,
  onNewChat,
  onExportPdf,
}: Props) {
  return (
    <aside className="sidebar">
      <div className="brand-row">
        <span className="brand-mark">🧠</span>
        <span>Patronus AI</span>
      </div>

      <button className="new-chat-btn" onClick={onNewChat}>
        + New Chat
      </button>

      <div className="sidebar-label">Recent Chats</div>
      {recentChats.map((chat, i) => (
        <button className="recent-btn" key={i} title={chat}>
          {chat.length > 28 ? `${chat.slice(0, 28)}...` : chat}
        </button>
      ))}

      <hr className="sb-divider" />

      <div className="status-card">
        <strong>Current Focus</strong>
        <p>
          Mood: {mood || "Not selected"}
          <br />
          Topic: {topic || "Open chat"}
        </p>
      </div>

      {canExport && (
        <>
          <hr className="sb-divider" />
          <button className="export-btn" onClick={onExportPdf} disabled={isExporting}>
            {isExporting ? "Preparing PDF..." : "Export Chat to PDF"}
          </button>
        </>
      )}

      <hr className="sb-divider" />

      <div className="about-card">
        <strong>About</strong>
        <p>
          AI-powered mental wellness assistant designed to provide empathetic support and
          guidance.
        </p>
      </div>
    </aside>
  );
}
