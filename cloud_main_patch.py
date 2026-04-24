"""
Cloud-patched main.py for GitHub Actions deployment.
Accepts JSON requests (from mobile), passes GEMINI_API_KEY from env,
and disables features that need local-only services (Ollama, tunnels).
"""

import os
import uuid
import json
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from pipeline.script_generator import ScriptGenerator
from pipeline.voice_generator import VoiceGenerator
from pipeline.avatar_generator import AvatarGenerator
from pipeline.bgm_generator import BGMGenerator
from pipeline.video_composer import VideoComposer
from pipeline.anti_detect import AntiDetect

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR.parent / "output"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="AI Reel Generator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR.parent / "frontend")), name="static")
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

script_gen = ScriptGenerator()
voice_gen = VoiceGenerator()
avatar_gen = AvatarGenerator(assets_dir=ASSETS_DIR)
bgm_gen = BGMGenerator(assets_dir=ASSETS_DIR)
video_composer = VideoComposer()
anti_detect = AntiDetect()


def _find_session(session_id: str, required_file: str = None):
    """Find a valid session dir. Falls back to the most recent session if needed."""
    if session_id:
        session_dir = OUTPUT_DIR / session_id
        if session_dir.exists():
            if required_file is None or (session_dir / required_file).exists():
                return session_dir

    for d in sorted(OUTPUT_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if d.is_dir():
            if required_file is None or (d / required_file).exists():
                return d
    return None


async def _get_body(request: Request) -> dict:
    """Parse request body as JSON or form data."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        return await request.json()
    else:
        form = await request.form()
        return dict(form)


@app.get("/")
async def serve_frontend():
    return FileResponse(str(BASE_DIR.parent / "frontend" / "index.html"))


@app.post("/api/script/generate")
async def generate_script(request: Request):
    data = await _get_body(request)
    topic = data.get("topic", "")
    tone = data.get("tone", "comedy")
    duration = int(data.get("duration_seconds", data.get("duration", 30)))
    provider = data.get("provider", "gemini")

    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    if provider == "ollama":
        provider = "gemini"

    try:
        result = await script_gen.generate(
            topic=topic, tone=tone, duration_sec=duration, provider=provider
        )
        script_text = result.get("full_script", "")
        session_id = data.get("session_id", str(uuid.uuid4()))
        session_dir = OUTPUT_DIR / session_id
        session_dir.mkdir(exist_ok=True)
        (session_dir / "script.json").write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")

        result["session_id"] = session_id
        result["script"] = script_text
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/generate")
async def generate_voice(request: Request):
    data = await _get_body(request)
    session_id = data.get("session_id", str(uuid.uuid4()))
    voice = data.get("voice", "hi-IN-SwaraNeural")
    speed = float(data.get("speed", 1.0))

    session_dir = OUTPUT_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    text = data.get("script", "").strip()

    if not text:
        script_file = session_dir / "script.json"
        if script_file.exists():
            script_data = json.loads(script_file.read_text(encoding="utf-8"))
            text = script_data.get("full_script", "")

    if not text:
        for d in sorted(OUTPUT_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if d.is_dir():
                sf = d / "script.json"
                if sf.exists():
                    sd = json.loads(sf.read_text(encoding="utf-8"))
                    text = sd.get("full_script", "")
                    if text:
                        session_id = d.name
                        session_dir = d
                        break

    if not text:
        raise HTTPException(status_code=400, detail="No script text found. Pass 'script' in the request or generate a script first.")

    try:
        result = await voice_gen.generate(text=text, voice=voice, output_dir=session_dir)
        result["session_id"] = session_id
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/avatar/generate")
async def generate_avatar(request: Request):
    data = await _get_body(request)
    session_id = data.get("session_id", "")
    mode = data.get("avatar_type", data.get("mode", "animated"))
    preset = data.get("avatar_preset", "default")

    session_dir = _find_session(session_id, "voiceover.mp3")
    if session_dir is None:
        raise HTTPException(status_code=400, detail="Generate voiceover first")
    session_id = session_dir.name

    audio_path = session_dir / "voiceover.mp3"

    if mode in ("sadtalker", "realistic"):
        mode = "animated"
    if mode in ("wav2lip", "lipsync"):
        mode = "animated"

    try:
        result = await avatar_gen.generate(
            mode=mode,
            audio_path=str(audio_path),
            output_dir=str(session_dir),
            image_path=None,
            preset=preset,
        )
        result["session_id"] = session_id
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/avatar/presets")
async def list_avatar_presets():
    presets = avatar_gen.list_presets()
    return JSONResponse({"presets": presets})


@app.post("/api/bgm/select")
async def select_bgm(request: Request):
    data = await _get_body(request)
    session_id = data.get("session_id", "")
    category = data.get("category", "comedy")
    volume = float(data.get("volume", 0.15))

    session_dir = _find_session(session_id)
    if session_dir is None:
        session_dir = OUTPUT_DIR / (session_id or str(uuid.uuid4()))
        session_dir.mkdir(exist_ok=True)
    session_id = session_dir.name

    try:
        result = await bgm_gen.select(
            category=category,
            output_dir=str(session_dir),
            custom_prompt=None,
        )
        result["session_id"] = session_id
        result["volume"] = volume
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bgm/library")
async def list_bgm_library():
    library = bgm_gen.list_library()
    return JSONResponse({"tracks": library})


@app.post("/api/video/compose")
async def compose_video(request: Request):
    data = await _get_body(request)
    session_id = data.get("session_id", "")
    captions = data.get("captions", data.get("add_captions", True))
    if isinstance(captions, str):
        captions = captions.lower() in ("true", "1", "yes")
    caption_style = data.get("caption_style", "word_highlight")

    session_dir = _find_session(session_id, "voiceover.mp3")
    if session_dir is None:
        raise HTTPException(status_code=400, detail="Generate voiceover first")
    session_id = session_dir.name

    try:
        result = await video_composer.compose(
            session_dir=str(session_dir),
            add_captions=captions,
            caption_style=caption_style,
        )
        result["session_id"] = session_id
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/video/finalize")
async def finalize_video(request: Request):
    data = await _get_body(request)
    session_id = data.get("session_id", "")
    anti_detect_level = data.get("anti_detect_level", "medium")

    grain_map = {"light": 0.01, "medium": 0.02, "heavy": 0.04}
    grain = grain_map.get(anti_detect_level, 0.02)
    room_tone = anti_detect_level != "light"

    session_dir = _find_session(session_id, "composed.mp4")
    if session_dir is None:
        raise HTTPException(status_code=400, detail="Compose video first")
    session_id = session_dir.name

    try:
        result = await anti_detect.process(
            session_dir=str(session_dir),
            grain_intensity=grain,
            audio_room_tone=room_tone,
        )
        result["session_id"] = session_id
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}/files")
async def list_session_files(session_id: str):
    session_dir = OUTPUT_DIR / session_id
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    files = [f.name for f in session_dir.iterdir() if f.is_file()]
    return JSONResponse({"files": files, "session_id": session_id})


@app.get("/api/session/{session_id}/download/{filename}")
async def download_file(session_id: str, filename: str):
    file_path = OUTPUT_DIR / session_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path), filename=filename)


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    session_dir = OUTPUT_DIR / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir)
    return JSONResponse({"status": "deleted", "session_id": session_id})
