"""Direct-strand Homology & Repeated Arm Detection Engine for GReGOrI / EHaB.

Detects tandem duplications and repeated arms on the same strand/direction:
1. Every single 20-mer (step=1) is scanned against downstream sequence.
2. Grouping hits with flexible distance tolerance for deletions/insertions.
3. Bidirectional homology expansion.
4. Cross-referencing homologous regions with SHaNE island coordinates.
"""
from __future__ import annotations

from typing import Any


def calculate_homology_score(seq1: str, seq2: str) -> float:
    """Calculate direct sequence identity (same direction)."""
    if not seq1 or not seq2 or len(seq1) != len(seq2):
        return 0.0
    matches = sum(1 for a, b in zip(seq1, seq2) if a == b and a not in "Nn-.")
    return matches / len(seq1)


def scan_direct_homology_seeds(
    sequence: str,
    window_size: int = 20,
    step: int = 1,
    max_lookahead: int = 80000,
    min_distance: int = 25,
) -> list[dict[str, int]]:
    """Scan sequence for exact direct matching 20-bp seed pairs on the same strand (every 20-mer indexed)."""
    hits = []
    seq_len = len(sequence)
    kmer_map: dict[str, list[int]] = {}

    for i in range(0, seq_len - window_size + 1, step):
        kmer = sequence[i : i + window_size]
        if "N" in kmer:
            continue
        if kmer in kmer_map:
            for prev_pos in kmer_map[kmer]:
                dist = i - prev_pos
                if min_distance <= dist <= max_lookahead:
                    hits.append({
                        "pos1": prev_pos,
                        "pos2": i,
                        "distance": dist,
                    })
            kmer_map[kmer].append(i)
        else:
            kmer_map[kmer] = [i]

    return hits


def group_homology_hits(
    hits: list[dict[str, int]],
    distance_tolerance: int = 200,
    max_gap: int = 2500,
) -> list[list[dict[str, int]]]:
    """Group direct homology hits with flexible tolerance for deletions/insertions."""
    if not hits:
        return []

    sorted_hits = sorted(hits, key=lambda x: (x["pos1"], x["pos2"]))
    groups: list[list[dict[str, int]]] = []

    for hit in sorted_hits:
        placed = False
        for grp in groups:
            last = grp[-1]
            # Check if hit is downstream from last and has matching shift distance within deletion tolerance
            if 0 < (hit["pos1"] - last["pos1"]) <= max_gap:
                if abs(hit["distance"] - last["distance"]) <= distance_tolerance:
                    grp.append(hit)
                    placed = True
                    break
        if not placed:
            groups.append([hit])

    # Filter groups with at least 2 consistent seeds
    return [g for g in groups if len(g) >= 2]


def expand_homology_islands(
    sequence: str,
    seed_groups: list[list[dict[str, int]]],
    threshold: float = 0.85,
    window_size: int = 20,
) -> list[dict[str, Any]]:
    """Expand homologous direct repeats bidirectionally along the same strand."""
    expanded_blocks = []
    seq_len = len(sequence)

    for grp in seed_groups:
        pos1_start = min(h["pos1"] for h in grp)
        pos1_end = max(h["pos1"] for h in grp) + window_size
        pos2_start = min(h["pos2"] for h in grp)
        pos2_end = max(h["pos2"] for h in grp) + window_size

        # Expand left
        while pos1_start > 0 and pos2_start > 0:
            test1 = sequence[pos1_start - 1 : pos1_start + window_size - 1]
            test2 = sequence[pos2_start - 1 : pos2_start + window_size - 1]
            if calculate_homology_score(test1, test2) >= threshold:
                pos1_start -= 1
                pos2_start -= 1
            else:
                break

        # Expand right
        while pos1_end < seq_len and pos2_end < seq_len:
            test1 = sequence[pos1_end - window_size + 1 : pos1_end + 1]
            test2 = sequence[pos2_end - window_size + 1 : pos2_end + 1]
            if calculate_homology_score(test1, test2) >= threshold:
                pos1_end += 1
                pos2_end += 1
            else:
                break

        length = pos1_end - pos1_start
        if length >= 25:
            s1 = sequence[pos1_start:pos1_end]
            s2 = sequence[pos2_start:pos2_end]
            identity = calculate_homology_score(s1, s2)
            expanded_blocks.append({
                "region1_start": pos1_start,
                "region1_end": pos1_end,
                "region2_start": pos2_start,
                "region2_end": pos2_end,
                "length_bp": length,
                "distance": pos2_start - pos1_start,
                "identity": round(identity, 3),
            })

    # Merge overlapping homology blocks
    expanded_blocks.sort(key=lambda x: (x["region1_start"], x["region2_start"]))
    merged: list[dict[str, Any]] = []
    for blk in expanded_blocks:
        if not merged:
            merged.append(blk)
        else:
            last = merged[-1]
            if blk["region1_start"] <= last["region1_end"] and blk["region2_start"] <= last["region2_end"]:
                last["region1_end"] = max(last["region1_end"], blk["region1_end"])
                last["region2_end"] = max(last["region2_end"], blk["region2_end"])
                last["length_bp"] = max(last["length_bp"], blk["length_bp"])
            else:
                merged.append(blk)

    return merged


def detect_repeated_arms(
    sequence: str,
    lineage_start: int,
    lineage_end: int,
    known_islands: list[dict[str, Any]],
    threshold: float = 0.85,
) -> list[dict[str, Any]]:
    """Perform direct homology matching on a SHaNE lineage to detect repeated/duplicated arms.
    
    Cross-references homologous regions with the SHaNE's complementary islands.
    """
    if not sequence or len(sequence) < 40:
        return []

    # 1. Scan direct same-strand matching seeds (every 20-mer indexed with step=1)
    seeds = scan_direct_homology_seeds(sequence, window_size=20, step=1, min_distance=25)
    if not seeds:
        return []

    # 2. Group consistent-shift seeds with generous deletion tolerance
    groups = group_homology_hits(seeds, distance_tolerance=200, max_gap=2500)
    if not groups:
        return []

    # 3. Expand homology islands
    homology_blocks = expand_homology_islands(sequence, groups, threshold=threshold)

    # 4. Cross-reference with SHaNE island coordinates
    repeated_arms = []
    for blk in homology_blocks:
        g_r1_s = lineage_start + blk["region1_start"]
        g_r1_e = lineage_start + blk["region1_end"]
        g_r2_s = lineage_start + blk["region2_start"]
        g_r2_e = lineage_start + blk["region2_end"]

        # Check overlap with any known island
        overlaps_island = False
        overlapping_islands = []
        for isl in known_islands:
            i_s = isl.get("start", isl.get("s_start", 0))
            i_e = isl.get("end", isl.get("s_end", 0))
            if not (g_r1_e < i_s or g_r1_s > i_e) or not (g_r2_e < i_s or g_r2_s > i_e):
                overlaps_island = True
                overlapping_islands.append(isl)

        repeated_arms.append({
            "region1": {"start": g_r1_s, "end": g_r1_e, "rel_start": blk["region1_start"], "rel_end": blk["region1_end"]},
            "region2": {"start": g_r2_s, "end": g_r2_e, "rel_start": blk["region2_start"], "rel_end": blk["region2_end"]},
            "length_bp": blk["length_bp"],
            "distance_bp": blk["distance"],
            "identity": blk["identity"],
            "overlaps_shane_islands": overlaps_island,
            "associated_island_count": len(overlapping_islands),
        })

    return repeated_arms
