"""Canonical legacy scientific reference implementation."""
from __future__ import annotations

import re


def get_reverse_complement(seq: str) -> str:
    complement_map = str.maketrans("ACGTNacgtn", "TGCANtgcan")
    return seq.translate(complement_map)[::-1]


def calculate_score(seq1: str, seq2_rc: str) -> float:
    if not seq1 or not seq2_rc or len(seq1) != len(seq2_rc):
        return 0.0
    matches = sum(1 for a, b in zip(seq1.upper(), seq2_rc.upper()) if a == b and a in "ACGT")
    return matches / len(seq1)


def is_wc_pair(a: str, b: str) -> bool:
    if a == "." or b == ".":
        return False
    a, b = a.upper(), b.upper()
    return (a == "A" and b == "T") or (a == "T" and b == "A") or (a == "C" and b == "G") or (a == "G" and b == "C")


def align_islands_wc(seq1: str, seq2: str) -> tuple[str, str]:
    """Dynamic Programming optimized for Watson-Crick pairing."""
    L1, L2 = len(seq1), len(seq2)
    if L1 == L2 and calculate_score(seq1, get_reverse_complement(seq2)) == 1.0:
        return seq1, seq2

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

    return "".join(align1)[::-1], "".join(align2)[::-1]
