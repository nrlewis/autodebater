import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { streamDebate } from "../api.js";
import MessageCard from "../components/MessageCard.jsx";
import ScoreBar from "../components/ScoreBar.jsx";

export default function DebatePage() {
  const { debateId } = useParams();
  const [messages, setMessages] = useState([]);
  const [done, setDone] = useState(false);
  const [error, setError] = useState(null);
  const [motion, setMotion] = useState("");
  const [mode, setMode] = useState("judged");
  const bottomRef = useRef(null);
  const esRef = useRef(null);

  // Derive the latest score/convergence from messages
  const latestScore = (() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].judgement != null) return messages[i].judgement;
    }
    return null;
  })();

  useEffect(() => {
    const es = streamDebate(
      debateId,
      (msg) => {
        if (!motion && msg.debate_id) {
          // pick up mode hint if available (not in message, but we detect panel via role)
        }
        setMessages((prev) => {
          // Update motion from first non-moderator debater message if not set
          return [...prev, msg];
        });
        // Auto-scroll
        setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
      },
      (err) => setError(err),
      () => setDone(true)
    );
    esRef.current = es;

    return () => es.close();
  }, [debateId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Detect mode from messages
  useEffect(() => {
    if (messages.some((m) => m.role === "panelist")) {
      setMode("panel");
    }
  }, [messages]);

  const motionText =
    messages.find((m) => m.role === "moderator")?.message?.replace(/^Panel discussion on:\s*/i, "").replace(/\.\s*Please begin\.$/, "") ||
    `Debate ${debateId.slice(0, 8)}`;

  return (
    <div>
      <div className="debate-header">
        <h1>{motionText}</h1>
        <div className="debate-meta">
          <span className="badge">{mode}</span>
          <span>{debateId.slice(0, 8)}</span>
        </div>
      </div>

      {latestScore != null && (
        <ScoreBar score={latestScore} mode={mode === "panel" ? "panel" : "debate"} />
      )}

      <div className="status">
        {!done && !error && (
          <>
            <span className="spinner" />
            Debate in progress…
          </>
        )}
        {done && !error && "Debate complete."}
        {error && <span className="error">Error: {error}</span>}
      </div>

      <div className="messages">
        {messages.map((msg, i) => (
          <MessageCard key={i} msg={msg} />
        ))}
      </div>

      <div ref={bottomRef} />
    </div>
  );
}
