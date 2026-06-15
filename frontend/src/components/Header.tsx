interface Props {
  darkMode: boolean;
  onToggleDark: () => void;
}

export default function Header({ darkMode, onToggleDark }: Props) {
  return (
    <div className="header-row">
      <div className="welcome-header">
        <h1>Welcome Back 👋</h1>
        <p>Your safe space to talk and reflect.</p>
      </div>
      <div className="theme-toggle-wrap">
        <button
          className="theme-toggle"
          onClick={onToggleDark}
          aria-label="Toggle dark mode"
          title="Toggle dark mode"
        >
          {darkMode ? "☀️" : "🌙"}
        </button>
        <span className="theme-hint">Theme</span>
      </div>
    </div>
  );
}
