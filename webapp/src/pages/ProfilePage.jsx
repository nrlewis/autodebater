import { useEffect, useState } from "react";
import { getProfile, saveProfile } from "../api.js";

export default function ProfilePage() {
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    getProfile()
      .then((data) => {
        setContent(data.content);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  async function handleSave(e) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    setSaved(false);
    try {
      await saveProfile(content);
      setSaved(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="status">
        <span className="spinner" />
        Loading…
      </div>
    );
  }

  return (
    <form className="form-card" onSubmit={handleSave}>
      <h1>Your Profile</h1>
      <p style={{ color: "var(--text-muted, #888)", marginBottom: "1rem", fontSize: "0.9rem" }}>
        This context is automatically injected into every participant's system prompt.
        Use it to describe your situation, goals, or any background the panel should know about.
      </p>

      <div className="field">
        <label>Background context</label>
        <textarea
          value={content}
          onChange={(e) => { setContent(e.target.value); setSaved(false); }}
          placeholder={`e.g.\n# About Me\nI'm a software engineer at a Series B startup...\n\n# Current question\nWe're deciding whether to build or buy a feature store.`}
          rows={16}
          style={{ fontFamily: "monospace", fontSize: "0.85rem" }}
        />
      </div>

      {error && <p className="status error">{error}</p>}
      {saved && <p className="status" style={{ color: "green" }}>Saved.</p>}

      <button type="submit" className="btn" disabled={saving}>
        {saving ? (
          <>
            <span className="spinner" />
            Saving…
          </>
        ) : (
          "Save Profile"
        )}
      </button>
    </form>
  );
}
