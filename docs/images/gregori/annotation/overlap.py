"""Fast interval overlap analyzer and gene superimposition onto SHaNEs."""
from __future__ import annotations

import urllib.parse
from bisect import bisect_left
from typing import Any


def classify_overlap(shane_start: int, shane_end: int, gene_start: int, gene_end: int) -> tuple[int, int, int, str] | None:
    """Classify exact spatial interval relationship between a SHaNE and a gene."""
    overlap_start = max(shane_start, gene_start)
    overlap_end = min(shane_end, gene_end)
    overlap_bp = max(0, overlap_end - overlap_start)
    if overlap_bp == 0:
        return None
    if shane_start == gene_start and shane_end == gene_end:
        relationship = "same_boundaries"
    elif gene_start <= shane_start and gene_end >= shane_end:
        relationship = "SHaNE_contained_in_gene"
    elif shane_start <= gene_start and shane_end >= gene_end:
        relationship = "gene_contained_in_SHaNE"
    elif gene_start < shane_start < gene_end < shane_end:
        relationship = "partial_overlap_left"
    elif shane_start < gene_start < shane_end < gene_end:
        relationship = "partial_overlap_right"
    else:
        relationship = "partial_overlap"
    return overlap_start, overlap_end, overlap_bp, relationship


def find_overlapping_genes(
    seq_genes: list[dict[str, Any]],
    shane_start: int,
    shane_end: int,
    species: str = "Unknown",
) -> list[dict[str, Any]]:
    """Identify overlapping genes for a given SHaNE coordinate span with full legacy evidencing and deduplication."""
    overlaps = []
    if not seq_genes:
        return overlaps

    starts = [g["start"] for g in seq_genes]
    idx_max = bisect_left(starts, shane_end)
    seen_identities = set()

    for g in seq_genes[:idx_max]:
        ov = classify_overlap(shane_start, shane_end, g["start"], g["end"])
        if ov is None:
            continue
        overlap_start, overlap_end, overlap_len, rel = ov
        gid = g.get("gene_id")
        symbol = g.get("symbol") or g.get("locus_tag") or gid or "."
        
        # Deduplication check: prevent multi-annotation of the same gene for a single SHaNE
        dedup_id = gid if (gid and gid != ".") else symbol
        dedup_key = (dedup_id, g["start"], g["end"])
        if dedup_key in seen_identities:
            continue
        seen_identities.add(dedup_key)

        if gid and gid != "." and gid != "None":
            ncbi_url = f"https://www.ncbi.nlm.nih.gov/gene/{gid}"
        else:
            q = " ".join(x for x in [symbol, species] if x and x != ".")
            ncbi_url = "https://www.ncbi.nlm.nih.gov/gene/?term=" + urllib.parse.quote(q)

        strand = g.get("strand", "+")
        overlaps.append({
            "gene_id": gid or ".",
            "symbol": symbol,
            "locus_tag": g.get("locus_tag", "."),
            "feature_id": symbol,
            "biotype": g.get("biotype", "gene"),
            "strand": strand,
            "start": g["start"],
            "end": g["end"],
            "genomic_start": g["start"],
            "genomic_end": g["end"],
            "transcription_start": g.get("transcription_start", g["end"] - 1 if strand == "-" else g["start"]),
            "transcription_end": g.get("transcription_end", g["start"] if strand == "-" else g["end"] - 1),
            "overlap_start": overlap_start,
            "overlap_end": overlap_end,
            "overlap_bp": overlap_len,
            "relationship": rel,
            "description": g.get("description", "."),
            "dbxref": g.get("dbxref", "."),
            "ncbi_url": ncbi_url,
        })

    return overlaps


def superimpose_genes_on_shanes(
    shanes: list[dict[str, Any]],
    gene_map_by_chrom: dict[str, list[dict[str, Any]]],
    chrom: str,
    species: str = "Unknown",
) -> None:
    """Superimpose overlapping genes directly onto a list of discovered SHaNE objects."""
    seq_genes = gene_map_by_chrom.get(chrom, [])
    for shane in shanes:
        matched = find_overlapping_genes(seq_genes, shane["start"], shane["end"], species)
        shane["genes"] = matched
        shane["gene_count"] = len(matched)
        shane["annotation_status"] = "annotated" if matched else "no_gene_overlap"
