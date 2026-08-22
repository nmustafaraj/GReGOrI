"""Whole-genome batch processing pipeline and standalone discovery manager."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .alignment import get_reverse_complement, similarity
from .core import (
    analyse_sequence,
    enrich_shane_details,
    open_fasta,
    records,
    write_outputs,
)
from .plotting import save_visualizations
from .terminal import Spinner, interactive_terminal_inspect, print_progress


def run_single_sequence_pipeline(
    fasta_path: str | Path,
    output_dir: str | Path,
    species: str = "Unknown",
    step: int = 1000,
    lookahead: int = 20000,
    threshold: float = 0.99,
    context_flank: int = 500,
    generate_plots: bool = True,
    inspect_interactive: bool = False,
) -> dict[str, Any]:
    """Execute complete analysis on a single chromosome/sequence FASTA."""
    fasta_p = Path(fasta_path).expanduser().resolve()
    out_p = Path(output_dir).expanduser().resolve()
    out_p.mkdir(parents=True, exist_ok=True)

    seq_records = list(records(fasta_p))
    if not seq_records:
        raise ValueError(f"No FASTA records found in {fasta_path}")

    header, sequence = seq_records[0]
    chrom = fasta_p.stem

    with Spinner(f"Scanning {chrom} ({len(sequence):,} bp)..."):
        hits, shanes = analyse_sequence(
            sequence,
            step=step,
            lookahead=lookahead,
            threshold=threshold,
        )

    for idx, shane in enumerate(shanes, 1):
        shane["systematic_name"] = f"{species[:2].capitalize()}_SHaNE_{chrom}.{shane['start']//100000}"
        enrich_shane_details(sequence, shane, context_flank)

    write_outputs(out_p, chrom, sequence, shanes, context_flank)

    if generate_plots:
        save_visualizations(sequence, shanes, out_p, chrom)

    summary = {
        "chromosome": chrom,
        "header": header,
        "length_bp": len(sequence),
        "raw_hits": len(hits),
        "shanes_count": len(shanes),
        "shanes": shanes,
        "output_directory": str(out_p),
    }

    (out_p / "chromosome_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if inspect_interactive:
        interactive_terminal_inspect(sequence, shanes, chrom)

    return summary


def run_whole_genome_batch_pipeline(
    fasta_paths: list[str | Path],
    output_dir: str | Path,
    species: str = "Unknown",
    step: int = 1000,
    lookahead: int = 20000,
    threshold: float = 0.99,
    context_flank: int = 500,
    generate_plots: bool = True,
) -> dict[str, Any]:
    """Run batch analysis across multiple chromosomes."""
    out_p = Path(output_dir).expanduser().resolve()
    out_p.mkdir(parents=True, exist_ok=True)

    all_results = []
    total_shanes = 0
    total_bases = 0

    for idx, fpath in enumerate(fasta_paths, 1):
        p = Path(fpath)
        chrom_out = out_p / p.stem
        res = run_single_sequence_pipeline(
            p,
            chrom_out,
            species=species,
            step=step,
            lookahead=lookahead,
            threshold=threshold,
            context_flank=context_flank,
            generate_plots=generate_plots,
            inspect_interactive=False,
        )
        all_results.append(res)
        total_shanes += res["shanes_count"]
        total_bases += res["length_bp"]
        print_progress(idx, len(fasta_paths), f"Completed {p.name}: {res['shanes_count']} SHaNEs")

    manifest = {
        "species": species,
        "total_chromosomes": len(fasta_paths),
        "total_bases": total_bases,
        "total_shanes": total_shanes,
        "chromosomes": all_results,
    }
    (out_p / "genome_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
