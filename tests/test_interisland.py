"""Tests for optimal 5-mer interisland alignment and internal branching classification."""
import unittest
from gregori.engine.interisland import (
    scan_wc_kmers,
    extend_match,
    chain_non_crossing_blocks,
    align_interisland_optimal_5mer,
    align_interisland_hierarchical,
    scan_self_complementarity,
    classify_internal_branching,
)
from gregori.engine.alignment import is_wc_pair


class TestInterislandMatching(unittest.TestCase):
    def test_5mer_scan_and_extend_with_3_mismatch_cutoff(self):
        target1 = "AAA" + "ACGTACGT" + "TTT"
        target2 = "AAA" + "TGCATGCA" + "TTT"
        seeds = scan_wc_kmers(target1, target2, k=5)
        self.assertGreater(len(seeds), 0)

        l1, r1, l2, r2 = extend_match(target1, target2, start1=3, start2=3, k=5, max_consecutive_mismatches=3)
        # Cut before 3 consecutive mismatches at left and right
        self.assertEqual(l1, 3)
        self.assertEqual(r1, 11)
        self.assertEqual(target1[l1:r1], "ACGTACGT")

    def test_non_crossing_max_score_chaining(self):
        # 3 blocks where block 2 crosses block 1
        b1 = {"start1": 0, "end1": 10, "start2": 0, "end2": 10, "score": 20}
        b2_cross = {"start1": 12, "end1": 20, "start2": 5, "end2": 13, "score": 15}  # Crosses b1 (start2 < end2 of b1)
        b2_valid = {"start1": 12, "end1": 20, "start2": 12, "end2": 20, "score": 15}  # Valid collinear
        b3 = {"start1": 25, "end1": 35, "start2": 25, "end2": 35, "score": 20}

        chain = chain_non_crossing_blocks([b1, b2_cross, b2_valid, b3])
        self.assertEqual(len(chain), 3)
        self.assertEqual(chain[0]["start1"], 0)
        self.assertEqual(chain[1]["start1"], 12)
        self.assertEqual(chain[2]["start1"], 25)

    def test_optimal_5mer_interisland_alignment_with_clean_orphans(self):
        seq1 = "AAAAAAAA" + "CGT" + "GGGGG"
        seq2 = "TTTTTTTT" + "A" + "CCCCC"

        aln1, aln2 = align_interisland_optimal_5mer(seq1, seq2, min_k=5)
        self.assertEqual(len(aln1), len(aln2))
        wc_count = sum(1 for a, b in zip(aln1, aln2) if is_wc_pair(a, b))
        self.assertGreaterEqual(wc_count, 13)
        # Ensure no scattered micro-dots
        self.assertNotIn("..a.", aln1)
        self.assertNotIn("..a.", aln2)

        aln1, aln2 = align_interisland_hierarchical(seq1, seq2, max_k=10, min_k=4)
        self.assertEqual(len(aln1), len(aln2))
        wc_count = sum(1 for a, b in zip(aln1, aln2) if is_wc_pair(a, b))
        # Both Block 1 (8) and Block 2 (5) should be aligned (at least 13 WC pairs)
        self.assertGreaterEqual(wc_count, 13)


class TestInternalBranchingClassification(unittest.TestCase):
    def test_double_branch(self):
        # Two independent, disjoint hairpins:
        # Hairpin 1: ACGT....ACGT_RC (= ACGT....ACGT)
        # Hairpin 2: GGCC....GGCC_RC (= GGCC....GGCC)
        # e.g. "ACGTaaaaACGT" (A pairs with T) -> "ACGTaaaaACGT"
        stem1 = "ACGT" + "aaaa" + "ACGT"  # ACGT vs ACGT: A-T, C-G, G-C, T-A when reverse complement is ACGT
        stem2 = "GGCC" + "tttt" + "GGCC"
        spacer = "NNNNNN"
        seq = stem1 + spacer + stem2

        res = classify_internal_branching(seq, min_stem=4)
        self.assertEqual(res["topology"], "double_branch")
        self.assertGreaterEqual(res["stems_count"], 2)

    def test_single_branch(self):
        # Single hairpin
        seq = "ACGT" + "aaaa" + "ACGT"
        res = classify_internal_branching(seq, min_stem=4)
        self.assertEqual(res["topology"], "single_branch")

    def test_sliding_branch_pseudoknot(self):
        # Crossed pairing / pseudoknot:
        # Arm 1A (ACGT) ... Arm 2A (GGCC) ... Arm 1B (ACGT_rc) ... Arm 2B (GGCC_rc)
        seq = "ACGT" + "NNN" + "GGCC" + "NNN" + "ACGT" + "NNN" + "GGCC"
        res = classify_internal_branching(seq, min_stem=4)
        self.assertEqual(res["topology"], "sliding_branch")

    def test_find_internal_hairpin_branches_multi_branch(self):
        from gregori.engine.interisland import find_internal_hairpin_branches
        # Hairpin 1: ACGTACGT....ACGTACGT (8 bp stem)
        h1 = "ACGTACGT" + "tttt" + "ACGTACGT"
        spacer = "AAAAAAAAAA"
        # Hairpin 2: GCGCCGCG....CGCGGCGC (8 bp stem)
        h2 = "GCGCCGCG" + "tttt" + "CGCGGCGC"
        seq = h1 + spacer + h2

        branches = find_internal_hairpin_branches(seq, min_stem=5)
        self.assertGreaterEqual(len(branches), 2)
        self.assertGreaterEqual(branches[0]["stem_length"], 8)
        self.assertGreaterEqual(branches[0]["score"], 0.80)

    def test_analyze_shane_branching(self):
        from gregori.engine.interisland import analyze_shane_branching
        # Outer island 5p: ACGTACGTACGT, 3p: ACGTACGTACGT
        # Inner loop: contains internal hairpin
        outer_5p = "ACGTACGTACGT"
        hairpin = "AAAAACCCCC" + "tttt" + "GGGGGTTTTT"
        outer_3p = "ACGTACGTACGT"
        seq = outer_5p + hairpin + outer_3p
        islands = [{"s_start": 0, "s_end": 12, "h_start": len(outer_5p) + len(hairpin), "h_end": len(seq)}]

        res = analyze_shane_branching(seq, islands, shane_start=1000000, min_stem=5)
        self.assertEqual(res["topology"], "single_branch")
        self.assertEqual(res["branch_count"], 1)
        self.assertEqual(res["branches"][0]["location"], "Central Loop")
        self.assertEqual(res["branches"][0]["genomic_arm5_start"], 1000012)
        self.assertIn("5' AAAAACCCCC", res["branching_alignment"])


if __name__ == "__main__":
    unittest.main()
