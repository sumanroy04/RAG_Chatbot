import { useState, useEffect } from "react";

interface Resource {
  id: number;
  title: string;
  category: string;
  content: string;
  tags?: string;
}

interface Props {
  apiBaseUrl: string;
}

export default function ResourceList({ apiBaseUrl }: Props) {
  const [resources, setResources] = useState<Resource[]>([]);
  const [category, setCategory] = useState<string>("");
  const [search, setSearch] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const fetchResources = async () => {
    setLoading(true);
    try {
      let url = `${apiBaseUrl}/api/resources/`;
      const params = new URLSearchParams();
      if (category) params.append("category", category);
      if (search) params.append("q", search);
      
      const queryStr = params.toString();
      if (queryStr) {
        url += `?${queryStr}`;
      }

      const response = await fetch(url);
      if (response.ok) {
        const data = (await response.json()) as Resource[];
        setResources(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      void fetchResources();
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [category, search]);

  return (
    <div className="chat-shell" style={{ padding: "25px", marginTop: "20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", flexWrap: "wrap", gap: "15px" }}>
        <div>
          <h2 style={{ margin: "0 0 5px 0" }}>📚 Wellness Library</h2>
          <p style={{ color: "var(--pat-muted)", margin: "0", fontSize: "14px" }}>
            Authoritative guidelines and articles on managing stress, anxiety, and sleep.
          </p>
        </div>

        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          <select
            style={{ padding: "10px", borderRadius: "6px", border: "1px solid var(--pat-border)", background: "var(--pat-surface)", color: "var(--pat-text)" }}
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">All Categories</option>
            <option value="Anxiety">Anxiety</option>
            <option value="Sleep Issues">Sleep Issues</option>
            <option value="Relationships">Relationships</option>
            <option value="Study Stress">Study Stress</option>
          </select>

          <input
            type="text"
            placeholder="Search library..."
            style={{ padding: "10px", borderRadius: "6px", border: "1px solid var(--pat-border)", background: "var(--pat-surface)", color: "var(--pat-text)" }}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "40px", color: "var(--pat-muted)" }}>Loading articles...</div>
      ) : resources.length === 0 ? (
        <div style={{ textAlign: "center", padding: "40px", color: "var(--pat-muted)" }}>No articles match your query.</div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
          {resources.map((item) => (
            <div
              key={item.id}
              style={{
                border: "1px solid var(--pat-border)",
                borderRadius: "8px",
                padding: "18px",
                background: "var(--pat-surface)",
                boxShadow: "0 4px 12px rgba(0,0,0,0.02)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", flexWrap: "wrap", gap: "10px" }}>
                <h3 style={{ margin: "0 0 8px 0" }}>{item.title}</h3>
                <span
                  style={{
                    padding: "3px 10px",
                    borderRadius: "12px",
                    fontSize: "11px",
                    fontWeight: "bold",
                    background: "var(--pat-accent-soft)",
                    color: "var(--pat-accent-text)",
                  }}
                >
                  {item.category}
                </span>
              </div>
              
              <p style={{ margin: "0 0 12px 0", fontSize: "14px", lineHeight: "1.6", color: "var(--pat-text)" }}>
                {item.content}
              </p>

              {item.tags && (
                <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                  {item.tags.split(",").map((tag) => (
                    <span
                      key={tag}
                      style={{
                        fontSize: "11px",
                        color: "var(--pat-muted)",
                        background: "rgba(0,0,0,0.04)",
                        padding: "2px 8px",
                        borderRadius: "4px",
                      }}
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
