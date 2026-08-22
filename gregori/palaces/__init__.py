"""GReGOrI Palaces Enterprise Architecture."""
from __future__ import annotations

from .browser_quality import apply as apply_browser_quality
from .identity import stable_id
from .naming import barcode, legacy_name
from .regression import compare as compare_tracks
from .rich_library import build as build_rich_library
from .science_gate import run as run_science_gate
from .sequence_report import fallback as fallback_seq_record, load as load_seq_report
from .validate import validate as validate_library
