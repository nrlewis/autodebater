import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listDebates } from "../api.js";

export default function HistoryPage() {
  const [debates, setDebates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    listDebates()
      .then((data) => {
        setDebates(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="status">
        <span className="spinner" />
        Loading…
      </div>
    );
  }

  if (error) {
    return <div className="status error">Error: {error}</div>;
  }

  if (debates.length === 0) {
    return (
      <div className="empty">
        No saved debates yet. Start one on the home page!
      </div>
    );
  }

  return (
    <div>
      <h1 style={{ marginBottom: "1.2rem", fontSize: "1.3rem" }}>
        Debate History
      </h1>
      <div className="history-list">
        {debates.map((d) => (
          <Link
            key={d.debate_id}
            to={`/debate/${d.debate_id}`}
            className="history-item"
          >
            <span className="badge">{d.mode || "debate"}</span>
            <span className="history-motion">{d.motion}</span>
            {d.created_at && (
              <span className="history-date">
                {new Date(d.created_at).toLocaleDateString(undefined, {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })}
              </span>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
