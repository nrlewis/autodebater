/**
 * ScoreBar — visualises either:
 *   mode="debate"  : running score 0-100 where 50 = neutral, >50 = FOR winning
 *   mode="panel"   : convergence 0-100 where higher = more converged
 */
export default function ScoreBar({ score, mode = "debate" }) {
  if (score == null) return null;

  const pct = Math.min(100, Math.max(0, score));

  let fillColor;
  let leftLabel;
  let rightLabel;

  if (mode === "panel") {
    // Convergence bar: left=diverged, right=converged
    const hue = Math.round((pct / 100) * 120); // red→green
    fillColor = `hsl(${hue}, 70%, 55%)`;
    leftLabel = "Diverged";
    rightLabel = "Converged";
  } else {
    // Debate score: left=CON winning, right=FOR winning
    const distance = Math.abs(pct - 50);
    const hue = pct >= 50 ? 140 : 0; // green for FOR, red for CON
    const lightness = 65 - distance * 0.3;
    fillColor = `hsl(${hue}, 65%, ${lightness}%)`;
    leftLabel = "CON";
    rightLabel = "FOR";
  }

  return (
    <div className="score-bar-wrap">
      <div className="score-bar-label">
        <span>{leftLabel}</span>
        <span>{rightLabel}</span>
      </div>
      <div className="score-bar-track">
        <div
          className="score-bar-fill"
          style={{ width: `${pct}%`, background: fillColor }}
        />
      </div>
      <div className="score-value">
        {mode === "panel"
          ? `Convergence: ${pct.toFixed(1)}/100`
          : `Score: ${pct.toFixed(1)}/100`}
      </div>
    </div>
  );
}
