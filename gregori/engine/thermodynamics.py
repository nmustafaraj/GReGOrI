"""Thermodynamics and Central Loop Secondary Structure & Evolutionary Analysis for GReGOrI.

Implements SantaLucia (1998) Unified Nearest-Neighbor DNA/RNA duplex parameters
and statistical analysis of central loop self-complementarity vs random expectations.
"""
from __future__ import annotations

import math
from typing import Any

from .alignment import calculate_score, align_loops_wc, get_reverse_complement, is_wc_pair

# SantaLucia (1998) Unified Nearest-Neighbor parameters for Watson-Crick DNA duplexes
# Delta H in kcal/mol, Delta S in cal/(mol*K)
NN_PARAMS: dict[str, tuple[float, float]] = {
    "AA/TT": (-7.9, -22.2),
    "TT/AA": (-7.9, -22.2),
    "AT/TA": (-7.2, -20.4),
    "TA/AT": (-7.2, -21.3),
    "CA/GT": (-8.5, -22.7),
    "GT/CA": (-8.4, -22.4),
    "CT/GA": (-7.8, -21.0),
    "GA/CT": (-8.2, -22.2),
    "CG/GC": (-10.6, -27.2),
    "GC/CG": (-9.8, -24.4),
    "GG/CC": (-8.0, -19.9),
    "CC/GG": (-8.0, -19.9),
    # Reverse orientations for complementary lookups
    "AC/TG": (-8.4, -22.4),
    "TG/AC": (-8.5, -22.7),
    "TC/AG": (-8.2, -22.2),
    "AG/TC": (-7.8, -21.0),
}

# Initiation terms (SantaLucia 1998)
INIT_AT: tuple[float, float] = (2.3, 4.1)
INIT_GC: tuple[float, float] = (0.1, -2.8)


def calculate_island_thermodynamics(
    arm5: str,
    arm3: str,
    na_conc_m: float = 0.050,
    strand_conc_m: float = 2e-7,
) -> dict[str, Any]:
    """Calculate nearest-neighbor Delta H, Delta S, Delta G(37C), and Tm for an island duplex."""
    s1 = arm5.strip().upper()
    s2 = arm3.strip().upper()
    n = min(len(s1), len(s2))
    if n < 2:
        return {
            "delta_h_kcal": 0.0,
            "delta_s_cal": 0.0,
            "delta_g_37_kcal": 0.0,
            "tm_celsius": 0.0,
            "is_stable": False,
        }

    # Automatically check if arm3 is passed in 5'->3' genomic orientation or 3'->5' anti-parallel alignment orientation
    direct_wc = sum(1 for i in range(n) if is_wc_pair(s1[i], s2[i]))
    s2_rev = s2[::-1]
    rev_wc = sum(1 for i in range(n) if is_wc_pair(s1[i], s2_rev[i]))
    if rev_wc > direct_wc:
        s2 = s2_rev

    dh = 0.0
    ds = 0.0

    valid_pairs = [(s1[i], s2[i]) for i in range(n) if s1[i] != "." and s2[i] != "."]
    if valid_pairs:
        p1 = valid_pairs[0]
        if p1 in (("G", "C"), ("C", "G")):
            dh += INIT_GC[0]
            ds += INIT_GC[1]
        elif p1 in (("A", "T"), ("T", "A")):
            dh += INIT_AT[0]
            ds += INIT_AT[1]
        pn = valid_pairs[-1]
        if pn in (("G", "C"), ("C", "G")):
            dh += INIT_GC[0]
            ds += INIT_GC[1]
        elif pn in (("A", "T"), ("T", "A")):
            dh += INIT_AT[0]
            ds += INIT_AT[1]

    stacked_pairs = 0
    wc_matches = 0
    gc_count = 0

    for i in range(n):
        if is_wc_pair(s1[i], s2[i]):
            wc_matches += 1
            if s1[i] in "GC":
                gc_count += 1

    for i in range(n - 1):
        c1_1, c1_2 = s1[i], s1[i + 1]
        c2_1, c2_2 = s2[i], s2[i + 1]
        if is_wc_pair(c1_1, c2_1) and is_wc_pair(c1_2, c2_2):
            key = f"{c1_1}{c1_2}/{c2_1}{c2_2}"
            if key in NN_PARAMS:
                h_val, s_val = NN_PARAMS[key]
                dh += h_val
                ds += s_val
                stacked_pairs += 1
            else:
                dh += -8.0
                ds += -22.0
                stacked_pairs += 1
        else:
            dh += 1.0
            ds += 2.0

    t_k = 310.15
    dg_37 = dh - (t_k * ds / 1000.0)

    salt_term = 16.6 * math.log10(na_conc_m)
    gc_pct = (gc_count / max(1, wc_matches)) * 100.0 if wc_matches else 0.0
    mismatch_pct = ((n - wc_matches) / max(1, n)) * 100.0

    if n >= 50:
        # Standard salt-corrected polymer melting temperature formula (SantaLucia 1998 / Owczarzy 2004 / Wetmur 1991)
        tm_c = 81.5 + salt_term + 0.41 * gc_pct - (500.0 / n) - 0.61 * mismatch_pct
    else:
        # Oligonucleotide nearest-neighbor formula with SantaLucia (1998) salt-adjusted entropy
        ds_salt = ds + 0.368 * (n - 1) * math.log(na_conc_m)
        r_const = 1.9872
        denom = ds_salt + r_const * math.log(strand_conc_m / 4.0)
        if denom != 0 and dh < 0:
            tm_c = (dh * 1000.0) / denom - 273.15
        else:
            tm_c = 64.9 + 41.0 * (gc_count - 16.4) / max(1, n)

    tm_c = max(10.0, min(115.0, tm_c))

    return {
        "delta_h_kcal": round(dh, 1),
        "delta_s_cal": round(ds, 1),
        "delta_g_37_kcal": round(dg_37, 1),
        "tm_celsius": round(tm_c, 1),
        "stacked_pairs": stacked_pairs,
        "is_stable": dg_37 < -2.0,
    }


def analyze_central_loop(loop_seq: str, min_subwindow: int = 15) -> dict[str, Any]:
    """Calculate GC distribution, random expected complementarity, and actual self-folding scores.
    
    Skips analysis if the central loop contains ambiguous / null (N) bases.
    """
    clean_seq = loop_seq.upper().replace(".", "").replace(" ", "").replace("-", "")
    n = len(clean_seq)

    # Exclude analysis if loop contains N, null bases, or non-canonical characters
    if not clean_seq or "N" in clean_seq or any(c not in "ACGT" for c in clean_seq):
        return {
            "has_central_loop": False,
            "contains_null_bases": True,
            "has_n_bases": True,
            "loop_length_bp": n,
            "loop_seq": clean_seq,
            "gc_content_percent": 0.0,
            "gc_spatial_uniformity": "N/A",
            "expected_random_wc_prob": 0.0,
            "expected_random_score_pct": 0.0,
            "actual_direct_score": 0.0,
            "actual_direct_score_pct": 0.0,
            "actual_optimized_score": 0.0,
            "actual_optimized_score_pct": 0.0,
            "evolved_to_remain_unfolded": False,
            "unfolding_ratio": 1.0,
            "hypothesis_badge": "Excluded (Contains N)",
            "hypothesis_text": "Central loop contains undetermined/null (N) bases and was excluded from thermodynamic and self-folding analysis.",
        }

    if n < 6:
        return {
            "has_central_loop": False,
            "contains_null_bases": False,
            "has_n_bases": False,
            "loop_length_bp": n,
            "loop_seq": clean_seq,
            "gc_content_percent": 0.0,
            "gc_spatial_uniformity": "N/A",
            "expected_random_wc_prob": 0.25,
            "expected_random_score_pct": 25.0,
            "actual_direct_score": 0.0,
            "actual_direct_score_pct": 0.0,
            "actual_optimized_score": 0.0,
            "actual_optimized_score_pct": 0.0,
            "evolved_to_remain_unfolded": False,
            "unfolding_ratio": 1.0,
            "hypothesis_badge": "N/A",
            "hypothesis_text": "Loop sequence too short for secondary structure evaluation.",
        }

    valid_bases = [c for c in clean_seq if c in "ACGT"]
    n_valid = len(valid_bases) or 1
    count_a = clean_seq.count("A")
    count_t = clean_seq.count("T")
    count_g = clean_seq.count("G")
    count_c = clean_seq.count("C")

    f_a = count_a / n_valid
    f_t = count_t / n_valid
    f_g = count_g / n_valid
    f_c = count_c / n_valid

    gc_pct = round(((count_g + count_c) / n_valid) * 100.0, 2)

    num_windows = 5
    window_size = max(min_subwindow, n // num_windows)
    gc_windows = []
    for start_idx in range(0, n, max(1, window_size)):
        chunk = clean_seq[start_idx : start_idx + window_size]
        if len(chunk) >= 5:
            gc_sub = sum(1 for c in chunk if c in "GC") / len(chunk) * 100.0
            gc_windows.append(gc_sub)

    if len(gc_windows) > 1:
        mean_gc = sum(gc_windows) / len(gc_windows)
        variance = sum((x - mean_gc) ** 2 for x in gc_windows) / len(gc_windows)
        std_dev = math.sqrt(variance)
        if std_dev <= 7.5:
            uniformity_label = "Evenly Distributed"
        elif std_dev <= 16.0:
            uniformity_label = "Moderately Uniform"
        else:
            uniformity_label = "Clustered / Patchy"
    else:
        std_dev = 0.0
        uniformity_label = "Evenly Distributed"

    expected_p = 2.0 * ((f_a * f_t) + (f_g * f_c))
    expected_p = max(0.05, min(0.50, expected_p))
    expected_pct = round(expected_p * 100.0, 2)

    half = n // 2
    first_half = clean_seq[:half]
    second_half = clean_seq[n - half :]
    second_half_rc = get_reverse_complement(second_half)
    direct_score = calculate_score(first_half, second_half_rc)
    direct_pct = round(direct_score * 100.0, 2)

    aln1, aln2 = align_loops_wc(first_half, second_half)
    wc_matches = sum(1 for a, b in zip(aln1, aln2) if is_wc_pair(a, b))
    aligned_len = len(aln1) or 1
    optimized_score = round(wc_matches / aligned_len, 4)
    optimized_pct = round(optimized_score * 100.0, 2)

    evolved_unfolded = (optimized_score < expected_p) or (direct_score < expected_p * 0.75)
    unfolding_ratio = round(optimized_score / max(0.01, expected_p), 3)

    if evolved_unfolded:
        hypothesis_badge = "Evolved to Remain Unfolded"
        hypothesis_text = (
            f"This central loop exhibits a lower Watson-Crick self-binding ({optimized_pct}%) "
            f"than statistically predicted by chance for a random sequence of {gc_pct}% GC ({expected_pct}%). "
            f"This is consistent with negative evolutionary selection against ectopic hairpin folding, "
            f"preserving an open, flexible single-stranded loop between the flanking island stems."
        )
    else:
        hypothesis_badge = "Self-Complementary Loop"
        hypothesis_text = (
            f"This central loop exhibits moderate or elevated self-complementarity ({optimized_pct}%) "
            f"relative to random expectation ({expected_pct}% for {gc_pct}% GC), indicating propensity "
            f"for internal secondary structure formation."
        )

    return {
        "has_central_loop": True,
        "loop_length_bp": n,
        "gc_content_percent": gc_pct,
        "gc_spatial_std_dev": round(std_dev, 2),
        "gc_spatial_uniformity": uniformity_label,
        "expected_random_wc_prob": round(expected_p, 4),
        "expected_random_score_pct": expected_pct,
        "actual_direct_score": round(direct_score, 4),
        "actual_direct_score_pct": direct_pct,
        "actual_optimized_score": optimized_score,
        "actual_optimized_score_pct": optimized_pct,
        "evolved_to_remain_unfolded": evolved_unfolded,
        "unfolding_ratio": unfolding_ratio,
        "hypothesis_badge": hypothesis_badge,
        "hypothesis_text": hypothesis_text,
    }
