import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createDebate } from "../api.js";

const MODES = [
  { value: "judged", label: "Judged Debate" },
  { value: "simple", label: "Simple Debate" },
  { value: "panel", label: "Panel Discussion" },
];

const LLM_PROVIDERS = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "azure", label: "Azure OpenAI" },
];

export default function HomePage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [form, setForm] = useState({
    motion: "",
    mode: "judged",
    llm: "anthropic",
    epochs: 2,
    model: "",
    temperature: "",
    debater_prompt: "",
    judge_prompt: "",
    use_tools: false,
    domains: "",
  });

  function set(key, value) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (!form.motion.trim()) {
      setError("Please enter a motion.");
      return;
    }

    const payload = {
      motion: form.motion.trim(),
      mode: form.mode,
      llm: form.llm,
      epochs: Number(form.epochs),
    };

    if (form.model) payload.model = form.model;
    if (form.temperature !== "") payload.temperature = Number(form.temperature);
    if (form.debater_prompt) payload.debater_prompt = form.debater_prompt;
    if (form.judge_prompt) payload.judge_prompt = form.judge_prompt;
    if (form.use_tools) payload.use_tools = true;
    if (form.domains) {
      payload.domains = form.domains
        .split(",")
        .map((d) => d.trim())
        .filter(Boolean);
    }

    try {
      setLoading(true);
      const { debate_id } = await createDebate(payload);
      navigate(`/debate/${debate_id}`);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <form className="form-card" onSubmit={handleSubmit}>
      <h1>Start a Debate</h1>

      <div className="field">
        <label>Motion</label>
        <textarea
          value={form.motion}
          onChange={(e) => set("motion", e.target.value)}
          placeholder="e.g. AI will surpass human intelligence within 10 years"
          rows={3}
          required
        />
      </div>

      <div className="row">
        <div className="field">
          <label>Mode</label>
          <select value={form.mode} onChange={(e) => set("mode", e.target.value)}>
            {MODES.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label>LLM Provider</label>
          <select value={form.llm} onChange={(e) => set("llm", e.target.value)}>
            {LLM_PROVIDERS.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label>Epochs</label>
          <input
            type="number"
            min={1}
            max={10}
            value={form.epochs}
            onChange={(e) => set("epochs", e.target.value)}
          />
        </div>
      </div>

      <button
        type="button"
        className="advanced-toggle"
        onClick={() => setShowAdvanced((v) => !v)}
      >
        {showAdvanced ? "Hide" : "Show"} advanced options
      </button>

      {showAdvanced && (
        <>
          <div className="row">
            <div className="field">
              <label>Model override</label>
              <input
                type="text"
                value={form.model}
                onChange={(e) => set("model", e.target.value)}
                placeholder="e.g. gpt-4o"
              />
            </div>
            <div className="field">
              <label>Temperature</label>
              <input
                type="number"
                min={0}
                max={2}
                step={0.1}
                value={form.temperature}
                onChange={(e) => set("temperature", e.target.value)}
                placeholder="0.7"
              />
            </div>
          </div>

          <div className="field">
            <label>Custom debater prompt</label>
            <textarea
              value={form.debater_prompt}
              onChange={(e) => set("debater_prompt", e.target.value)}
              placeholder="Override the default debater system prompt"
            />
          </div>

          <div className="field">
            <label>Custom judge prompt</label>
            <textarea
              value={form.judge_prompt}
              onChange={(e) => set("judge_prompt", e.target.value)}
              placeholder="Override the default judge system prompt"
            />
          </div>

          {form.mode === "panel" && (
            <div className="field">
              <label>Expert domains (comma-separated)</label>
              <input
                type="text"
                value={form.domains}
                onChange={(e) => set("domains", e.target.value)}
                placeholder="e.g. ethics, technology, economics"
              />
            </div>
          )}

          {form.mode !== "panel" && (
            <div className="field">
              <label style={{ flexDirection: "row", gap: "0.5rem", display: "flex", alignItems: "center", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={form.use_tools}
                  onChange={(e) => set("use_tools", e.target.checked)}
                  style={{ width: "auto" }}
                />
                Enable LangChain tools (Wikipedia, DuckDuckGo)
              </label>
            </div>
          )}
        </>
      )}

      {error && <p className="status error">{error}</p>}

      <button type="submit" className="btn" disabled={loading}>
        {loading ? (
          <>
            <span className="spinner" />
            Starting…
          </>
        ) : (
          "Start Debate"
        )}
      </button>
    </form>
  );
}
