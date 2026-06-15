import { useState, useEffect } from "react";

interface Appointment {
  id: number;
  therapist_name: string;

  date_time: string;
  status: string;
}

interface Props {
  token: string | null;
  apiBaseUrl: string;
}

const THERAPISTS = [
  "Dr. Ananya Sharma (Clinical Psychologist)",
  "Dr. Rohan Verma (Psychiatrist)",
  "Dr. Sarah Kurian (Counsellor)",
  "Prof. Amit Sen (Child & Adolescent Therapist)",
];

export default function BookingForm({ token, apiBaseUrl }: Props) {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [therapist, setTherapist] = useState(THERAPISTS[0]);
  const [dateTime, setDateTime] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchAppointments = async () => {
    if (!token) return;
    try {
      const response = await fetch(`${apiBaseUrl}/api/appointments/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = (await response.json()) as Appointment[];
        setAppointments(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    void fetchAppointments();
  }, [token]);

  const handleBook = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      setError("Please log in first to book an appointment.");
      return;
    }
    if (!dateTime) {
      setError("Please select a date and time.");
      return;
    }

    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      const response = await fetch(`${apiBaseUrl}/api/appointments/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          therapist_name: therapist,
          date_time: dateTime,
        }),
      });

      if (!response.ok) {
        throw new Error("Could not book appointment. Please try again.");
      }

      setSuccess("Your appointment has been booked successfully! Confirmations sent.");
      setDateTime("");
      void fetchAppointments();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to book appointment.");
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="chat-shell" style={{ textAlign: "center", padding: "40px" }}>
        <h2>🗓️ Appointment Scheduling</h2>
        <p style={{ color: "var(--pat-muted)", margin: "15px 0" }}>
          Secure session booking requires an active account. Please register or login to manage consultations.
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "25px", marginTop: "20px" }}>
      <div className="chat-shell" style={{ padding: "25px" }}>
        <h3>Schedule a Session</h3>
        <p style={{ color: "var(--pat-muted)", fontSize: "14px", marginBottom: "15px" }}>
          Choose a qualified specialist and a convenient slot.
        </p>

        {error && <div style={{ color: "#ff4d4f", background: "#ff4d4f11", padding: "8px", borderRadius: "6px", marginBottom: "12px", fontSize: "13px" }}>⚠️ {error}</div>}
        {success && <div style={{ color: "#52c41a", background: "#52c41a11", padding: "8px", borderRadius: "6px", marginBottom: "12px", fontSize: "13px" }}>✅ {success}</div>}

        <form onSubmit={handleBook} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <div>
            <label style={{ display: "block", marginBottom: "4px", fontSize: "14px", fontWeight: "600" }}>Therapist / Counselor</label>
            <select
              style={{ width: "100%", padding: "10px", borderRadius: "6px", border: "1px solid var(--pat-border)", background: "var(--pat-surface)", color: "var(--pat-text)" }}
              value={therapist}
              onChange={(e) => setTherapist(e.target.value)}
            >
              {THERAPISTS.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: "block", marginBottom: "4px", fontSize: "14px", fontWeight: "600" }}>Date and Time</label>
            <input
              type="datetime-local"
              required
              style={{ width: "100%", padding: "10px", borderRadius: "6px", border: "1px solid var(--pat-border)", background: "var(--pat-surface)", color: "var(--pat-text)" }}
              value={dateTime}
              onChange={(e) => setDateTime(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "10px",
              background: "var(--pat-accent)",
              color: "white",
              border: "none",
              borderRadius: "8px",
              fontWeight: "bold",
              cursor: "pointer",
            }}
          >
            {loading ? "Booking..." : "Confirm Schedule"}
          </button>
        </form>
      </div>

      <div className="chat-shell" style={{ padding: "25px" }}>
        <h3>Your Appointments</h3>
        <p style={{ color: "var(--pat-muted)", fontSize: "14px", marginBottom: "15px" }}>
          Upcoming and past consultations.
        </p>

        {appointments.length === 0 ? (
          <p style={{ color: "var(--pat-muted)", fontSize: "14px", textAlign: "center", marginTop: "30px" }}>
            No scheduled sessions found.
          </p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px", maxHeight: "350px", overflowY: "auto" }}>
            {appointments.map((appt) => (
              <div
                key={appt.id}
                style={{
                  border: "1px solid var(--pat-border)",
                  borderRadius: "8px",
                  padding: "12px",
                  background: "var(--pat-surface-soft)",
                }}
              >
                <div style={{ fontWeight: "700", fontSize: "14px" }}>{appt.therapist_name}</div>
                <div style={{ color: "var(--pat-muted)", fontSize: "13px", marginTop: "4px" }}>
                  📅 {new Date(appt.date_time).toLocaleString()}
                </div>
                <span
                  style={{
                    display: "inline-block",
                    marginTop: "6px",
                    padding: "2px 8px",
                    borderRadius: "12px",
                    fontSize: "11px",
                    fontWeight: "bold",
                    background: appt.status === "Scheduled" ? "#52c41a22" : "#bfbfbf22",
                    color: appt.status === "Scheduled" ? "#52c41a" : "#8c8c8c",
                  }}
                >
                  {appt.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
