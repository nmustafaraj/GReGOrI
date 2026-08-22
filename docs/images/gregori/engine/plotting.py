"""Matplotlib-based locus and chromosome overview plotting with graceful fallback."""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def is_plotting_available() -> bool:
    """Static matplotlib image generation is disabled during real-time scan for maximum engine speed."""
    return False


def save_visualizations(
    sequence: str,
    shanes: list[dict[str, Any]],
    output_dir: str | Path,
    chrom: str,
) -> None:
    """Render chromosome overview distribution and per-locus locus diagrams."""
    if plt is None:
        return

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Chromosome Overview Plot
    fig, ax = plt.subplots(figsize=(16, 2.4))
    ax.hlines(0, 0, len(sequence), color="black", linewidth=1.5)
    if shanes:
        ax.vlines([s["start"] for s in shanes], -0.5, 0.5, color="#d946ef", linewidth=2)
    ax.set_title(f"GReGOrI - SHaNE distribution - {chrom}", fontweight="bold")
    ax.set_xlabel("Genomic coordinate (bp; 0-based)")
    ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(out_path / "chromosome_overview.png", dpi=220)
    fig.savefig(out_path / "chromosome_overview.svg")
    plt.close(fig)

    # 2. Loci plots with superimposed gene tracks
    loci = out_path / "loci"
    loci.mkdir(exist_ok=True)
    for index, shane in enumerate(shanes, 1):
        left = max(0, shane["start"] - 2000)
        right = min(len(sequence), shane["end"] + 2000)
        genes = shane.get("genes", [])
        has_genes = bool(genes)

        fig, ax = plt.subplots(figsize=(14, 3.6 if has_genes else 3.0))
        ax.hlines(0, left, right, color="#cbd5e1", linewidth=7)
        ax.broken_barh([(shane["start"], shane["end"] - shane["start"])], (-0.15, 0.3), facecolors="#22d3ee")

        # Plot 5' and 3' island arms
        for island in shane.get("islands", []):
            ax.broken_barh([(island["s_start"], island["s_end"] - island["s_start"])], (0.18, 0.22), facecolors="#d946ef")
            ax.broken_barh([(island["h_start"], island["h_end"] - island["h_start"])], (-0.40, 0.22), facecolors="#8b5cf6")

        # Plot Superimposed Genes
        if has_genes:
            for g in genes:
                g_start = max(left, int(g.get("genomic_start", g.get("start", shane["start"]))))
                g_end = min(right, int(g.get("genomic_end", g.get("end", shane["end"]))))
                if g_end > g_start:
                    ax.broken_barh([(g_start, g_end - g_start)], (0.45, 0.18), facecolors="#10b981", edgecolors="#047857", linewidth=1.2)
                    sym = g.get("symbol") or g.get("feature_id") or "gene"
                    ax.text((g_start + g_end) / 2, 0.54, f"{sym} ({g.get('strand','+')})", ha="center", va="center", color="#064e3b", fontsize=9, fontweight="bold")

            ax.set_ylim(-0.65, 0.75)
            ax.set_yticks([0.54, 0.29, 0, -0.29])
            ax.set_yticklabels(["Genes", "5' islands", "SHaNE", "3' islands"])
        else:
            ax.set_ylim(-0.65, 0.65)
            ax.set_yticks([0.29, 0, -0.29])
            ax.set_yticklabels(["5' islands", "SHaNE", "3' islands"])

        ax.set_xlim(left, right)
        ax.set_xlabel("Genomic coordinate (bp; 0-based)")
        gene_str = f" | {len(genes)} gene(s) crossed" if has_genes else ""
        ax.set_title(f"SHaNE {index}: {shane['start']:,}-{shane['end']:,} bp | {len(shane.get('islands', []))} island(s){gene_str}", fontweight="bold")
        fig.tight_layout()
        fig.savefig(loci / f"SHaNE_{index}_locus.png", dpi=220)
        fig.savefig(loci / f"SHaNE_{index}_locus.svg")
        plt.close(fig)
