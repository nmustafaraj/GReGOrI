"""Project manager, worker execution, and lifecycle mutation controller."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import threading
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..annotation.gff import load_gene_map, open_text
from ..annotation.ncbi import download_ncbi_package
from ..annotation.overlap import find_overlapping_genes, superimpose_genes_on_shanes
from ..browser.builder import build_browser, build_ehab_draft, build_library
from ..engine.core import (
    accession_from_header,
    analyse_sequence,
    enrich_shane_details,
    inspect_sequences,
    records,
    similarity,
    species_from_header,
    write_outputs,
)
from ..engine.alignment import get_reverse_complement, rc
from ..palaces.naming import barcode, legacy_name
from ..palaces.sequence_report import fallback as fallback_seq_record, load as load_seq_report

HOME = Path.home() / "Documents" / "GReGOrI"
PROJECTS = HOME / "projects"
EHAB_DIR = HOME / "ehab_runs"
TRASH = HOME / ".trash"
CACHE = HOME / "cache"
FLAGS: dict[str, dict[str, bool]] = {}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def setup_workspace():
    """Ensure required home directories exist."""
    for path in (
        PROJECTS,
        EHAB_DIR,
        TRASH,
        CACHE,
        HOME / "imports",
        HOME / "exports",
        HOME / "logs",
        HOME / "settings",
    ):
        path.mkdir(parents=True, exist_ok=True)


def _safe_clean_dir(path: Path) -> None:
    """Safely and thoroughly clean a directory, handling Windows file locks and read-only attributes."""
    if not path.exists():
        return
    import stat
    def on_rm_error(func, p, exc_info):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:
            pass

    try:
        shutil.rmtree(path, onerror=on_rm_error, ignore_errors=True)
    except Exception:
        pass

    if path.exists():
        trash_dest = TRASH / f"abandoned_{path.name}_{int(time.time() * 1000)}"
        try:
            shutil.move(str(path), str(trash_dest))
        except Exception:
            pass


def read_manifest(pid: str) -> dict[str, Any]:
    path = PROJECTS / pid / "project.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(pid: str, data: dict[str, Any]) -> dict[str, Any]:
    data["updated_utc"] = utc_now()
    proj_dir = PROJECTS / pid
    if proj_dir.exists():
        (proj_dir / "project.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def update_manifest(pid: str, **changes) -> dict[str, Any]:
    data = read_manifest(pid)
    if not data:
        return {}
    data.update(changes)
    return write_manifest(pid, data)


def read_card(pid: str) -> dict[str, Any]:
    """Read card file for live genome size, SHaNE discovery, and stage tracking."""
    path = PROJECTS / pid / "card.json"
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    manifest = read_manifest(pid)
    if not manifest:
        return {}
    summary = manifest.get("summary", {})
    status = manifest.get("status", "unknown")
    color = "neon_blue" if status == "complete" else "gray"
    return {
        "project_id": pid,
        "assembly_key": manifest.get("assembly_key", pid),
        "species": manifest.get("species", "Unknown"),
        "category": "shane" if status == "complete" else "gregori",
        "status": status,
        "created_utc": manifest.get("created_utc", utc_now()),
        "updated_utc": manifest.get("updated_utc", utc_now()),
        "total_bases": summary.get("genome_size_bp", 0),
        "completed_bases": summary.get("genome_size_bp", 0) if status == "complete" else 0,
        "percent_complete": 100.0 if status == "complete" else 0.0,
        "sequences_total": summary.get("sequences", 0),
        "sequences_completed": summary.get("sequences", 0) if status == "complete" else 0,
        "current_sequence": None,
        "shanes_discovered": summary.get("shanes", 0),
        "genes_superimposed": summary.get("genes_crossed"),
        "gene_discovery_status": "completed" if summary.get("genes_crossed") is not None and summary.get("genes_crossed") > 0 else "not_run",
        "color_state": color,
        "parameters": manifest.get("parameters", {}),
    }


def write_card(pid: str, data: dict[str, Any]) -> dict[str, Any]:
    """Write card tracking file atomically."""
    data["updated_utc"] = utc_now()
    proj_dir = PROJECTS / pid
    if proj_dir.exists():
        target = proj_dir / "card.json"
        tmp = proj_dir / "card.json.tmp"
        try:
            tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            tmp.replace(target)
        except Exception:
            try:
                target.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except Exception:
                pass
    return data


def update_card(pid: str, **changes) -> dict[str, Any]:
    """Update card tracking fields."""
    data = read_card(pid)
    if not data:
        return {}
    data.update(changes)
    return write_card(pid, data)

def read_ehab_manifest(pid: str) -> dict[str, Any]:
    path = EHAB_DIR / pid / "project.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_ehab_manifest(pid: str, data: dict[str, Any]) -> dict[str, Any]:
    data["updated_utc"] = utc_now()
    proj_dir = EHAB_DIR / pid
    if proj_dir.exists():
        (proj_dir / "project.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def update_ehab_manifest(pid: str, **changes) -> dict[str, Any]:
    data = read_ehab_manifest(pid)
    if not data:
        return {}
    data.update(changes)
    return write_ehab_manifest(pid, data)


def read_ehab_card(pid: str) -> dict[str, Any]:
    path = EHAB_DIR / pid / "card.json"
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    manifest = read_ehab_manifest(pid)
    if not manifest:
        return {}
    status = manifest.get("status", "unknown")
    color = "gold" if status == "complete" else "gray"
    return {
        "project_id": pid,
        "assembly_key": manifest.get("assembly_key", pid),
        "species": manifest.get("species", "Unknown"),
        "category": "ehab",
        "status": status,
        "created_utc": manifest.get("created_utc", utc_now()),
        "updated_utc": manifest.get("updated_utc", utc_now()),
        "percent_complete": 100.0 if status == "complete" else 0.0,
        "total_combinations": 60,
        "completed_combinations": 60 if status == "complete" else 0,
        "current_combination": None,
        "max_discovery_shanes": manifest.get("peak_run", {}).get("max_shanes", 0),
        "optimal_parameters": manifest.get("peak_run", {}).get("parameters"),
        "color_state": color,
        "browser_entry": f"/managed_ehab/{pid}/ehab_browser/index.html" if status == "complete" else None,
    }


def write_ehab_card(pid: str, data: dict[str, Any]) -> dict[str, Any]:
    data["updated_utc"] = utc_now()
    proj_dir = EHAB_DIR / pid
    if proj_dir.exists():
        (proj_dir / "card.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def update_ehab_card(pid: str, **changes) -> dict[str, Any]:
    data = read_ehab_card(pid)
    if not data:
        return {}
    data.update(changes)
    return write_ehab_card(pid, data)


def get_all_ehab_projects() -> list[dict[str, Any]]:
    out = []
    if not EHAB_DIR.exists():
        return out
    for path in EHAB_DIR.glob("*/project.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            pid = data.get("project_id") or path.parent.name
            data["card"] = read_ehab_card(pid)
            out.append(data)
        except Exception:
            pass
    return out



def emit_event(pid: str, event: str, **data):
    events_file = PROJECTS / pid / "events.jsonl"
    if not events_file.parent.exists():
        return
    try:
        with events_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"utc": utc_now(), "event": event, **data}) + "\n")
    except OSError:
        pass


class Control:
    """Thread-safe in-memory cancellation and pause checkpoint monitor."""

    def __init__(self, pid: str):
        self.pid = pid
        self._was_paused = False

    def safe_point(self, checkpoint: dict[str, Any]):
        flags = FLAGS.setdefault(self.pid, {"pause": False, "cancel": False})
        if flags.get("cancel"):
            raise InterruptedError("cancelled")
        if flags.get("pause"):
            self._was_paused = True
            update_manifest(self.pid, status="paused", checkpoint=checkpoint)
            update_card(self.pid, status="paused")
            emit_event(self.pid, "job_paused", checkpoint=checkpoint)
            while flags.get("pause"):
                time.sleep(0.25)
                flags = FLAGS.get(self.pid, {"pause": False, "cancel": False})
                if flags.get("cancel"):
                    raise InterruptedError("cancelled")
            self._was_paused = False
            update_manifest(self.pid, status="analysing")
            update_card(self.pid, status="analysing")
            emit_event(self.pid, "job_resumed")
        elif self._was_paused:
            self._was_paused = False
            update_manifest(self.pid, status="analysing")
            update_card(self.pid, status="analysing")


def normalize_project(data: dict[str, Any], path: Path | None = None) -> dict[str, Any]:
    data = dict(data or {})
    pid = data.get("project_id") or (path.parent.name if path else "UNKNOWN")
    data.setdefault("project_id", pid)
    data.setdefault("assembly_key", data.get("assembly_accession") or pid.split("__", 1)[0])
    data.setdefault("analysis_version", pid.rsplit("__", 1)[-1] if "__" in pid else "legacy")
    data.setdefault("source", "legacy")
    data.setdefault("species", "Unknown")
    params = data.get("parameters") if isinstance(data.get("parameters"), dict) else {}
    params.setdefault("step", 1000)
    params.setdefault("lookahead", 20000)
    params.setdefault("threshold", 0.99)
    data["parameters"] = params
    data.setdefault("input_summary", {})
    data.setdefault("summary", {})
    data.setdefault("metadata", {})
    data.setdefault("outputs", {})
    data.setdefault("visibility", {"gregori": True, "shane": True, "ehab": False})
    if data.get("repository_owner") == "ehab":
        data["visibility"] = {"gregori": False, "shane": False, "ehab": True}
    data.setdefault("created_utc", data.get("updated_utc") or utc_now())
    data.setdefault("updated_utc", data["created_utc"])
    data.setdefault("status", "unknown")
    if data["status"] == "complete" and not data.get("completed_utc"):
        data["completed_utc"] = data.get("updated_utc")
    return data


def recover_orphaned_projects():
    for path in PROJECTS.glob("*/project.json"):
        try:
            data = normalize_project(json.loads(path.read_text(encoding="utf-8")), path)
        except Exception:
            continue
        pid = data.get("project_id") or path.parent.name
        if data.get("status") in {"queued", "analysing", "downloading", "pausing", "paused", "cancelling"}:
            data["status"] = "interrupted"
            data["interruption_reason"] = "Server was restarted while analysis was running."
            data["updated_utc"] = utc_now()
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            update_card(pid, status="interrupted", color_state="gray")


def get_all_projects() -> list[dict[str, Any]]:
    out = []
    for path in PROJECTS.glob("*/project.json"):
        try:
            p = normalize_project(json.loads(path.read_text(encoding="utf-8")), path)
            p["card"] = read_card(p["project_id"])
            out.append(p)
        except Exception:
            pass
    for ep in get_all_ehab_projects():
        out.append(ep)
    return sorted(out, key=lambda x: x.get("updated_utc", ""), reverse=True)


def calculate_signature(files: list[str], params: dict[str, Any], selection: list[str] | None = None) -> str:
    payload = {
        "files": [(str(Path(x).resolve()), Path(x).stat().st_size, Path(x).stat().st_mtime_ns) for x in files if Path(x).exists()],
        "parameters": params,
        "selection": sorted(selection or []),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]


def determine_project_identity(
    report: dict[str, Any],
    params: dict[str, Any],
    assembly_key: str | None = None,
    selection: list[str] | None = None,
) -> tuple[str, str]:
    source_hash = hashlib.sha256("".join(report["files"]).encode()).hexdigest()[:10]
    assembly = assembly_key or f"CUSTOM_{source_hash}"
    sig = calculate_signature(report["files"], params, selection)
    return assembly, f"{assembly}__{sig}"


def create_job(
    data: dict[str, Any],
    source: str = "custom",
    metadata: dict[str, Any] | None = None,
    gff3: str | None = None,
    launch: bool = True,
) -> dict[str, Any]:
    limits = data.get("limits") or {}
    params = {
        "step": int(data.get("step", 1000)),
        "lookahead": int(data.get("lookahead", 20000)),
        "threshold": float(data.get("threshold", 0.99)),
        "context_flank": max(0, min(10000, int(data.get("context_flank", 500)))),
    }
    selection = data.get("selected_sequences") or []
    custom_gene_map = gff3 or data.get("gff3") or data.get("gene_map")

    if source == "ncbi" and not data.get("input_paths"):
        assembly = data.get("assembly_key") or data.get("accession")
        if not assembly:
            raise ValueError("Assembly accession is required for NCBI jobs.")
        sig = hashlib.sha256(json.dumps({"assembly": assembly, "parameters": params, "selection": sorted(selection)}, sort_keys=True).encode()).hexdigest()[:12]
        pid = f"{assembly}__{sig}"
        folder = PROJECTS / pid
        if folder.exists():
            if pid in FLAGS:
                FLAGS[pid]["cancel"] = True
                FLAGS.pop(pid, None)
            _safe_clean_dir(folder)
        folder.mkdir(parents=True, exist_ok=True)

        species = data.get("species") or (metadata.get("species") if metadata else "Unknown") or "Unknown"

        manifest = {
            "project_id": pid,
            "assembly_key": assembly,
            "analysis_version": pid.rsplit("__", 1)[-1],
            "project_path": str(folder),
            "source": "ncbi",
            "repository_owner": "shane",
            "visibility": {"gregori": True, "shane": True, "ehab": False},
            "input_paths": [],
            "species": species,
            "parameters": params,
            "input_summary": {"file_count": 1, "sequence_count": len(selection), "total_bases": 0, "total_mb": 0},
            "limits": limits,
            "selected_sequences": selection,
            "gff3": custom_gene_map,
            "sequence_report": data.get("sequence_report"),
            "metadata": metadata or {},
            "status": "queued",
            "created_utc": utc_now(),
            "updated_utc": utc_now(),
            "outputs": {},
        }
        write_manifest(pid, manifest)
        write_card(pid, {
            "project_id": pid,
            "assembly_key": assembly,
            "species": species,
            "category": "gregori",
            "status": "queued",
            "created_utc": utc_now(),
            "updated_utc": utc_now(),
            "total_bases": 0,
            "completed_bases": 0,
            "percent_complete": 0.0,
            "sequences_total": len(selection),
            "sequences_completed": 0,
            "current_sequence": None,
            "shanes_discovered": 0,
            "genes_superimposed": None,
            "gene_discovery_status": "not_run",
            "color_state": "gray",
            "parameters": params,
        })
        FLAGS[pid] = {"pause": False, "cancel": False}
        if launch:
            threading.Thread(target=execute_worker, args=(pid,), daemon=True).start()
        return manifest

    report = inspect_sequences(data.get("input_paths", []), limits)
    if not report["valid"]:
        raise ValueError("; ".join(report["violations"]) or "No readable FASTA sequences found.")

    assembly, pid = determine_project_identity(report, params, data.get("assembly_key"), selection)
    folder = PROJECTS / pid

    if folder.exists():
        if pid in FLAGS:
            FLAGS[pid]["cancel"] = True
            FLAGS.pop(pid, None)
        _safe_clean_dir(folder)
    folder.mkdir(parents=True, exist_ok=True)

    detected = ", ".join(x for x in report["species"] if x != "Unknown") or "Unknown"
    species = detected if data.get("use_referenced_species", True) else data.get("species") or "Unknown"

    manifest = {
        "project_id": pid,
        "assembly_key": assembly,
        "analysis_version": pid.rsplit("__", 1)[-1],
        "project_path": str(folder),
        "source": source,
        "repository_owner": "shane",
        "visibility": {"gregori": True, "shane": True, "ehab": False},
        "input_paths": report["files"],
        "species": species,
        "parameters": params,
        "input_summary": {k: report[k] for k in ("file_count", "sequence_count", "total_bases", "total_mb")},
        "limits": limits,
        "selected_sequences": selection,
        "gff3": custom_gene_map,
        "metadata": metadata or {},
        "status": "queued",
        "created_utc": utc_now(),
        "updated_utc": utc_now(),
        "outputs": {},
    }

    write_manifest(pid, manifest)
    write_card(pid, {
        "project_id": pid,
        "assembly_key": assembly,
        "species": species,
        "category": "gregori",
        "status": "queued",
        "created_utc": utc_now(),
        "updated_utc": utc_now(),
        "total_bases": report["total_bases"],
        "completed_bases": 0,
        "percent_complete": 0.0,
        "sequences_total": report["sequence_count"],
        "sequences_completed": 0,
        "current_sequence": None,
        "shanes_discovered": 0,
        "genes_superimposed": None,
        "gene_discovery_status": "not_run",
        "color_state": "gray",
        "parameters": params,
    })
    FLAGS[pid] = {"pause": False, "cancel": False}
    if launch:
        threading.Thread(target=execute_worker, args=(pid,), daemon=True).start()
    return manifest


def execute_worker(pid: str):
    """Worker process executing pure GReGOrI discovery analysis with live card tracking."""
    manifest = read_manifest(pid)
    control = Control(pid)
    update_manifest(pid, status="analysing")
    update_card(pid, status="analysing", color_state="gray")
    root = Path(__file__).resolve().parents[2]

    try:
        # If NCBI source and fasta is not yet downloaded, download now
        if manifest.get("source") == "ncbi" and not manifest.get("input_paths"):
            accession = manifest["assembly_key"]
            update_manifest(pid, status="downloading")
            update_card(pid, status="downloading", color_state="gray")
            emit_event(pid, "download_started", accession=accession, percent=2, message=f"Downloading NCBI package for {accession}...")
            pkg = download_ncbi_package(accession, CACHE)
            manifest["input_paths"] = [pkg["fasta"]]
            manifest["gff3"] = manifest.get("gff3") or pkg.get("gff3")
            manifest["sequence_report"] = manifest.get("sequence_report") or pkg.get("sequence_report")
            update_manifest(pid, status="analysing", input_paths=manifest["input_paths"], gff3=manifest["gff3"], sequence_report=manifest["sequence_report"])
            update_card(pid, status="analysing", color_state="gray")
            emit_event(pid, "download_complete", accession=accession, percent=5)

        selected = set(manifest.get("selected_sequences") or [])
        records_list = []
        for fpath in map(Path, manifest["input_paths"]):
            for header, sequence in records(fpath):
                acc = accession_from_header(header)
                if selected and acc not in selected:
                    continue
                records_list.append((header, sequence, acc))

        if not records_list:
            raise ValueError("No sequence records matched the selection.")

        total_bases = sum(len(x[1]) for x in records_list)
        done_bases = 0
        all_results = []
        all_shanes_count = 0

        # Load sequence report if available
        seq_report_path = manifest.get("sequence_report")
        seq_map = load_seq_report(seq_report_path) if seq_report_path and Path(seq_report_path).is_file() else {}

        emit_event(pid, "job_started", sequence_count=len(records_list), total_bases=total_bases)
        update_card(pid, total_bases=total_bases, sequences_total=len(records_list), sequences_completed=0)

        for index, (header, sequence, acc) in enumerate(records_list, 1):
            control.safe_point({"phase": "before_sequence", "sequence_index": index})
            chrom = acc

            # Resolve sequence metadata
            seqmeta = seq_map.get(acc) or fallback_seq_record(header, acc)
            chrom_group = seqmeta.get("chromosome_group", "Other sequences")
            display_name = seqmeta.get("display_name", acc)

            emit_event(
                pid, "sequence_started",
                sequence_index=index, sequence_count=len(records_list),
                chromosome=chrom, sequence_length=len(sequence),
                completed_bases=done_bases, total_bases=total_bases,
            )

            last_card_emit = 0.0

            def on_worker_emit(event: str, **d: Any):
                nonlocal last_card_emit
                emit_event(pid, event, **d)
                if event == "scan_progress":
                    completed = d.get("completed_bases", done_bases)
                    pct = d.get("percent", 0.0)
                    now_t = time.time()
                    if now_t - last_card_emit >= 0.25 or pct >= 100.0:
                        last_card_emit = now_t
                        update_card(
                            pid,
                            total_bases=total_bases,
                            completed_bases=completed,
                            percent_complete=pct,
                            sequences_total=len(records_list),
                            sequences_completed=index - 1,
                            current_sequence=display_name,
                            shanes_discovered=all_shanes_count,
                        )

            # Stage 1: Pure SHaNE discovery analysis (NO gene discovery during GReGOrI scan)
            hits, shanes = analyse_sequence(
                sequence,
                step=manifest["parameters"]["step"],
                lookahead=manifest["parameters"]["lookahead"],
                threshold=manifest["parameters"]["threshold"],
                control=control,
                emit=on_worker_emit,
                base_done=done_bases,
                total_bases=total_bases,
                seq_index=index,
                seq_total=len(records_list),
            )

            for s in shanes:
                s["systematic_name"] = legacy_name(manifest.get("species", "Unknown"), display_name, s["start"])
                s["barcode_id"] = barcode(manifest.get("assembly_key"), acc, s["start"], s["end"])
                body = sequence[s["start"]:s["end"]]
                valid_bases = sum(body.count(x) for x in ("A", "C", "G", "T", "a", "c", "g", "t"))
                s["gc_content_percent"] = 100.0 * (body.count("G") + body.count("C") + body.count("g") + body.count("c")) / valid_bases if valid_bases else 0.0

            # Write outputs for this chromosome (computes maximized score and void lengths)
            safe_chrom = re.sub(r'[^A-Za-z0-9_.-]', '_', chrom).strip('._') or f"seq_{index}"
            chrom_out = PROJECTS / pid / "analysis" / safe_chrom
            write_outputs(chrom_out, chrom, sequence, shanes, manifest["parameters"].get("context_flank", 500))

            done_bases += len(sequence)
            all_shanes_count += len(shanes)
            pct_done = (done_bases / total_bases * 100) if total_bases else 100.0

            update_card(
                pid,
                total_bases=total_bases,
                completed_bases=done_bases,
                percent_complete=pct_done,
                sequences_total=len(records_list),
                sequences_completed=index,
                current_sequence=display_name,
                shanes_discovered=all_shanes_count,
            )

            all_results.append({
                "chromosome": chrom_group,
                "display_name": display_name,
                "accession": acc,
                "length_bp": len(sequence),
                "shanes": shanes,
                "raw_hits": len(hits),
            })

            emit_event(
                pid, "sequence_complete",
                sequence_index=index, sequence_count=len(records_list),
                chromosome=chrom, completed_bases=done_bases,
                total_bases=total_bases, percent=pct_done,
                shanes_identified=all_shanes_count,
            )
        # Build Rich Library JSON and Browser
        manifest = read_manifest(pid)
        library_path = build_library(manifest, all_results, sequence_map=seq_map)

        # Automatic Gene Discovery / Superimposition across all available GFF3 / GFF sources
        gene_count, gff3_path = auto_superimpose_genes_for_project(pid, manifest, library_path)

        browser_page = build_browser(root, library_path, root / "frontend" / "assets" / "SHaNE.png")

        outputs = {
            "analysis": str(PROJECTS / pid / "analysis"),
            "central_library": str(library_path),
            "browser_entry": str(browser_page),
        }

        update_manifest(
            pid,
            status="complete",
            completed_utc=utc_now(),
            summary={
                "sequences": len(records_list),
                "shanes": all_shanes_count,
                "genome_size_bp": total_bases,
                "genes_crossed": gene_count,
            },
            chromosomes=[{"accession": r["accession"], "length_bp": r["length_bp"], "shanes": len(r["shanes"])} for r in all_results],
            outputs=outputs,
        )

        update_card(
            pid,
            category="shane",
            status="complete",
            total_bases=total_bases,
            completed_bases=total_bases,
            percent_complete=100.0,
            sequences_total=len(records_list),
            sequences_completed=len(records_list),
            current_sequence=None,
            shanes_discovered=all_shanes_count,
            genes_superimposed=gene_count if gene_count > 0 else (0 if gff3_path else None),
            gene_discovery_status="completed" if gene_count > 0 else ("no_overlap" if gff3_path else "not_run"),
            color_state="neon_blue",
        )

        emit_event(pid, "job_complete", total_bases=total_bases, shanes=all_shanes_count, genes_crossed=gene_count)

    except InterruptedError:
        update_manifest(pid, status="cancelled")
        update_card(pid, status="cancelled", color_state="gray")
        emit_event(pid, "job_cancelled")
    except Exception as exc:
        update_manifest(pid, status="failed", error=str(exc))
        update_card(pid, status="failed", color_state="gray")
        emit_event(pid, "job_failed", error=str(exc), traceback=traceback.format_exc())


def parse_header_offset(header_or_name: str) -> tuple[str, int, int]:
    """Extract sequence accession and 1-based start/end coordinate offsets from header or filename."""
    m = re.search(r"(?:ref\||gi\|\d+\|)?([A-Za-z0-9_.-]+)(?:\|)?[:\[\(](\d+)[.\-]+(\d+)", header_or_name)
    if m:
        acc = m.group(1).rstrip(":._")
        start_offset = int(m.group(2))
        end_offset = int(m.group(3))
        return acc, start_offset, end_offset
    return header_or_name, 0, 0


def find_gff3_for_run(manifest: dict[str, Any], project_folder: Path, target_accs: list[str]) -> Path | None:
    """Intelligently locate matching GFF/GFF3 annotation file across manifest, assembly cache, project, or CACHE."""
    # 1. Direct path in manifest
    gff = manifest.get("gff3")
    if gff and Path(gff).is_file():
        return Path(gff)

    # 2. Check assembly cache folder
    ass_key = manifest.get("assembly_key") or manifest.get("assembly_accession")
    if ass_key:
        cache_sub = CACHE / ass_key
        if cache_sub.exists():
            cands = list(cache_sub.rglob("*.gff")) + list(cache_sub.rglob("*.gff3")) + list(cache_sub.rglob("*.gff.gz")) + list(cache_sub.rglob("*.gff3.gz"))
            if cands:
                return cands[0]

    # 3. Check project folder
    proj_gffs = list(project_folder.rglob("*.gff")) + list(project_folder.rglob("*.gff3")) + list(project_folder.rglob("*.gff.gz")) + list(project_folder.rglob("*.gff3.gz"))
    if proj_gffs:
        return proj_gffs[0]

    # 4. Search across all CACHE directories for matching accession
    clean_accs = {a.split(".")[0] for a in target_accs if a and len(a) > 2}
    for gff_path in CACHE.rglob("*"):
        if not gff_path.is_file() or not any(gff_path.name.lower().endswith(ext) for ext in (".gff", ".gff3", ".gff.gz", ".gff3.gz")):
            continue
        try:
            with open_text(gff_path) as handle:
                for _ in range(200):
                    line = handle.readline()
                    if not line:
                        break
                    if any(c in line for c in clean_accs):
                        return gff_path
        except Exception:
            pass

    return None


def auto_superimpose_genes_for_project(pid: str, manifest: dict[str, Any], library_path: Path, custom_gff: str | Path | None = None) -> tuple[int, Path | None]:
    """Automatically find matching GFF, calculate chromosomal offsets, and superimpose genes onto SHaNEs."""
    if custom_gff:
        manifest["gff3"] = str(custom_gff)

    if not library_path.exists():
        return 0, None

    try:
        lib = json.loads(library_path.read_text(encoding="utf-8"))
    except Exception:
        return 0, None

    shanes = lib.get("shanes", [])
    target_accs = list({s.get("sequence_accession") for s in shanes if s.get("sequence_accession")})
    if not target_accs:
        target_accs = list({r.get("accession") for r in manifest.get("chromosomes", []) if r.get("accession")})

    gff3_path = Path(custom_gff) if custom_gff and Path(custom_gff).is_file() else find_gff3_for_run(manifest, PROJECTS / pid, target_accs)
    if not gff3_path or not Path(gff3_path).exists():
        return 0, None

    try:
        genes_by_chrom = load_gene_map(gff3_path)
    except Exception:
        return 0, None

    if not genes_by_chrom:
        return 0, None

    # Determine any coordinate offsets from filenames or headers
    offsets: dict[str, int] = {}
    for fpath in manifest.get("input_paths", []):
        p = Path(fpath)
        clean_acc, start_off, _ = parse_header_offset(p.name)
        if start_off > 0:
            offsets[clean_acc] = start_off
            offsets[p.stem] = start_off

    distinct_genes = set()
    species = manifest.get("species", "Unknown")

    for shane in shanes:
        acc = shane.get("sequence_accession", "")
        coords = shane.get("coordinates", {})
        s_start = coords.get("start", shane.get("start", 0))
        s_end = coords.get("end", shane.get("end", 0))

        offset = offsets.get(acc, 0)
        if offset == 0:
            clean_acc, start_off, _ = parse_header_offset(acc)
            offset = start_off
        else:
            clean_acc = acc

        genomic_start = s_start + (offset - 1 if offset > 0 else 0)
        genomic_end = s_end + (offset - 1 if offset > 0 else 0)

        # Retrieve genes on chromosome with flexible matching
        chr_genes = genes_by_chrom.get(acc) or genes_by_chrom.get(clean_acc)
        if not chr_genes:
            unver = clean_acc.split(".")[0]
            chr_genes = genes_by_chrom.get(unver)
            if not chr_genes:
                for k, v in genes_by_chrom.items():
                    if k.startswith(unver) or unver in k:
                        chr_genes = v
                        break
        chr_genes = chr_genes or []

        matched = find_overlapping_genes(chr_genes, genomic_start, genomic_end, species)
        shane["genes"] = matched
        shane["gene_count"] = len(matched)
        shane["annotation_status"] = "annotated" if matched else "no_gene_overlap"
        for g in matched:
            distinct_genes.add((acc, g["start"], g["end"], g.get("symbol", ".")))

    lib["annotation_audit"] = {"loaded": True, "gff3": str(gff3_path)}
    library_path.write_text(json.dumps(lib, indent=2), encoding="utf-8")
    manifest["gff3"] = str(gff3_path)
    return len(distinct_genes), gff3_path


def perform_project_action(action_or_pid: str, pid_or_action: str, **kwargs) -> dict[str, Any]:
    """Execute mutation action on run (pause, resume, cancel, restart, rerun, delete, superimpose-genes)."""
    known_actions = {"pause", "resume", "cancel", "restart", "rerun", "delete", "superimpose-genes", "delete-browser"}
    if action_or_pid in known_actions:
        action = action_or_pid
        pid = pid_or_action
    else:
        pid = action_or_pid
        action = pid_or_action
    if action == "pause":
        if pid in FLAGS:
            FLAGS[pid]["pause"] = True
        update_manifest(pid, status="pausing")
        update_card(pid, status="pausing")
        emit_event(pid, "job_pausing")
        return {"status": "pausing"}

    if action == "resume":
        if pid in FLAGS:
            FLAGS[pid]["pause"] = False
        update_manifest(pid, status="analysing")
        update_card(pid, status="analysing")
        emit_event(pid, "job_resumed")
        return {"status": "analysing"}

    if action == "cancel":
        if pid in FLAGS:
            FLAGS[pid]["cancel"] = True
        update_card(pid, status="cancelling")
        emit_event(pid, "job_cancelled")
        return update_manifest(pid, status="cancelling")

    if action in {"restart", "rerun"}:
        if pid.startswith("ehab_"):
            man = read_ehab_manifest(pid)
            if not man:
                raise ValueError(f"EHaB project '{pid}' not found.")
            for sub in ("analysis", "ehab_browser"):
                shutil.rmtree(EHAB_DIR / pid / sub, ignore_errors=True)
            (EHAB_DIR / pid / "events.jsonl").unlink(missing_ok=True)
            man.pop("error", None)
            man.pop("completed_utc", None)
            man["status"] = "queued"
            write_ehab_manifest(pid, man)

            write_card(pid, {
                "project_id": pid,
                "assembly_key": man.get("assembly_key", pid),
                "species": man.get("species", "Unknown"),
                "category": "ehab",
                "status": "queued",
                "created_utc": man.get("created_utc", utc_now()),
                "updated_utc": utc_now(),
                "total_bases": man.get("total_bases", 0),
                "completed_bases": 0,
                "percent_complete": 0.0,
                "sequences_total": len(man.get("selected_sequences", [])),
                "sequences_completed": 0,
                "current_sequence": None,
                "shanes_discovered": 0,
                "total_combinations": 60,
                "completed_combinations": 0,
                "optimal_parameters": None,
                "max_discovery_shanes": 0,
                "color_state": "gray",
            })

            FLAGS[pid] = {"pause": False, "cancel": False}
            threading.Thread(target=execute_ehab_worker, args=(pid,), daemon=True).start()
            return {"status": "queued"}

        manifest = read_manifest(pid)
        if not manifest:
            raise ValueError(f"Project '{pid}' not found.")

        for sub in ("analysis", "central_library", "ehab_browser_draft"):
            shutil.rmtree(PROJECTS / pid / sub, ignore_errors=True)

        (PROJECTS / pid / "events.jsonl").unlink(missing_ok=True)

        manifest.pop("error", None)
        manifest.pop("completed_utc", None)
        manifest["outputs"] = {}
        manifest["summary"] = {}
        manifest["status"] = "queued"
        write_manifest(pid, manifest)

        total_bases = manifest.get("input_summary", {}).get("total_bases", 0)
        seq_count = manifest.get("input_summary", {}).get("sequence_count", len(manifest.get("selected_sequences", [])))
        write_card(pid, {
            "project_id": pid,
            "assembly_key": manifest.get("assembly_key", pid),
            "species": manifest.get("species", "Unknown"),
            "category": "gregori",
            "status": "queued",
            "created_utc": manifest.get("created_utc", utc_now()),
            "updated_utc": utc_now(),
            "total_bases": total_bases,
            "completed_bases": 0,
            "percent_complete": 0.0,
            "sequences_total": seq_count,
            "sequences_completed": 0,
            "current_sequence": None,
            "shanes_discovered": 0,
            "genes_superimposed": None,
            "gene_discovery_status": "not_run",
            "color_state": "gray",
            "parameters": manifest.get("parameters", {}),
        })

        FLAGS[pid] = {"pause": False, "cancel": False}
        threading.Thread(target=execute_worker, args=(pid,), daemon=True).start()
        return {"status": "queued"}

    if action == "delete":
        if pid in FLAGS:
            FLAGS[pid]["cancel"] = True
            FLAGS.pop(pid, None)
        proj_dir = PROJECTS / pid if (PROJECTS / pid).exists() else EHAB_DIR / pid
        _safe_clean_dir(proj_dir)
        return {"deleted": pid}

    if action == "superimpose-genes":
        manifest = read_manifest(pid)
        lib_path = PROJECTS / pid / "central_library" / "GReGOrI_SHaNE_library.json"
        if not lib_path.exists():
            raise ValueError("Project library has not been generated yet.")

        gene_count, gff3_path = auto_superimpose_genes_for_project(pid, manifest, lib_path, custom_gff=kwargs.get("gff3"))
        if not gff3_path:
            raise ValueError("No GFF3 gene annotation file found for this project.")

        root = Path(__file__).resolve().parents[2]
        browser_page = build_browser(root, lib_path, root / "frontend" / "assets" / "SHaNE.png")

        summary = manifest.get("summary", {})
        summary["genes_crossed"] = gene_count
        manifest["summary"] = summary
        manifest["gff3"] = str(gff3_path)
        write_manifest(pid, manifest)

        update_card(
            pid,
            genes_superimposed=gene_count,
            gene_discovery_status="completed" if gene_count > 0 else "no_overlap",
        )

        manifest["card"] = read_card(pid)
        emit_event(pid, "genes_superimposed", genes_crossed=gene_count)
        return manifest

    raise ValueError(f"Unknown project action '{action}'")


# Alias for app.py endpoints
mutate_project = perform_project_action


def create_ehab_job(
    data: dict[str, Any],
    source: str = "ncbi",
    metadata: dict[str, Any] | None = None,
    launch: bool = True,
) -> dict[str, Any]:
    """Create an EHaB 60-parameter Efficiency Injection job."""
    EHAB_DIR.mkdir(parents=True, exist_ok=True)
    selection = data.get("selected_sequences") or []
    assembly = data.get("assembly_key") or data.get("accession") or "CUSTOM_EHAB"
    
    sig_payload = {"assembly": assembly, "selection": sorted(selection), "source": source, "t": int(time.time() * 1000)}
    sig = hashlib.sha256(json.dumps(sig_payload, sort_keys=True).encode()).hexdigest()[:10]
    pid = f"EHAB__{assembly}__{sig}"
    folder = EHAB_DIR / pid
    folder.mkdir(parents=True, exist_ok=True)

    species = data.get("species") or (metadata.get("species") if metadata else "Unknown") or "Unknown"

    manifest = {
        "project_id": pid,
        "assembly_key": assembly,
        "species": species,
        "source": source,
        "category": "ehab",
        "repository_owner": "ehab",
        "project_path": str(folder),
        "input_paths": data.get("input_paths") or [],
        "selected_sequences": selection,
        "metadata": metadata or {},
        "status": "queued",
        "color_state": "gray",
        "total_combinations": 60,
        "completed_combinations": 0,
        "created_utc": utc_now(),
        "updated_utc": utc_now(),
        "outputs": {},
    }

    write_ehab_manifest(pid, manifest)
    write_ehab_card(pid, {
        "project_id": pid,
        "assembly_key": assembly,
        "species": species,
        "category": "ehab",
        "status": "queued",
        "color_state": "gray",
        "created_utc": utc_now(),
        "updated_utc": utc_now(),
        "percent_complete": 0.0,
        "total_combinations": 60,
        "completed_combinations": 0,
        "current_combination": None,
        "max_discovery_shanes": 0,
        "optimal_parameters": None,
        "sequences_total": len(selection),
        "sequences_completed": 0,
    })

    FLAGS[pid] = {"pause": False, "cancel": False}
    if launch:
        threading.Thread(target=execute_ehab_worker, args=(pid,), daemon=True).start()
    return manifest


def execute_ehab_worker(pid: str):
    """Execute EHaB 60-parameter permutation benchmark pipeline."""
    manifest = read_ehab_manifest(pid)
    control = Control(pid)
    update_ehab_manifest(pid, status="analysing")
    update_ehab_card(pid, status="analysing", color_state="gray")
    root = Path(__file__).resolve().parents[2]

    try:
        if manifest.get("source") == "ncbi" and not manifest.get("input_paths"):
            accession = manifest["assembly_key"]
            update_ehab_manifest(pid, status="downloading")
            update_ehab_card(pid, status="downloading", color_state="gray")
            pkg = download_ncbi_package(accession, CACHE)
            manifest["input_paths"] = [pkg["fasta"]]
            manifest["gff3"] = manifest.get("gff3") or pkg.get("gff3")
            manifest["sequence_report"] = manifest.get("sequence_report") or pkg.get("sequence_report")
            update_ehab_manifest(pid, status="analysing", input_paths=manifest["input_paths"], gff3=manifest["gff3"], sequence_report=manifest["sequence_report"])
            update_ehab_card(pid, status="analysing", color_state="gray")

        selected = set(manifest.get("selected_sequences") or [])
        records_list = []
        for fpath in map(Path, manifest["input_paths"]):
            for header, sequence in records(fpath):
                acc = accession_from_header(header)
                if selected and acc not in selected:
                    continue
                records_list.append((header, sequence, acc))

        if not records_list:
            raise ValueError("No sequence records matched the selection for EHaB analysis.")

        seq_report_path = manifest.get("sequence_report")
        seq_map = load_seq_report(seq_report_path) if seq_report_path and Path(seq_report_path).is_file() else {}

        from ..engine.ehab_grid import run_ehab_sequence_eval, get_ehab_60_permutations
        permutations = get_ehab_60_permutations()

        combined_runs = {p["index"]: {
            "index": p["index"],
            "tag": p["tag"],
            "label": p["label"],
            "parameters": {"step": p["step"], "threshold": p["threshold"], "lookahead": p["lookahead"]},
            "raw_hits": 0,
            "shanes_count": 0,
            "island_count": 0,
            "total_shane_length_bp": 0,
            "total_island_length_bp": 0,
            "shanes": [],
            "chromosome_summary": {},
        } for p in permutations}

        total_seqs = len(records_list)
        total_steps_eval = total_seqs * 60
        step_counter = 0

        for s_idx, (header, sequence, acc) in enumerate(records_list, 1):
            seqmeta = seq_map.get(acc) or fallback_seq_record(header, acc)
            chrom_group = seqmeta.get("chromosome_group", "Other sequences")
            display_name = seqmeta.get("display_name", acc)
            species = manifest.get("species", "Unknown")

            def on_eval_progress(cur_idx, total_perms, perm_info, run_summary):
                nonlocal step_counter
                step_counter += 1
                pct = (step_counter / total_steps_eval) * 100
                update_ehab_card(
                    pid,
                    percent_complete=round(pct, 1),
                    completed_combinations=cur_idx,
                    current_sequence=display_name,
                    current_combination=perm_info,
                )

            seq_evals = run_ehab_sequence_eval(
                sequence=sequence,
                species=species,
                chrom_display=display_name,
                accession=acc,
                on_progress=on_eval_progress,
                control=control,
            )

            for res in seq_evals:
                idx = res["index"]
                target = combined_runs[idx]
                target["raw_hits"] += res["raw_hits"]
                target["shanes_count"] += res["shanes_count"]
                target["island_count"] += res["island_count"]
                target["total_shane_length_bp"] += res["total_shane_length_bp"]
                target["total_island_length_bp"] += res["total_island_length_bp"]
                target["shanes"].extend(res["shanes"])
                target["chromosome_summary"][display_name] = {
                    "chromosome_group": chrom_group,
                    "length_bp": len(sequence),
                    "shanes_count": res["shanes_count"],
                    "island_count": res["island_count"],
                    "total_island_length_bp": res["total_island_length_bp"],
                }

        import statistics
        final_runs_list = list(combined_runs.values())
        for r in final_runs_list:
            lens = [s.get("end", 0) - s.get("start", 0) for s in r["shanes"]]
            r["mean_shane_length_bp"] = round(statistics.fmean(lens), 1) if lens else 0
            r["median_shane_length_bp"] = round(statistics.median(lens), 1) if lens else 0

        peak_run = max(final_runs_list, key=lambda x: (x["shanes_count"], x["total_island_length_bp"])) if final_runs_list else None

        from ..engine.ehab_grid import cluster_ehab_shanes
        seq_map_for_homology = {acc: seq for _, seq, acc in records_list}
        clustering_res = cluster_ehab_shanes(final_runs_list, sequence_map=seq_map_for_homology)
        lineages = clustering_res["lineages"]
        combined_shanes = clustering_res["combined_shanes"]

        ehab_folder = EHAB_DIR / pid
        lib_payload = {
            "format": "GReGOrI-EHaB-Comparison-Library",
            "version": "4.2",
            "generated_utc": utc_now(),
            "project_id": pid,
            "assembly_key": manifest.get("assembly_key"),
            "species": manifest.get("species"),
            "sequence_records": [{"display_name": acc, "length_bp": len(seq)} for _, seq, acc in records_list],
            "total_permutations": 60,
            "distinct_lineages_count": len(lineages),
            "combined_shanes_count": len(combined_shanes),
            "lineages": lineages,
            "combined_shanes": combined_shanes,
            "connected_loci": lineages,  # backward-compatible
            "peak_optimal_run": {
                "index": peak_run["index"] if peak_run else 1,
                "tag": peak_run["tag"] if peak_run else "",
                "parameters": peak_run["parameters"] if peak_run else {},
                "max_shanes": peak_run["shanes_count"] if peak_run else 0,
                "total_island_length_bp": peak_run["total_island_length_bp"] if peak_run else 0,
            } if peak_run else None,
            "runs": final_runs_list,
        }

        lib_file = ehab_folder / "EHaB_comparison_library.json"
        lib_file.write_text(json.dumps(lib_payload, indent=2), encoding="utf-8")

        browser_dir = ehab_folder / "ehab_browser"
        browser_dir.mkdir(parents=True, exist_ok=True)
        browser_html = browser_dir / "index.html"

        from ..browser.EHaB_browser_builder import build_ehab_browser
        logo_path = root / "frontend" / "assets" / "EHaB.png"
        build_ehab_browser(lib_payload, browser_html, logo_path)

        manifest["status"] = "complete"
        manifest["outputs"] = {
            "ehab_library": str(lib_file),
            "browser_entry": str(browser_html),
        }
        manifest["completed_utc"] = utc_now()
        manifest["peak_run"] = lib_payload["peak_optimal_run"]
        manifest["distinct_lineages_count"] = len(lineages)
        manifest["combined_shanes_count"] = len(combined_shanes)
        write_ehab_manifest(pid, manifest)

        update_ehab_card(
            pid,
            status="complete",
            color_state="gold",
            percent_complete=100.0,
            completed_combinations=60,
            max_discovery_shanes=len(lineages) or (peak_run["shanes_count"] if peak_run else 0),
            optimal_parameters=peak_run["parameters"] if peak_run else None,
            browser_entry=f"/managed_ehab/{pid}/ehab_browser/index.html",
        )
    except Exception as exc:
        traceback.print_exc()
        update_ehab_manifest(pid, status="failed", error=str(exc))
        update_ehab_card(pid, status="failed", color_state="red", error=str(exc))
