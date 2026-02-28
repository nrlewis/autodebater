const BASE = "/api";

export async function createDebate(payload) {
  const res = await fetch(`${BASE}/debates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function listDebates() {
  const res = await fetch(`${BASE}/debates`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getDebate(debateId) {
  const res = await fetch(`${BASE}/debates/${debateId}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getProfile() {
  const res = await fetch(`${BASE}/profile`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json(); // { content: string }
}

export async function saveProfile(content) {
  const res = await fetch(`${BASE}/profile`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

/**
 * Opens an SSE connection to stream debate messages.
 * @param {string} debateId
 * @param {(msg: object) => void} onMessage  called with each parsed message
 * @param {(err: string) => void} onError
 * @param {() => void} onDone
 * @returns {EventSource} caller can call .close() to abort
 */
export function streamDebate(debateId, onMessage, onError, onDone) {
  const es = new EventSource(`${BASE}/debates/${debateId}/stream`);

  es.onmessage = (event) => {
    const text = event.data;
    if (text === "[DONE]") {
      es.close();
      onDone();
      return;
    }
    try {
      const obj = JSON.parse(text);
      if (obj.error) {
        es.close();
        onError(obj.error);
      } else {
        onMessage(obj);
      }
    } catch {
      // ignore parse errors
    }
  };

  es.onerror = () => {
    es.close();
    onError("Connection lost");
  };

  return es;
}
