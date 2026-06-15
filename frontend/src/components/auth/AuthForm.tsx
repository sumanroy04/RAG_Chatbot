import { useState } from "react";

interface Props {
  onAuthSuccess: (user: { username: string; email: string; role: string }, token: string) => void;
  apiBaseUrl: string;
}

export default function AuthForm({ onAuthSuccess, apiBaseUrl }: Props) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("user");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const endpoint = isRegister ? "/api/auth/register" : "/api/auth/login";
    const payload = isRegister 
      ? { username, email, password, role }
      : { email, password };

    try {
      const response = await fetch(`${apiBaseUrl}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = (await response.json()) as {
        detail?: string;
        message?: string;
        access_token?: string;
        username?: string;
        email?: string;
        role?: string;
      };

      if (!response.ok) {
        throw new Error(data.detail || "Authentication failed.");
      }

      if (data.access_token && data.username && data.email && data.role) {
        onAuthSuccess(
          { username: data.username, email: data.email, role: data.role },
          data.access_token
        );
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-shell" style={{ maxWidth: "450px", margin: "40px auto", padding: "30px" }}>
      <h2 style={{ textAlign: "center", marginBottom: "20px" }}>
        {isRegister ? "Create Account" : "Welcome Back"}
      </h2>

      {error && (
        <div style={{ background: "#ff4d4f22", color: "#ff4d4f", padding: "10px", borderRadius: "6px", marginBottom: "15px", fontSize: "14px" }}>
          ⚠️ {error}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {isRegister && (
          <div>
            <label style={{ display: "block", marginBottom: "4px", fontSize: "14px", fontWeight: "600" }}>Name</label>
            <input
              type="text"
              required
              style={{ width: "100%", padding: "10px", borderRadius: "6px", border: "1px solid var(--pat-border)", background: "var(--pat-surface)", color: "var(--pat-text)" }}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
        )}

        <div>
          <label style={{ display: "block", marginBottom: "4px", fontSize: "14px", fontWeight: "600" }}>Email Address</label>
          <input
            type="email"
            required
            style={{ width: "100%", padding: "10px", borderRadius: "6px", border: "1px solid var(--pat-border)", background: "var(--pat-surface)", color: "var(--pat-text)" }}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "4px", fontSize: "14px", fontWeight: "600" }}>Password</label>
          <input
            type="password"
            required
            style={{ width: "100%", padding: "10px", borderRadius: "6px", border: "1px solid var(--pat-border)", background: "var(--pat-surface)", color: "var(--pat-text)" }}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {isRegister && (
          <div>
            <label style={{ display: "block", marginBottom: "4px", fontSize: "14px", fontWeight: "600" }}>Account Type</label>
            <select
              style={{ width: "100%", padding: "10px", borderRadius: "6px", border: "1px solid var(--pat-border)", background: "var(--pat-surface)", color: "var(--pat-text)" }}
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="user">User / Patient</option>
              <option value="therapist">Mental Health Specialist / Therapist</option>
            </select>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{
            marginTop: "10px",
            padding: "12px",
            background: "var(--pat-accent)",
            color: "white",
            border: "none",
            borderRadius: "8px",
            fontWeight: "bold",
            cursor: "pointer",
            boxShadow: "var(--pat-button-shadow)",
          }}
        >
          {loading ? "Please wait..." : isRegister ? "Sign Up" : "Log In"}
        </button>
      </form>

      <div style={{ textAlign: "center", marginTop: "20px", fontSize: "14px" }}>
        {isRegister ? "Already have an account?" : "Need an account?"}{" "}
        <button
          style={{ background: "none", border: "none", color: "var(--pat-accent)", fontWeight: "bold", cursor: "pointer", padding: "0" }}
          onClick={() => {
            setIsRegister(!isRegister);
            setError(null);
          }}
        >
          {isRegister ? "Login" : "Register"}
        </button>
      </div>
    </div>
  );
}
