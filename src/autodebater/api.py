"""
FastAPI backend for AutoDebater.
Debates run in background threads; messages are streamed to clients via SSE.
"""

import asyncio
import json
import logging
import os
import threading
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from autodebater.debate_runners import (
    BasicJudgedDebateRunner,
    BasicSimpleDebateRunner,
    ExpertPanelRunner,
    RunnerConfig,
)
from autodebater.persistence import DebateExporter, DebateStore
from autodebater.profile import ProfileStore

logger = logging.getLogger(__name__)

app = FastAPI(title="AutoDebater API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory registry of running/completed debates
_debates: dict = {}


class DebateRequest(BaseModel):
    motion: str
    mode: str = "judged"          # "judged" | "simple" | "panel"
    llm: str = "openai"
    epochs: int = 2
    debater_prompt: Optional[str] = None
    judge_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    use_tools: Optional[bool] = None  # None = mode-dependent default
    domains: Optional[List[str]] = None
    context: Optional[str] = None     # override profile context for this debate


def _build_runner(req: DebateRequest):
    # Panel defaults to tools-on (evidence-backed discussion); debates default off
    use_tools = req.use_tools if req.use_tools is not None else (req.mode == "panel")
    # Auto-load profile unless the request supplies explicit context
    context = req.context or ProfileStore().load()
    config = RunnerConfig(
        motion=req.motion,
        epochs=req.epochs,
        llm=req.llm,
        debater_prompt=req.debater_prompt,
        judge_prompt=req.judge_prompt,
        model=req.model,
        temperature=req.temperature,
        use_tools=use_tools,
        domains=req.domains,
        context=context,
    )
    if req.mode == "panel":
        return ExpertPanelRunner(config)
    if req.mode == "simple":
        return BasicSimpleDebateRunner.from_config(config)
    return BasicJudgedDebateRunner.from_config(config)


def _run_in_thread(debate_id: str, runner):
    try:
        for msg in runner.run_debate():
            _debates[debate_id]["messages"].append(msg.to_dict())
    except Exception as exc:
        logger.exception("Debate %s failed: %s", debate_id, exc)
        _debates[debate_id]["error"] = str(exc)
    finally:
        _debates[debate_id]["done"] = True
        # Persist on completion
        try:
            motion = _debates[debate_id]["motion"]
            DebateStore().save(runner.debate.dialogue_history, motion)
        except Exception:
            pass


@app.get("/api/profile")
async def get_profile():
    content = ProfileStore().load()
    return {"content": content or ""}


@app.put("/api/profile")
async def save_profile(payload: dict):
    ProfileStore().save(payload.get("content", ""))
    return {"status": "saved"}


@app.post("/api/debates")
async def create_debate(req: DebateRequest):
    runner = _build_runner(req)
    debate_id = runner.debate.debate_id
    _debates[debate_id] = {
        "motion": req.motion,
        "mode": req.mode,
        "messages": [],
        "done": False,
        "error": None,
    }
    thread = threading.Thread(target=_run_in_thread, args=(debate_id, runner), daemon=True)
    thread.start()
    return {"debate_id": debate_id, "mode": req.mode, "motion": req.motion}


@app.get("/api/debates/{debate_id}/stream")
async def stream_debate(debate_id: str):
    """SSE endpoint — streams messages as they are produced."""

    # Check active debates first
    if debate_id in _debates:
        record = _debates[debate_id]

        async def generate_live():
            index = 0
            while True:
                messages = record["messages"]
                while index < len(messages):
                    yield f"data: {json.dumps(messages[index])}\n\n"
                    index += 1  # noqa: F821  (nonlocal via closure is fine here)
                if record["done"]:
                    if record["error"]:
                        yield f"data: {json.dumps({'error': record['error']})}\n\n"
                    yield "data: [DONE]\n\n"
                    break
                await asyncio.sleep(0.15)

        # Rebind index in a mutable container to avoid Python closure gotcha
        async def generate_live_fixed():
            idx = 0
            while True:
                messages = record["messages"]
                while idx < len(messages):
                    yield f"data: {json.dumps(messages[idx])}\n\n"
                    idx += 1
                if record["done"]:
                    if record["error"]:
                        yield f"data: {json.dumps({'error': record['error']})}\n\n"
                    yield "data: [DONE]\n\n"
                    break
                await asyncio.sleep(0.15)

        return StreamingResponse(
            generate_live_fixed(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # Fall back to persisted history
    store = DebateStore()
    messages = store.load(debate_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Debate not found")

    async def replay():
        for msg in messages:
            yield f"data: {json.dumps(msg.to_dict())}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        replay(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/debates")
async def list_debates():
    return DebateStore().list_debates()


@app.get("/api/debates/{debate_id}")
async def get_debate(debate_id: str):
    store = DebateStore()
    messages = store.load(debate_id)
    debates = store.list_debates()
    meta = next((d for d in debates if d["debate_id"] == debate_id), None)
    if not meta and debate_id not in _debates:
        raise HTTPException(status_code=404, detail="Debate not found")
    if not meta and debate_id in _debates:
        meta = {
            "debate_id": debate_id,
            "motion": _debates[debate_id]["motion"],
            "mode": _debates[debate_id]["mode"],
            "created_at": None,
        }
    return {"meta": meta, "messages": [m.to_dict() for m in messages]}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ── Serve React SPA (production build) ──────────────────────────────────────
_WEBAPP_DIST = Path(__file__).parent.parent.parent.parent / "webapp" / "dist"

if _WEBAPP_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=str(_WEBAPP_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        return FileResponse(str(_WEBAPP_DIST / "index.html"))
