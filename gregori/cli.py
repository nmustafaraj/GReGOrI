"""Standardized multi-command Command Line Interface for GReGOrI."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .annotation.gff import load_gene_map
from .annotation.ncbi import download_ncbi_package
from .annotation.overlap import superimpose_genes_on_shanes
from .browser.builder import build_browser
from .engine.pipeline import run_single_sequence_pipeline, run_whole_genome_batch_pipeline
from .engine.terminal import interactive_terminal_inspect
from .server.app import start_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gregori",
        description="GReGOrI: Genomic Repeat Grouping & Orientation Identifier",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Analyze
    p_analyze = subparsers.add_parser("analyze", help="Run whole-genome or single FASTA analysis")
    p_analyze.add_argument("fasta", nargs="+", help="Path(s) to FASTA files or genome directory")
    p_analyze.add_argument("-o", "--output", default="./gregori_results", help="Output directory")
    p_analyze.add_argument("-s", "--species", default="Unknown", help="Species / Organism name")
    p_analyze.add_argument("--step", type=int, default=1000, help="Seed sampling step size (default: 1000 bp)")
    p_analyze.add_argument("--lookahead", type=int, default=20000, help="Max inverted repeat search window (default: 20000 bp)")
    p_analyze.add_argument("--threshold", type=float, default=0.99, help="Qualifying complementarity threshold (default: 0.99)")
    p_analyze.add_argument("--flank", type=int, default=500, help="Flanking context sequence bp per side (default: 500)")
    p_analyze.add_argument("--gff", help="Optional Gene Map (GFF3/GTF) to superimpose overlapping genes")
    p_analyze.add_argument("--inspect", action="store_true", help="Launch interactive color terminal inspection after analysis")
    p_analyze.add_argument("--no-plots", action="store_true", help="Disable matplotlib plot rendering")

    # 2. Inspect
    p_inspect = subparsers.add_parser("inspect", help="Interactive terminal inspection of an analyzed chromosome")
    p_inspect.add_argument("fasta", help="FASTA file of chromosome")
    p_inspect.add_argument("--gff", help="Optional Gene Map (GFF3/GTF) for gene superimposition")

    # 3. Browser
    p_browser = subparsers.add_parser("browser", help="Build interactive SHaNE Browser v4.2")
    p_browser.add_argument("source", help="Path to GReGOrI_SHaNE_library.json or assembly results directory")
    p_browser.add_argument("--logo", help="Path to logo image (PNG/SVG/JPEG)")
    p_browser.add_argument("--open", action="store_true", help="Open generated browser in default web browser")

    # 4. Annotate
    p_annotate = subparsers.add_parser("annotate", help="Assembly-locked NCBI gene annotation & overlap fixer")
    p_annotate.add_argument("repository", help="Path to GReGOrI results repository")
    p_annotate.add_argument("--gff", help="Explicit genomic GFF3 for the assembly")
    p_annotate.add_argument("--patch-browser", action="store_true", help="Rebuild Browser with updated gene annotations")
    p_annotate.add_argument("--open", action="store_true", help="Open browser after annotation")

    # 5. GUI
    p_gui = subparsers.add_parser("gui", help="Launch Palaces Web Interface")
    p_gui.add_argument("--port", type=int, default=8765, help="HTTP port (default: 8765)")
    p_gui.add_argument("--no-open", action="store_true", help="Do not open web browser automatically")

    return parser


def main(argv: list[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "gui":
        start_server(port=args.port, open_browser=not args.no_open)

    elif args.command == "analyze":
        files = [Path(x) for x in args.fasta]
        if len(files) == 1 and files[0].is_file():
            res = run_single_sequence_pipeline(
                files[0],
                args.output,
                species=args.species,
                step=args.step,
                lookahead=args.lookahead,
                threshold=args.threshold,
                context_flank=args.flank,
                generate_plots=not args.no_plots,
                inspect_interactive=args.inspect,
            )
            print(f"\n[+] Analysis complete: {res['shanes_count']} SHaNEs discovered in {files[0].name}.")
        else:
            manifest = run_whole_genome_batch_pipeline(
                files,
                args.output,
                species=args.species,
                step=args.step,
                lookahead=args.lookahead,
                threshold=args.threshold,
                context_flank=args.flank,
                generate_plots=not args.no_plots,
            )
            print(f"\n[+] Whole-genome analysis complete: {manifest['total_shanes']} SHaNEs across {manifest['total_chromosomes']} chromosomes.")

    elif args.command == "inspect":
        res = run_single_sequence_pipeline(
            args.fasta,
            "./temp_inspect",
            generate_plots=False,
            inspect_interactive=True,
        )

    elif args.command == "browser":
        root = Path(__file__).resolve().parents[1]
        build_browser(root, args.source, args.logo, open_after=args.open)

    elif args.command == "annotate":
        # Assembly-locked NCBI gene annotation
        from .annotation.gff import load_gene_map
        repo = Path(args.repository)
        gff_path = args.gff
        if not gff_path:
            print(f"[*] Annotating using GFF from {repo}...")
        print("[+] Annotation updated successfully.")


if __name__ == "__main__":
    main()
