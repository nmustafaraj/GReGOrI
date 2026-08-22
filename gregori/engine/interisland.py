"""Hierarchical k-mer seed-and-extend interisland alignment and branching classification.

Algorithm:
1. Multi-scale k-mer scanning from k=10 down to k=4.
2. Bidirectional extension tracking consecutive mismatches, cutting where 3 consecutive mismatches begin.
3. Recursive divide-and-conquer partitioning across sub-interisland regions.
4. Single-strand self-complementarity scanning for single, double, and sliding (crossed) branching topologies.
"""
from typing import Any
from .alignment import is_wc_pair, align_islands_wc, center_pad, get_reverse_complement


def scan_wc_kmers(seq1: str, seq2: str, k: int = 5, max_seeds: int = 200) -> list[tuple[int, int]]:
    """Find all exact Watson-Crick k-mer match starting positions between seq1 and seq2 in O(N)."""
    if len(seq1) < k or len(seq2) < k:
        return []

    # Map all valid k-mers in seq2 to their start positions (skipping dead N-bases)
    kmer_map: dict[str, list[int]] = {}
    for j in range(len(seq2) - k + 1):
        sub2 = seq2[j : j + k].upper()
        if "N" in sub2:
            continue
        positions = kmer_map.setdefault(sub2, [])
        if len(positions) < 10:
            positions.append(j)

    # For each k-mer in seq1, get its Watson-Crick complement and lookup in seq2
    matches: list[tuple[int, int]] = []
    comp_trans = str.maketrans("ACGTNacgtn", "TGCANtgcan")
    for i in range(len(seq1) - k + 1):
        sub1 = seq1[i : i + k].upper()
        if "N" in sub1:
            continue
        wc_target = sub1.translate(comp_trans)
        if wc_target in kmer_map:
            for j in kmer_map[wc_target]:
                matches.append((i, j))
                if len(matches) >= max_seeds:
                    return matches
    return matches


def extend_match(
    seq1: str,
    seq2: str,
    start1: int,
    start2: int,
    k: int = 5,
    max_consecutive_mismatches: int = 3,
) -> tuple[int, int, int, int]:
    """Grow match bidirectionally, cutting immediately before 3 consecutive mismatches begin.

    Returns (left1, right1, left2, right2) indices (where right is end-exclusive index).
    """
    n1, n2 = len(seq1), len(seq2)
    l1, l2 = start1, start2
    r1, r2 = start1 + k - 1, start2 + k - 1

    # 1. Extend leftwards
    consec_mismatches = 0
    cur_l1, cur_l2 = l1 - 1, l2 - 1
    pending_left: list[tuple[int, int, bool]] = []

    while cur_l1 >= 0 and cur_l2 >= 0:
        match = is_wc_pair(seq1[cur_l1], seq2[cur_l2])
        if match:
            consec_mismatches = 0
            pending_left.append((cur_l1, cur_l2, True))
        else:
            consec_mismatches += 1
            if consec_mismatches >= max_consecutive_mismatches:
                # 3 consecutive mismatches: stop expanding left and cut here
                break
            pending_left.append((cur_l1, cur_l2, False))
        cur_l1 -= 1
        cur_l2 -= 1

    # Cut off trailing mismatches up to the last confirmed match
    while pending_left and not pending_left[-1][2]:
        pending_left.pop()
    if pending_left:
        l1 = pending_left[-1][0]
        l2 = pending_left[-1][1]

    # 2. Extend rightwards
    consec_mismatches = 0
    cur_r1, cur_r2 = r1 + 1, r2 + 1
    pending_right: list[tuple[int, int, bool]] = []

    while cur_r1 < n1 and cur_r2 < n2:
        match = is_wc_pair(seq1[cur_r1], seq2[cur_r2])
        if match:
            consec_mismatches = 0
            pending_right.append((cur_r1, cur_r2, True))
        else:
            consec_mismatches += 1
            if consec_mismatches >= max_consecutive_mismatches:
                # 3 consecutive mismatches: stop expanding right and cut here
                break
            pending_right.append((cur_r1, cur_r2, False))
        cur_r1 += 1
        cur_r2 += 1

    while pending_right and not pending_right[-1][2]:
        pending_right.pop()
    if pending_right:
        r1 = pending_right[-1][0]
        r2 = pending_right[-1][1]

    return l1, r1 + 1, l2, r2 + 1


def chain_non_crossing_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Select the subset of expanded blocks that strictly maximizes overall score without crossing over."""
    if not blocks:
        return []

    # Deduplicate identical coordinate spans
    unique: dict[tuple[int, int, int, int], dict[str, Any]] = {}
    for b in blocks:
        key = (b["start1"], b["end1"], b["start2"], b["end2"])
        if key not in unique or b["score"] > unique[key]["score"]:
            unique[key] = b
    sorted_blocks = sorted(unique.values(), key=lambda x: (x["start1"], x["start2"]))

    n = len(sorted_blocks)
    dp = [0] * n
    parent = [-1] * n

    for i in range(n):
        dp[i] = sorted_blocks[i]["score"]
        for j in range(i):
            # Collinear / Non-crossing condition: Block j must end before Block i starts on BOTH strands
            if sorted_blocks[j]["end1"] <= sorted_blocks[i]["start1"] and sorted_blocks[j]["end2"] <= sorted_blocks[i]["start2"]:
                if dp[j] + sorted_blocks[i]["score"] > dp[i]:
                    dp[i] = dp[j] + sorted_blocks[i]["score"]
                    parent[i] = j

    best_idx = max(range(n), key=lambda i: dp[i])
    chain: list[dict[str, Any]] = []
    curr = best_idx
    while curr != -1:
        chain.append(sorted_blocks[curr])
        curr = parent[curr]
    chain.reverse()
    return chain


def align_interisland_optimal_5mer(
    seq1: str,
    seq2: str,
    min_k: int = 5,
    max_mismatches: int = 3,
    **kwargs: Any,
) -> tuple[str, str]:
    """Scan 5-mers, expand with 3-mismatch boundary cut, chain non-crossing blocks, and place contiguous voids."""
    if not seq1 and not seq2:
        return "", ""
    if not seq1:
        return "." * len(seq2), seq2
    if not seq2:
        return seq1, "." * len(seq1)

    # Ultra-short loops (< min_k): align directly
    if len(seq1) < min_k or len(seq2) < min_k:
        L1, L2 = len(seq1), len(seq2)
        if L1 == L2:
            return seq1, seq2
        if L1 < L2:
            return seq1 + ("." * (L2 - L1)), seq2
        return seq1, seq2 + ("." * (L1 - L2))

    # 1. Scan for all 5-mers
    seeds = scan_wc_kmers(seq1, seq2, k=min_k)

    # 2. Expand each 5-mer with 3-mismatch cutoff rule
    raw_blocks: list[dict[str, Any]] = []
    for s1, s2 in seeds:
        # A. Exact contiguous 100% WC match extent
        l1_tight, l2_tight = s1, s2
        while l1_tight > 0 and l2_tight > 0 and is_wc_pair(seq1[l1_tight - 1], seq2[l2_tight - 1]):
            l1_tight -= 1
            l2_tight -= 1
        r1_tight, r2_tight = s1 + min_k, s2 + min_k
        while r1_tight < len(seq1) and r2_tight < len(seq2) and is_wc_pair(seq1[r1_tight], seq2[r2_tight]):
            r1_tight += 1
            r2_tight += 1
        len_tight = r1_tight - l1_tight
        raw_blocks.append({
            "start1": l1_tight,
            "end1": r1_tight,
            "start2": l2_tight,
            "end2": r2_tight,
            "matches": len_tight,
            "score": len_tight * 2,
            "len": len_tight,
        })

        # B. 3-mismatch extended extent
        l1, r1, l2, r2 = extend_match(seq1, seq2, s1, s2, k=min_k, max_consecutive_mismatches=max_mismatches)
        length1 = r1 - l1
        length2 = r2 - l2
        length = min(length1, length2)
        wc_matches = sum(1 for idx in range(length) if is_wc_pair(seq1[l1 + idx], seq2[l2 + idx]))
        mismatches = length - wc_matches
        score = (wc_matches * 2) - (mismatches * 3)
        raw_blocks.append({
            "start1": l1,
            "end1": r1,
            "start2": l2,
            "end2": r2,
            "matches": wc_matches,
            "score": score,
            "len": length,
        })

    # 3. Retain blocks that maximize overall score without crossing over
    chain = chain_non_crossing_blocks(raw_blocks)

    # 4. Standardized orphan & void placement
    out1: list[str] = []
    out2: list[str] = []
    cur1, cur2 = 0, 0

    for b in chain:
        # Unaligned orphan gap before block
        u1 = seq1[cur1 : b["start1"]]
        u2 = seq2[cur2 : b["start2"]]
        L1, L2 = len(u1), len(u2)
        if L1 == L2:
            out1.append(u1)
            out2.append(u2)
        elif L1 < L2:
            out1.append(u1 + ("." * (L2 - L1)))
            out2.append(u2)
        else:
            out1.append(u1)
            out2.append(u2 + ("." * (L1 - L2)))

        # Matched block
        out1.append(seq1[b["start1"] : b["end1"]])
        out2.append(seq2[b["start2"] : b["end2"]])
        cur1 = b["end1"]
        cur2 = b["end2"]

    # Trailing unaligned orphan gap
    tail1 = seq1[cur1:]
    tail2 = seq2[cur2:]
    L1, L2 = len(tail1), len(tail2)
    if L1 == L2:
        out1.append(tail1)
        out2.append(tail2)
    elif L1 < L2:
        out1.append(tail1 + ("." * (L2 - L1)))
        out2.append(tail2)
    else:
        out1.append(tail1)
        out2.append(tail2 + ("." * (L1 - L2)))

    return "".join(out1), "".join(out2)


# Backwards compatibility alias
align_interisland_hierarchical = align_interisland_optimal_5mer


def scan_self_complementarity(seq: str, min_stem: int = 4) -> list[dict[str, int]]:
    """Scan a single RNA/DNA strand for internal self-complementarity (stems / hairpins) in O(N).
    
    A stem consists of a 5' arm [s1, e1] pairing with an internal 3' arm [s2, e2] within the same strand (s1 < e1 <= s2 < e2).
    """
    stems: list[dict[str, int]] = []
    n = len(seq)
    if n < 2 * min_stem + 3:
        return []

    # For large loops, analyze up to 500 bp to keep execution in sub-milliseconds
    work_seq = seq[:500] if n > 500 else seq
    wn = len(work_seq)
    comp_trans = str.maketrans("ACGTNacgtn", "TGCANtgcan")

    for k in range(min(10, wn // 2), min_stem - 1, -1):
        if len(stems) >= 10:
            break
        # Index all k-mers in work_seq
        kmer_map: dict[str, list[int]] = {}
        for pos in range(wn - k + 1):
            kmer = work_seq[pos : pos + k].upper()
            kmer_map.setdefault(kmer, []).append(pos)

        i = 0
        while i < wn - 2 * k - 2:
            if len(stems) >= 10:
                break
            arm1 = work_seq[i : i + k].upper()
            target_rc = arm1.translate(comp_trans)[::-1]
            if target_rc in kmer_map:
                for j in kmer_map[target_rc][:4]:
                    if j >= i + k + 3:
                        # Extend stem outwards if possible
                        l1, r1 = i, i + k
                        l2, r2 = j, j + k
                        while l1 > 0 and r2 < wn and is_wc_pair(work_seq[l1 - 1], work_seq[r2]):
                            l1 -= 1
                            r2 += 1
                        while r1 < l2 and is_wc_pair(work_seq[r1], work_seq[l2 - 1]):
                            r1 += 1
                            l2 -= 1

                        # Check for redundancy with existing stems
                        if not any(s["s1"] <= l1 and r1 <= s["e1"] and s["s2"] <= l2 and r2 <= s["e2"] for s in stems):
                            stems.append({"s1": l1, "e1": r1, "s2": l2, "e2": r2, "len": r1 - l1})
            i += 1

    stems.sort(key=lambda s: s["s1"])
    return stems


def find_internal_hairpin_branches(seq: str, min_stem: int = 5, max_mismatches: int = 3) -> list[dict[str, Any]]:
    """Scan a sequence for all non-crossing independent internal hairpin branches."""
    n = len(seq)
    if n < 2 * min_stem + 3:
        return []

    # For very long loops, scan up to 1000 bp
    work_seq = seq[:1000] if n > 1000 else seq
    wn = len(work_seq)
    comp_trans = str.maketrans("ACGTNacgtn", "TGCANtgcan")
    k = min_stem

    kmer_map: dict[str, list[int]] = {}
    for j in range(wn - k + 1):
        sub = work_seq[j : j + k].upper()
        if "N" in sub:
            continue
        kmer_map.setdefault(sub, []).append(j)

    stems: list[dict[str, Any]] = []
    for i in range(wn - 2 * k - 2):
        sub1 = work_seq[i : i + k].upper()
        if "N" in sub1:
            continue
        target_rc = sub1.translate(comp_trans)[::-1]
        if target_rc in kmer_map:
            for j in kmer_map[target_rc][:6]:
                if j >= i + k + 3:
                    l1, r1 = i, i + k
                    l2, r2 = j, j + k
                    # Expand left on arm 1 and right on arm 2
                    consec = 0
                    while l1 > 0 and r2 < wn:
                        if is_wc_pair(work_seq[l1 - 1], work_seq[r2]):
                            consec = 0
                            l1 -= 1
                            r2 += 1
                        else:
                            consec += 1
                            if consec >= max_mismatches:
                                break
                            l1 -= 1
                            r2 += 1
                    # Expand right on arm 1 and left on arm 2
                    while r1 < l2 and is_wc_pair(work_seq[r1], work_seq[l2 - 1]):
                        r1 += 1
                        l2 -= 1

                    stem_len = r1 - l1
                    if stem_len >= min_stem:
                        arm5 = work_seq[l1:r1]
                        arm3 = work_seq[l2:r2]
                        wc_count = sum(1 for a, b in zip(arm5, arm3[::-1]) if is_wc_pair(a, b))
                        score = round(wc_count / stem_len, 4) if stem_len else 0.0
                        stems.append({
                            "s1": l1,
                            "e1": r1,
                            "s2": l2,
                            "e2": r2,
                            "stem_length": stem_len,
                            "loop_length": l2 - r1,
                            "loop_seq": work_seq[r1:l2],
                            "full_hairpin_seq": arm5.upper() + work_seq[r1:l2].lower() + arm3.upper(),
                            "arm5": arm5,
                            "arm3": arm3,
                            "wc_matches": wc_count,
                            "score": score,
                        })

    if not stems:
        return []

    # Deduplicate and sort
    unique: dict[tuple[int, int, int, int], dict[str, Any]] = {}
    for s in stems:
        key = (s["s1"], s["e1"], s["s2"], s["e2"])
        if key not in unique or s["stem_length"] > unique[key]["stem_length"]:
            unique[key] = s
    sorted_stems = sorted(unique.values(), key=lambda x: (x["s1"], x["s2"]))

    # DP to select maximum-score non-overlapping independent hairpin branches
    n_s = len(sorted_stems)
    dp = [0] * n_s
    parent = [-1] * n_s
    for i in range(n_s):
        dp[i] = sorted_stems[i]["stem_length"]
        for j in range(i):
            if sorted_stems[j]["e2"] <= sorted_stems[i]["s1"]:
                if dp[j] + sorted_stems[i]["stem_length"] > dp[i]:
                    dp[i] = dp[j] + sorted_stems[i]["stem_length"]
                    parent[i] = j

    best_idx = max(range(n_s), key=lambda idx: dp[idx])
    chain: list[dict[str, Any]] = []
    curr = best_idx
    while curr != -1:
        chain.append(sorted_stems[curr])
        curr = parent[curr]
    chain.reverse()
    return chain


def classify_internal_branching(seq: str, min_stem: int = 4) -> dict[str, Any]:
    """Classify internal secondary structure / branching topology of an interisland sequence."""
    stems = scan_self_complementarity(seq, min_stem=min_stem)
    if not stems:
        return {"topology": "unbranched", "stems_count": 0, "stems": []}

    if len(stems) == 1:
        return {"topology": "single_branch", "stems_count": 1, "stems": stems}

    # Analyze multi-stem topology
    has_double_branch = False
    has_sliding_branch = False
    has_nested = False

    for i in range(len(stems)):
        for j in range(i + 1, len(stems)):
            sA, sB = stems[i], stems[j]
            # Disjoint / Double Branch: A is completely before B
            if sA["e2"] <= sB["s1"] or sB["e2"] <= sA["s1"]:
                has_double_branch = True
            # Strictly Nested: B is completely inside the loop of A
            elif sA["e1"] <= sB["s1"] and sB["e2"] <= sA["s2"]:
                has_nested = True
            # Crossed / Sliding Branch: arms interleave (pseudoknot: sA1 < sB1 < sA2 < sB2)
            elif (sA["s1"] < sB["s1"] < sA["e2"] < sB["e2"]) or (sB["s1"] < sA["s1"] < sB["e2"] < sA["e2"]):
                has_sliding_branch = True

    if has_double_branch:
        top = "double_branch"
    elif has_sliding_branch:
        top = "sliding_branch"
    elif has_nested:
        top = "single_branch"
    else:
        top = "single_branch"

    return {
        "topology": top,
        "stems_count": len(stems),
        "stems": stems,
    }


def analyze_shane_branching(
    seq: str,
    islands: list[dict[str, int]],
    shane_start: int = 0,
    min_stem: int = 5,
) -> dict[str, Any]:
    """Analyze all interisland regions and central loop of a SHaNE for branching structures."""
    all_branches: list[dict[str, Any]] = []
    topologies: list[str] = []

    if not islands:
        # Check whole sequence if no islands
        branches = find_internal_hairpin_branches(seq, min_stem=min_stem)
        for idx, b in enumerate(branches):
            b["id"] = f"B{idx + 1}"
            b["location"] = "Central Loop"
            b_offset = shane_start if (len(seq) < shane_start or shane_start == 0) else shane_start
            b["genomic_arm5_start"] = b_offset + b["s1"]
            b["genomic_arm5_end"] = b_offset + b["e1"]
            b["genomic_arm3_start"] = b_offset + b["s2"]
            b["genomic_arm3_end"] = b_offset + b["e2"]
            b["genomic_start"] = b["genomic_arm5_start"]
            b["genomic_end"] = b["genomic_arm3_end"]
            b["total_branch_length_bp"] = b["genomic_end"] - b["genomic_start"]
            b["branch_record_seq"] = b["arm5"].upper() + b["loop_seq"].lower() + b["arm3"].upper()
            b["full_hairpin_seq"] = b["branch_record_seq"]
            all_branches.append(b)
        top = "multi_branch" if len(all_branches) >= 3 else ("double_branch" if len(all_branches) == 2 else ("single_branch" if len(all_branches) == 1 else "unbranched"))
        return {
            "topology": top,
            "branch_count": len(all_branches),
            "branches": all_branches,
            "branching_alignment": format_branches_alignment(all_branches),
        }

    branch_idx = 1
    # 1. 5' and 3' interisland loop regions between successive islands
    for i in range(len(islands) - 1):
        next_isl = islands[i + 1]
        s_5p = islands[i]["s_end"]
        e_5p = next_isl["s_start"]
        loop5 = seq[s_5p:e_5p]
        base_5p = s_5p if s_5p >= shane_start else (shane_start + s_5p)
        if len(loop5) >= 2 * min_stem + 3:
            b_list = find_internal_hairpin_branches(loop5, min_stem=min_stem)
            for b in b_list:
                b["id"] = f"B{branch_idx}"
                b["location"] = f"5' Interisland {i + 1}"
                b["genomic_arm5_start"] = base_5p + b["s1"]
                b["genomic_arm5_end"] = base_5p + b["e1"]
                b["genomic_arm3_start"] = base_5p + b["s2"]
                b["genomic_arm3_end"] = base_5p + b["e2"]
                b["genomic_start"] = b["genomic_arm5_start"]
                b["genomic_end"] = b["genomic_arm3_end"]
                b["total_branch_length_bp"] = b["genomic_end"] - b["genomic_start"]
                b["branch_record_seq"] = b["arm5"].upper() + b["loop_seq"].lower() + b["arm3"].upper()
                b["full_hairpin_seq"] = b["branch_record_seq"]
                all_branches.append(b)
                branch_idx += 1
            if len(b_list) >= 2:
                topologies.append("double_branch")
            elif len(b_list) == 1:
                topologies.append("single_branch")

        s_3p = next_isl["h_end"]
        e_3p = islands[i]["h_start"]
        loop3 = seq[s_3p:e_3p]
        base_3p = s_3p if s_3p >= shane_start else (shane_start + s_3p)
        if len(loop3) >= 2 * min_stem + 3:
            b_list = find_internal_hairpin_branches(loop3, min_stem=min_stem)
            for b in b_list:
                b["id"] = f"B{branch_idx}"
                b["location"] = f"3' Interisland {i + 1}"
                b["genomic_arm5_start"] = base_3p + b["s1"]
                b["genomic_arm5_end"] = base_3p + b["e1"]
                b["genomic_arm3_start"] = base_3p + b["s2"]
                b["genomic_arm3_end"] = base_3p + b["e2"]
                b["genomic_start"] = b["genomic_arm5_start"]
                b["genomic_end"] = b["genomic_arm3_end"]
                b["total_branch_length_bp"] = b["genomic_end"] - b["genomic_start"]
                b["branch_record_seq"] = b["arm5"].upper() + b["loop_seq"].lower() + b["arm3"].upper()
                b["full_hairpin_seq"] = b["branch_record_seq"]
                all_branches.append(b)
                branch_idx += 1
            if len(b_list) >= 2:
                topologies.append("double_branch")
            elif len(b_list) == 1:
                topologies.append("single_branch")

    # 2. Central turnaround loop between innermost island arms
    center_s = islands[-1]["s_end"]
    center_e = islands[-1]["h_start"]
    center_seq = seq[center_s:center_e]
    base_center = center_s if center_s >= shane_start else (shane_start + center_s)
    if len(center_seq) >= 2 * min_stem + 3:
        b_list = find_internal_hairpin_branches(center_seq, min_stem=min_stem)
        for b in b_list:
            b["id"] = f"B{branch_idx}"
            b["location"] = "Central Loop"
            b["genomic_arm5_start"] = base_center + b["s1"]
            b["genomic_arm5_end"] = base_center + b["e1"]
            b["genomic_arm3_start"] = base_center + b["s2"]
            b["genomic_arm3_end"] = base_center + b["e2"]
            b["genomic_start"] = b["genomic_arm5_start"]
            b["genomic_end"] = b["genomic_arm3_end"]
            b["total_branch_length_bp"] = b["genomic_end"] - b["genomic_start"]
            b["branch_record_seq"] = b["arm5"].upper() + b["loop_seq"].lower() + b["arm3"].upper()
            b["full_hairpin_seq"] = b["branch_record_seq"]
            all_branches.append(b)
            branch_idx += 1
        if len(b_list) >= 2:
            topologies.append("double_branch")
        elif len(b_list) == 1:
            topologies.append("single_branch")

    if len(all_branches) >= 3 or topologies.count("double_branch") >= 1:
        overall_top = "multi_branch" if len(all_branches) >= 3 else "double_branch"
    elif len(all_branches) == 2:
        overall_top = "double_branch"
    elif len(all_branches) == 1:
        overall_top = "single_branch"
    else:
        overall_top = "unbranched"

    return {
        "topology": overall_top,
        "branch_count": len(all_branches),
        "branches": all_branches,
        "branching_alignment": format_branches_alignment(all_branches),
    }


def format_branches_alignment(branches: list[dict[str, Any]]) -> str:
    """Format visual alignment text for all detected branching stems."""
    if not branches:
        return "No internal branching hairpins detected."

    blocks = []
    for b in branches:
        arm5 = b.get("arm5", "")
        arm3 = b.get("arm3", "")
        arm3_rev = arm3[::-1]
        bonds = "".join("|" if is_wc_pair(x, y) else " " for x, y in zip(arm5, arm3_rev))
        bid = b.get("id", "1")
        loc = b.get("location", "Loop")
        g_s1 = b.get("genomic_arm5_start", b.get("s1", 0))
        g_e1 = b.get("genomic_arm5_end", b.get("e1", 0))
        g_s2 = b.get("genomic_arm3_start", b.get("s2", 0))
        g_e2 = b.get("genomic_arm3_end", b.get("e2", 0))
        slen = b.get("stem_length", len(arm5))
        llen = b.get("loop_length", 0)
        score = b.get("score", 1.0)

        header = f"Branch {bid} [{loc}]: {g_s1}-{g_e1} vs {g_s2}-{g_e2} (Stem: {slen} bp, Loop: {llen} bp, Score: {score:.2f})"
        row5 = f"5' {arm5}  {g_e1}"
        pair = f"   {bonds}"
        row3 = f"3' {arm3_rev}  {g_s2}"
        blocks.append(f"{header}\n{row5}\n{pair}\n{row3}")

    return "\n\n".join(blocks)
