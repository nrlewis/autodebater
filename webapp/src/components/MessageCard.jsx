export default function MessageCard({ msg }) {
  const { name, role, stance, judgement, message } = msg;

  const stanceClass = stance
    ? `stance-${stance.toLowerCase().replace(/\s+/g, "-")}`
    : "";

  return (
    <div className={`message-card role-${role} ${stanceClass}`}>
      <div className="message-header">
        <span className="message-name">{name}</span>
        <span className="message-role">{role}</span>
        {stance && <span className="message-stance">{stance}</span>}
        {judgement != null && (
          <span className="message-score">Score: {Number(judgement).toFixed(1)}</span>
        )}
      </div>
      <div className="message-text">{message}</div>
    </div>
  );
}
