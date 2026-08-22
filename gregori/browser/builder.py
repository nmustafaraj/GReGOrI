"""Unified SHaNE Browser v4.2 builder and orchestrator."""
from __future__ import annotations

import base64
import json
import mimetypes
import subprocess
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .bright_browser_theme import apply as apply_bright_theme
from ..palaces.browser_quality import apply as apply_browser_quality
from ..palaces.rich_library import build as build_rich_library

HERE = Path(__file__).resolve().parent


def build_library(
    project: dict[str, Any],
    records: list[dict[str, Any]],
    sequence_map: dict[str, Any] | None = None,
    annotation_audit: dict[str, Any] | None = None,
) -> Path:
    """Build standardized GReGOrI_SHaNE_library.json with Palaces rich model."""
    return build_rich_library(project, records, sequence_map, annotation_audit)


def build_browser(
    root: str | Path,
    library_path: str | Path,
    logo_path: str | Path | None = None,
    open_after: bool = False,
) -> Path:
    """Execute complete Browser v4.2 build pipeline."""
    library_p = Path(library_path).expanduser().resolve()
    repo = library_p.parent
    root_p = Path(root).expanduser().resolve()

    # If logo is not provided, use default SHaNE logo if present
    if not logo_path:
        default_logo = root_p / "frontend" / "assets" / "SHaNE.png"
        if default_logo.is_file():
            logo_path = default_logo

    logo_args = ["--logo", str(logo_path)] if logo_path and Path(logo_path).is_file() else []

    # 1. Base Builder
    builder_script = HERE / "GReGOrI_browser_builder.py"
    if not builder_script.exists():
        builder_script = HERE / "GReGOrI_browser_v4_builder.py"
    cmd_v4 = [sys.executable, str(builder_script), str(library_p), *logo_args]
    proc = subprocess.run(cmd_v4, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"SHaNE Browser build failed: {proc.stderr or proc.stdout}")

    # 2. Refiner
    refiner_script = HERE / "GReGOrI_browser_refiner.py"
    if not refiner_script.exists():
        refiner_script = HERE / "GReGOrI_browser_v4.1_refiner.py"
    cmd_v41 = [sys.executable, str(refiner_script), str(repo), *logo_args]
    proc = subprocess.run(cmd_v41, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"SHaNE Browser refinement failed: {proc.stderr or proc.stdout}")

    # 3. Finisher
    finisher_script = HERE / "GReGOrI_browser_finisher.py"
    if not finisher_script.exists():
        finisher_script = HERE / "GReGOrI_browser_v4.2_finisher.py"
    cmd_v42 = [sys.executable, str(finisher_script), str(repo)]
    proc = subprocess.run(cmd_v42, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"SHaNE Browser finish failed: {proc.stderr or proc.stdout}")

    page = repo / "browser_v4_2" / "index.html"
    if not page.is_file():
        raise RuntimeError("SHaNE Browser v4.2 completed without generating index.html")

    apply_bright_theme(page)
    apply_browser_quality(page)

    if open_after:
        webbrowser.open(page.as_uri())

    return page


def build_ehab_draft(
    root: str | Path,
    project_path: str | Path,
    logo_path: str | Path | None = None,
) -> Path:
    """Build EHaB interactive exploration draft browser."""
    root_p = Path(root).expanduser().resolve()
    proj_p = Path(project_path).expanduser().resolve()
    out = proj_p / "ehab_browser_draft"

    if not logo_path:
        default_logo = root_p / "frontend" / "assets" / "EHaB.png"
        if default_logo.is_file():
            logo_path = default_logo

    logo_args = ["--logo", str(logo_path)] if logo_path and Path(logo_path).is_file() else []
    builder_script = HERE / "EHaB_browser_draft_builder.py"

    cmd = [sys.executable, str(builder_script), str(proj_p), "--output", str(out), *logo_args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"EHaB draft build failed: {proc.stderr or proc.stdout}")

    page = out / "index.html"
    if not page.is_file():
        raise RuntimeError("EHaB draft completed without generating index.html")

    return page


def build_ehab_comparison_browser(
    library_data: dict[str, Any],
    output_path: str | Path,
    logo_path: str | Path | None = None,
) -> Path:
    """Build golden EHaB Comparative Browser from 60-run evaluation library."""
    from .EHaB_browser_builder import build_ehab_browser
    return build_ehab_browser(library_data, Path(output_path), Path(logo_path) if logo_path else None)
