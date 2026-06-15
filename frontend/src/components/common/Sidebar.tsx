interface Props {
  recentChats: string[];
  mood: string | null;
  topic: string | null;
  canExport: boolean;
  isExporting: boolean;
  onNewChat: () => void;
  onExportPdf: () => void;
  activeTab: "chat" | "resources" | "appointments" | "auth";
  onTabChange: (tab: "chat" | "resources" | "appointments" | "auth") => void;
  user: { username: string; email: string; role: string } | null;
  onLogout: () => void;
}

export default function Sidebar({
  recentChats,
  mood,
  topic,
  canExport,
  isExporting,
  onNewChat,
  onExportPdf,
  activeTab,
  onTabChange,
  user,
  onLogout,
}: Props) {
  return (
    <aside className="sidebar">
      <div className="brand-row" onClick={() => onTabChange("chat")} style={{ cursor: "pointer" }}>
        <span className="brand-mark">🧠</span>
        <span>Patronus AI</span>
      </div>

      <nav className="sidebar-nav" style={{ display: "flex", flexDirection: "column", gap: "6px", margin: "10px 0" }}>
        <button
          className={`recent-btn ${activeTab === "chat" ? "is-selected" : ""}`}
          style={{
            background: activeTab === "chat" ? "var(--pat-accent-soft)" : "transparent",
            color: activeTab === "chat" ? "var(--pat-accent-text)" : "var(--pat-text)",
            fontWeight: activeTab === "chat" ? "700" : "500",
            border: activeTab === "chat" ? "1px solid var(--pat-accent)" : "1px solid transparent",
            borderRadius: "8px",
            minHeight: "3.2rem",
            justifyContent: "flex-start",
            paddingLeft: "0.9rem",
            width: "100%",
            textAlign: "left",
            cursor: "pointer",
          }}
          onClick={() => onTabChange("chat")}
        >
          💬 empathetic Chat
        </button>

        <button
          className={`recent-btn ${activeTab === "resources" ? "is-selected" : ""}`}
          style={{
            background: activeTab === "resources" ? "var(--pat-accent-soft)" : "transparent",
            color: activeTab === "resources" ? "var(--pat-accent-text)" : "var(--pat-text)",
            fontWeight: activeTab === "resources" ? "700" : "500",
            border: activeTab === "resources" ? "1px solid var(--pat-accent)" : "1px solid transparent",
            borderRadius: "8px",
            minHeight: "3.2rem",
            justifyContent: "flex-start",
            paddingLeft: "0.9rem",
            width: "100%",
            textAlign: "left",
            cursor: "pointer",
          }}
          onClick={() => onTabChange("resources")}
        >
          📚 Wellness Library
        </button>

        <button
          className={`recent-btn ${activeTab === "appointments" ? "is-selected" : ""}`}
          style={{
            background: activeTab === "appointments" ? "var(--pat-accent-soft)" : "transparent",
            color: activeTab === "appointments" ? "var(--pat-accent-text)" : "var(--pat-text)",
            fontWeight: activeTab === "appointments" ? "700" : "500",
            border: activeTab === "appointments" ? "1px solid var(--pat-accent)" : "1px solid transparent",
            borderRadius: "8px",
            minHeight: "3.2rem",
            justifyContent: "flex-start",
            paddingLeft: "0.9rem",
            width: "100%",
            textAlign: "left",
            cursor: "pointer",
          }}
          onClick={() => onTabChange("appointments")}
        >
          🗓️ Book Appointment
        </button>

        <button
          className={`recent-btn ${activeTab === "auth" ? "is-selected" : ""}`}
          style={{
            background: activeTab === "auth" ? "var(--pat-accent-soft)" : "transparent",
            color: activeTab === "auth" ? "var(--pat-accent-text)" : "var(--pat-text)",
            fontWeight: activeTab === "auth" ? "700" : "500",
            border: activeTab === "auth" ? "1px solid var(--pat-accent)" : "1px solid transparent",
            borderRadius: "8px",
            minHeight: "3.2rem",
            justifyContent: "flex-start",
            paddingLeft: "0.9rem",
            width: "100%",
            textAlign: "left",
            cursor: "pointer",
          }}
          onClick={() => onTabChange("auth")}
        >
          👤 {user ? `${user.username} (${user.role})` : "Login / Register"}
        </button>
      </nav>

      {activeTab === "chat" && (
        <>
          <button className="new-chat-btn" onClick={onNewChat} style={{ width: "100%" }}>
            + New Chat
          </button>

          <div className="sidebar-label" style={{ marginTop: "1rem" }}>Recent Chats</div>
          {recentChats.map((chat, i) => (
            <button className="recent-btn" key={i} title={chat} style={{ width: "100%", textAlign: "left" }}>
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
              <button className="export-btn" onClick={onExportPdf} disabled={isExporting} style={{ width: "100%" }}>
                {isExporting ? "Preparing PDF..." : "Export Chat to PDF"}
              </button>
            </>
          )}
        </>
      )}

      {user && (
        <div style={{ marginTop: "auto", paddingTop: "20px" }}>
          <button
            onClick={onLogout}
            style={{
              width: "100%",
              minHeight: "2.6rem",
              background: "#ff4d4f",
              color: "white",
              border: "none",
              borderRadius: "8px",
              fontWeight: "bold",
              cursor: "pointer",
            }}
          >
            Logout
          </button>
        </div>
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
