"""Watson-Crick Dynamic Programming & Alignment routines for GReGOrI."""
from __future__ import annotations

COMP_MAP = str.maketrans("ACGTNacgtn", "TGCANtgcan")


def get_reverse_complement(seq: str) -> str:
    """Return reverse complement of a nucleotide sequence."""
    return seq.translate(COMP_MAP)[::-1]


def rc(seq: str) -> str:
    """Convenience alias for reverse complement."""
    return get_reverse_complement(seq)


def is_wc_pair(a: str, b: str) -> bool:
    """Check if two characters form a canonical Watson-Crick base pair."""
    if not a or not b or a == "." or b == ".":
        return False
    ua, ub = a.upper(), b.upper()
    return (
        (ua == "A" and ub == "T")
        or (ua == "T" and ub == "A")
        or (ua == "C" and ub == "G")
        or (ua == "G" and ub == "C")
    )


def calculate_score(seq1: str, seq2_rc: str) -> float:
    """Calculate identity/complementarity proportion between two equal-length strings."""
    if not seq1 or not seq2_rc or len(seq1) != len(seq2_rc):
        return 0.0
    matches = sum(1 for a, b in zip(seq1.upper(), seq2_rc.upper()) if a == b and a in "ACGT")
    return matches / len(seq1)


def similarity(a: str, b: str) -> float:
    """Alias for identity proportion."""
    return calculate_score(a, b)


def center_pad(seq: str, target_len: int) -> str:
    """Distribute padding dots symmetrically around a sequence."""
    diff = target_len - len(seq)
    if diff <= 0:
        return seq
    left = diff // 2
    right = diff - left
    return ("." * left) + seq + ("." * right)


def align_islands_wc(seq1: str, seq2: str, band: int = 20, min_k: int = 5) -> tuple[str, str]:
    """Watson-Crick Dynamic Programming: exact 2D grid for standard lengths, banded acceleration for large sequences."""
    L1, L2 = len(seq1), len(seq2)
    if L1 == 0 and L2 == 0:
        return "", ""
    if L1 == L2 and all(is_wc_pair(a, b) for a, b in zip(seq1, seq2)):
        return seq1, seq2

    # Exact full 2D matrix for loops/islands <= 150 bp
    if max(L1, L2) <= 150:
        score = [[0] * (L2 + 1) for _ in range(L1 + 1)]
        for i in range(L1 + 1):
            score[i][0] = -2 * i
        for j in range(L2 + 1):
            score[0][j] = -2 * j

        for i in range(1, L1 + 1):
            for j in range(1, L2 + 1):
                match_score = 2 if is_wc_pair(seq1[i - 1], seq2[j - 1]) else -1
                score[i][j] = max(
                    score[i - 1][j - 1] + match_score,
                    score[i - 1][j] - 2,
                    score[i][j - 1] - 2,
                )

        align1, align2 = [], []
        i, j = L1, L2
        while i > 0 or j > 0:
            if i > 0 and j > 0:
                match_score = 2 if is_wc_pair(seq1[i - 1], seq2[j - 1]) else -1
                if score[i][j] == score[i - 1][j - 1] + match_score:
                    align1.append(seq1[i - 1])
                    align2.append(seq2[j - 1])
                    i -= 1
                    j -= 1
                    continue
            if i > 0 and (j == 0 or score[i][j] == score[i - 1][j] - 2):
                align1.append(seq1[i - 1])
                align2.append(".")
                i -= 1
            else:
                align1.append(".")
                align2.append(seq2[j - 1])
                j -= 1

        raw1, raw2 = "".join(align1)[::-1], "".join(align2)[::-1]
        return coalesce_orphan_voids(raw1, raw2, min_k=min_k)

    # Fast banded dynamic programming for larger sequences
    k = max(band, abs(L1 - L2) + 6)
    w = 2 * k + 1
    NEG_INF = -10**9
    dp = [[NEG_INF] * w for _ in range(L1 + 1)]
    dp[0][k] = 0

    for i in range(1, min(L1 + 1, k + 1)):
        dp[i][0 - i + k] = -2 * i
    for j in range(1, min(L2 + 1, k + 1)):
        dp[0][j + k] = -2 * j

    for i in range(1, L1 + 1):
        j_min = max(1, i - k)
        j_max = min(L2, i + k)
        for j in range(j_min, j_max + 1):
            offset = j - i + k
            m_score = 2 if is_wc_pair(seq1[i - 1], seq2[j - 1]) else -1
            diag = dp[i - 1][offset] + m_score if offset < w else NEG_INF
            up = dp[i - 1][offset + 1] - 2 if (offset + 1) < w else NEG_INF
            left = dp[i][offset - 1] - 2 if (offset - 1) >= 0 else NEG_INF
            dp[i][offset] = max(diag, up, left)

    align1, align2 = [], []
    i, j = L1, L2
    while i > 0 or j > 0:
        offset = j - i + k
        if i > 0 and j > 0:
            m_score = 2 if is_wc_pair(seq1[i - 1], seq2[j - 1]) else -1
            if offset < w and dp[i][offset] == dp[i - 1][offset] + m_score:
                align1.append(seq1[i - 1])
                align2.append(seq2[j - 1])
                i -= 1
                j -= 1
                continue
        if i > 0 and (j == 0 or (offset + 1 < w and dp[i][offset] == dp[i - 1][offset + 1] - 2)):
            align1.append(seq1[i - 1])
            align2.append(".")
            i -= 1
        elif j > 0:
            align1.append(".")
            align2.append(seq2[j - 1])
            j -= 1
        else:
            break

    raw1, raw2 = "".join(align1)[::-1], "".join(align2)[::-1]
    return coalesce_orphan_voids(raw1, raw2, min_k=min_k)


def coalesce_orphan_voids(aln1: str, aln2: str, min_k: int = 5) -> tuple[str, str]:
    """Eliminate orphan matches of length < min_k bp scattered across voids.

    In any unaligned region between solid stems (>= min_k), bases are kept contiguous
    without scattered micro-dots, and the length difference is padded with a clean contiguous void block.
    """
    L = len(aln1)
    if L == 0:
        return "", ""

    is_solid = [False] * L
    i = 0
    while i < L:
        if is_wc_pair(aln1[i], aln2[i]):
            start = i
            while i < L and is_wc_pair(aln1[i], aln2[i]):
                i += 1
            if i - start >= min_k:
                for idx in range(start, i):
                    is_solid[idx] = True
        else:
            i += 1

    out1, out2 = [], []
    i = 0
    while i < L:
        if is_solid[i]:
            out1.append(aln1[i])
            out2.append(aln2[i])
            i += 1
        else:
            start = i
            while i < L and not is_solid[i]:
                i += 1
            sub1 = aln1[start:i].replace(".", "")
            sub2 = aln2[start:i].replace(".", "")

            len1, len2 = len(sub1), len(sub2)
            if len1 == len2:
                pad1 = sub1
                pad2 = sub2
            elif len1 < len2:
                pad1 = sub1 + ("." * (len2 - len1))
                pad2 = sub2
            else:
                pad1 = sub1
                pad2 = sub2 + ("." * (len1 - len2))

            out1.append(pad1)
            out2.append(pad2)

    return "".join(out1), "".join(out2)


def align_loops_wc(seq1: str, seq2: str, min_k: int = 5) -> tuple[str, str]:
    """Watson-Crick loop/interisland alignment: global DP void optimization maximizing whole-loop complementarity."""
    if not seq1 and not seq2:
        return "", ""
    width = max(len(seq1), len(seq2))

    aln1, aln2 = align_islands_wc(seq1, seq2, min_k=min_k)
    pad1, pad2 = center_pad(seq1, width), center_pad(seq2, width)
    m_aln = sum(1 for a, b in zip(aln1, aln2) if is_wc_pair(a, b))
    m_pad = sum(1 for a, b in zip(pad1, pad2) if is_wc_pair(a, b))
    if m_aln >= m_pad:
        return aln1, aln2
    return pad1, pad2


def pairline(a: str, b: str) -> str:
    """Generate Watson-Crick bond line ('|' for WC pairs, ' ' otherwise)."""
    return "".join("|" if is_wc_pair(x, y) else " " for x, y in zip(a, b))


def format_alignment(
    top: str,
    bonds: str,
    bot: str,
    start: int,
    end: int,
    width: int = 60,
) -> str:
    """Format folded 3-line alignment into wrapped blocks with coordinate headers."""
    lines = []
    total = max(len(top), len(bonds), len(bot))
    top = top.ljust(total)
    bonds = bonds.ljust(total)
    bot = bot.ljust(total)

    for i in range(0, total, width):
        t_sub = top[i : i + width]
        m_sub = bonds[i : i + width]
        b_sub = bot[i : i + width]
        lines.append(f"5'-3' {t_sub}")
        lines.append(f"      {m_sub}")
        lines.append(f"3'-5' {b_sub}\n")
    return "\n".join(lines).rstrip()
