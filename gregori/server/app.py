"""GReGOrI Local HTTP Application Server and REST API."""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from ..annotation.ncbi import (
    check_ncbi_tools,
    get_assembly_sequence_summary,
    install_ncbi_tools,
    search_ncbi_assemblies,
)
from ..engine.core import inspect_sequences
from .controller import (
    EHAB_DIR,
    PROJECTS,
    create_ehab_job,
    create_job,
    get_all_projects,
    mutate_project,
    recover_orphaned_projects,
    setup_workspace,
)
from .picker import pick_paths

ROOT = Path(__file__).resolve().parents[2]

LEGACY_CONSOLE_SESSIONS: dict[str, dict] = {}


def start_legacy_console_session() -> dict:
    """Start an interactive Python subprocess for the Legacy script in a sandboxed temp directory."""
    root = ROOT
    legacy_script = root / "Legacy" / "GReGOrI (legacy version).py"
    if not legacy_script.exists():
        legacy_script = root / "Legacy" / "GReGOrI (legacy fallback).py"
    if not legacy_script.exists():
        # check for legacy names as safety fallback
        legacy_script = root / "Legacy" / "GReGOrI_v0.4.2_Legacy.py"
    if not legacy_script.exists():
        return {"error": f"Legacy script not found at {legacy_script}", "status": 404}

    py_exe = sys.executable
    if py_exe.lower().endswith("pythonw.exe"):
        py_exe = py_exe[:-9] + "python.exe"

    # Build PATH that includes the GReGOrI bin/ folder so the Legacy script's
    # shutil.which("datasets") can find the bundled NCBI binary.
    _system = platform.system().lower()
    _machine = platform.machine().lower()
    if "windows" in _system:
        _os_dir = "windows-x64"
    elif "linux" in _system:
        _os_dir = "linux-x64"
    elif "arm" in _machine or "aarch" in _machine:
        _os_dir = "macos-arm64"
    else:
        _os_dir = "macos-x64"

    bin_dir = root / "bin" / _os_dir
    env = dict(os.environ)
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")

    # Create an isolated sandbox directory for this session.
    # All files created by the Legacy script go here and are deleted on exit.
    import tempfile, shutil as _shutil
    sandbox = Path(tempfile.mkdtemp(prefix="gregori_legacy_"))
    env["GREGORI_CACHE"] = str(sandbox / "cache")

    def _cleanup_sandbox():
        try:
            _shutil.rmtree(sandbox, ignore_errors=True)
        except Exception:
            pass

    try:
        proc = subprocess.Popen(
            [py_exe, "-u", str(legacy_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,
            cwd=str(sandbox),   # script runs inside the sandbox
            env=env,
        )
    except Exception as exc:
        _cleanup_sandbox()
        return {"error": f"Failed to start Python process: {exc}", "status": 500}

    session_id = uuid.uuid4().hex[:12]
    session_data = {
        "proc": proc,
        "buffer": [],
        "alive": True,
        "lock": threading.Lock(),
        "created_at": time.time(),
        "sandbox": sandbox,
        "cleanup": _cleanup_sandbox,
    }

    def stdout_reader():
        while True:
            try:
                ch = proc.stdout.read(1)
                if not ch:
                    break
                with session_data["lock"]:
                    session_data["buffer"].append(ch)
            except Exception:
                break
        session_data["alive"] = False
        # Auto-clean when the process exits naturally (e.g. user chose "Exit")
        _cleanup_sandbox()

    t = threading.Thread(target=stdout_reader, daemon=True)
    t.start()

    LEGACY_CONSOLE_SESSIONS[session_id] = session_data
    return {"session_id": session_id, "status": "started"}


def poll_legacy_console_session(session_id: str, offset: int = 0) -> dict:
    """Poll newly buffered stdout/stderr text chunks from the running console process."""
    session = LEGACY_CONSOLE_SESSIONS.get(session_id)
    if not session:
        return {"error": "Session not found", "alive": False, "output": "", "next_offset": offset}

    with session["lock"]:
        full_text = "".join(session["buffer"])

    is_alive = session["proc"].poll() is None
    new_text = full_text[offset:]
    return {
        "output": new_text,
        "next_offset": len(full_text),
        "alive": is_alive
    }


def send_legacy_console_input(session_id: str, text: str) -> dict:
    """Write input line into the subprocess's stdin."""
    session = LEGACY_CONSOLE_SESSIONS.get(session_id)
    if not session or not session.get("proc") or session["proc"].poll() is not None:
        return {"error": "Session is not active"}

    try:
        session["proc"].stdin.write(text + "\n")
        session["proc"].stdin.flush()
        return {"status": "ok"}
    except Exception as exc:
        return {"error": str(exc)}


def interrupt_legacy_console_session(session_id: str) -> dict:
    """Terminate the running interactive Python session and delete its sandbox."""
    session = LEGACY_CONSOLE_SESSIONS.get(session_id)
    if not session:
        return {"status": "ok"}

    try:
        proc = session.get("proc")
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        # Always clean the sandbox, whether terminate succeeded or not
        cleanup = session.get("cleanup")
        if cleanup:
            cleanup()
        LEGACY_CONSOLE_SESSIONS.pop(session_id, None)

    return {"status": "interrupted"}


def serve_file(handler: SimpleHTTPRequestHandler, path: Path, content_type: str | None = None):
    data = path.read_bytes()
    handler.send_response(200)
    handler.send_header("Content-Type", content_type or ("text/html; charset=utf-8" if path.name.endswith(".html") else "application/octet-stream"))
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


class AppHandler(SimpleHTTPRequestHandler):
    """Serve static frontend and handle JSON API requests."""

    def json_response(self, data: dict | list, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8") or "{}")

    def do_GET(self):
        url = urlparse(self.path)
        clean_path = url.path.rstrip("/")

        if clean_path in ("/legacy", "/legacy.html", "/legacy-console"):
            legacy_html = ROOT / "frontend" / "legacy.html"
            if legacy_html.exists():
                return serve_file(self, legacy_html)

        if clean_path == "/api/legacy-console/poll":
            params = parse_qs(url.query)
            sid = params.get("session_id", [""])[0]
            try:
                offset = int(params.get("offset", [0])[0])
            except ValueError:
                offset = 0
            return self.json_response(poll_legacy_console_session(sid, offset))

        if clean_path == "/api/legacy/launch":
            return self.json_response({"status": "launched", "url": "/legacy.html"})

        if url.path == "/api/projects":
            return self.json_response({"projects": get_all_projects()})

        if url.path == "/api/pick-files":
            return self.json_response({"paths": pick_paths("files")})

        if url.path == "/api/pick-folder":
            return self.json_response({"paths": pick_paths("folder")})

        if url.path == "/api/pick-gene-map":
            return self.json_response({"paths": pick_paths("gene_map")})

        if url.path == "/api/ncbi/status":
            return self.json_response(check_ncbi_tools())

        if url.path == "/api/events":
            pid = parse_qs(url.query).get("project_id", [""])[0]
            path = PROJECTS / pid / "events.jsonl"
            events = []
            if path.exists():
                for line in path.read_text(encoding="utf-8").splitlines():
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        pass
            return self.json_response({"events": events})

        if url.path.startswith("/managed/"):
            parts = url.path.split("/")
            pid = unquote(parts[2])
            rel = "/".join(parts[3:])
            base = (PROJECTS / pid).resolve()
            target_path = (base / rel).resolve()
            if base not in target_path.parents and target_path != base:
                return self.send_error(403)
            if target_path.is_file():
                return serve_file(self, target_path)

        if url.path.startswith("/managed_ehab/"):
            parts = url.path.split("/")
            pid = unquote(parts[2])
            rel = "/".join(parts[3:])
            base = (EHAB_DIR / pid).resolve()
            target_path = (base / rel).resolve()
            if base not in target_path.parents and target_path != base:
                return self.send_error(403)
            if target_path.is_file():
                return serve_file(self, target_path)

        return super().do_GET()

    def do_POST(self):
        try:
            url = urlparse(self.path)
            clean_path = url.path.rstrip("/")
            data = self.read_body()

            if clean_path == "/api/legacy-console/start":
                return self.json_response(start_legacy_console_session())

            if clean_path == "/api/legacy-console/input":
                return self.json_response(send_legacy_console_input(data.get("session_id", ""), data.get("input", "")))

            if clean_path == "/api/legacy-console/interrupt":
                return self.json_response(interrupt_legacy_console_session(data.get("session_id", "")))

            if clean_path == "/api/legacy/launch":
                return self.json_response({"status": "launched", "url": "/legacy.html"})

            if clean_path == "/api/upload-fasta":
                upload_dir = PROJECTS / "_uploads"
                upload_dir.mkdir(parents=True, exist_ok=True)
                saved_paths = []
                for f in data.get("files", []):
                    fname = Path(f.get("name", "upload.fasta")).name
                    content = f.get("content", "")
                    dest = upload_dir / fname
                    if f.get("is_base64"):
                        import base64
                        dest.write_bytes(base64.b64decode(content))
                    else:
                        dest.write_text(content, encoding="utf-8")
                    saved_paths.append(str(dest.resolve()))
                return self.json_response({"paths": saved_paths})

            if clean_path == "/api/inspect-fasta":
                return self.json_response(inspect_sequences(data.get("paths", []), data.get("limits") or {}))

            if clean_path == "/api/jobs":
                return self.json_response(create_job(data, source="custom"), 201)

            if clean_path == "/api/jobs/ehab":
                return self.json_response({"error": "EHaB pipeline is currently deactivated (work in progress)"}, 403)

            if clean_path in (
                "/api/project/pause",
                "/api/project/resume",
                "/api/project/cancel",
                "/api/project/restart",
                "/api/project/rerun",
                "/api/project/delete",
                "/api/project/delete-browser",
            ):
                action = clean_path.rsplit("/", 1)[-1]
                return self.json_response(mutate_project(action, data["project_id"]))

            if clean_path == "/api/project/superimpose-genes":
                return self.json_response(mutate_project("superimpose-genes", data["project_id"], gff3=data.get("gff3")))

            if clean_path == "/api/ncbi/install":
                return self.json_response(install_ncbi_tools())

            if clean_path == "/api/ncbi/search":
                return self.json_response({
                    "assemblies": search_ncbi_assemblies(data.get("query", ""), int(data.get("limit", 30)))
                })

            if clean_path == "/api/ncbi/sequences":
                accession = data["accession"]
                sequences = get_assembly_sequence_summary(accession)
                return self.json_response({"accession": accession, "sequences": sequences})

            if clean_path == "/api/jobs/ncbi":
                payload = {
                    "input_paths": [],
                    "assembly_key": data["accession"],
                    "use_referenced_species": True,
                    "species": data.get("species", "Unknown"),
                    "step": data.get("step", 1000),
                    "lookahead": data.get("lookahead", 20000),
                    "threshold": data.get("threshold", 0.99),
                    "limits": {},
                    "selected_sequences": data.get("selected_sequences") or [],
                    "context_flank": data.get("context_flank", 500),
                    "gff3": data.get("gff3"),
                }
                return self.json_response(create_job(payload, source="ncbi", metadata=data.get("metadata") or {}), 201)

            return self.json_response({"error": "Unknown endpoint"}, 404)

        except Exception as exc:
            return self.json_response({"error": str(exc)}, 400)


def start_server(port: int = 8765, open_browser: bool = True):
    """Start local HTTP backend and serve frontend."""
    setup_workspace()
    recover_orphaned_projects()

    frontend_dir = ROOT / "frontend"
    os.chdir(frontend_dir)

    server = ThreadingHTTPServer(("127.0.0.1", port), AppHandler)
    url = f"http://127.0.0.1:{port}/"

    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    print(f"\n========================================================")
    print(f" GReGOrI Palaces Web GUI running at: {url}")
    print(f" Press Ctrl+C to stop the server.")
    print(f"========================================================\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description="Start GReGOrI Local Web Interface")
    parser.add_argument("--port", type=int, default=8765, help="HTTP server port (default: 8765)")
    parser.add_argument("--no-open", action="store_true", help="Do not open web browser automatically")
    args = parser.parse_args()
    start_server(port=args.port, open_browser=not args.no_open)


if __name__ == "__main__":
    main()
