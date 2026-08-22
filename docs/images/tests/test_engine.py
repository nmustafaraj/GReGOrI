"""Unit tests for the GReGOrI Core Engine and Watson-Crick dynamic programming alignments."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gregori.engine.alignment import (
    align_islands_wc,
    align_loops_wc,
    format_alignment,
    get_reverse_complement,
    is_wc_pair,
    pairline,
    rc,
    similarity,
)
from gregori.engine.core import (
    analyse_sequence,
    enforce_strict_nesting,
    expand_islands,
    group_hits,
    scan_seeds,
)


class TestAlignment(unittest.TestCase):
    def test_reverse_complement(self):
        self.assertEqual(rc("ACGTN"), "NACGT")
        self.assertEqual(get_reverse_complement("TGCAN"), "NTGCA")

    def test_wc_pairing(self):
        self.assertTrue(is_wc_pair("A", "T"))
        self.assertTrue(is_wc_pair("G", "C"))
        self.assertTrue(is_wc_pair("T", "A"))
        self.assertTrue(is_wc_pair("C", "G"))
        self.assertFalse(is_wc_pair("A", "A"))
        self.assertFalse(is_wc_pair("A", "."))

    def test_align_islands_wc(self):
        a, b = align_islands_wc("ACGT", "TGCA")
        self.assertEqual(len(a), len(b))
        self.assertEqual(pairline(a, b), "||||")

    def test_n_base_dead_regions(self):
        # 1. N bases cannot form Watson-Crick pairs
        self.assertFalse(is_wc_pair("N", "N"))
        self.assertFalse(is_wc_pair("N", "A"))
        self.assertFalse(is_wc_pair("N", "T"))
        self.assertFalse(is_wc_pair("N", "G"))
        self.assertFalse(is_wc_pair("N", "C"))
        self.assertFalse(is_wc_pair("A", "N"))

        # 2. calculate_score excludes N from matching
        self.assertEqual(similarity("NNNN", "NNNN"), 0.0)
        self.assertAlmostEqual(similarity("ACGTNN", "ACGTNN"), 4.0 / 6.0)

        # 3. pairline generates spaces for N bases
        self.assertEqual(pairline("ACGTNN", "TGCANN"), "||||  ")

    def test_format_alignment(self):
        txt = format_alignment("ACGT", "||||", "TGCA", 0, 4, width=60)
        lines = txt.splitlines()
        self.assertEqual(len(lines), 3)
        self.assertTrue("5'-3'" in lines[0])


    def test_align_loops_with_voids(self):
        # Test case 1 from user image: 'cccccacccccc' vs 'tagggggtgggggaa'
        s1 = "cccccacccccc"
        s2 = "tagggggtgggggaa"
        a1, a2 = align_loops_wc(s1, s2)
        pl = pairline(a1, a2)
        self.assertIn(".", a1 + a2)
        self.assertIn("|||||||||||", pl)

        # Test case 2 from user image: 'cctctccccctaatttctatatcctgaaata' vs 'gagagggattaaaagatataggactttataa'
        s3_1 = "cctctccccctaatttctatatcctgaaata"
        s3_2 = "gagagggattaaaagatataggactttataa"
        a3_1, a3_2 = align_loops_wc(s3_1, s3_2)
        pl3 = pairline(a3_1, a3_2)
        self.assertIn(".", a3_1 + a3_2)
        self.assertIn("||||||||||||||||||", pl3)


class TestDiscoveryEngine(unittest.TestCase):
    def test_scan_and_nesting(self):
        # Construct synthetic inverted repeat
        left = "ACGTACGTACGTACGTACGT"
        mid = "NNNNNNNNNNNNNNNNNNNN"
        right = rc(left)
        seq = "A" * 50 + left + mid + right + "T" * 50

        hits = scan_seeds(seq, step=10, lookahead=100)
        self.assertTrue(len(hits) >= 1)
        grouped = group_hits(hits)
        self.assertTrue(len(grouped) >= 1)

    def test_full_analysis(self):
        left = "ACGTACGTACGTACGTACGT" * 2
        right = rc(left)
        seq = "A" * 50 + left + "C" * 20 + right + "G" * 50
        hits, shanes = analyse_sequence(seq, step=10, lookahead=200, threshold=0.95)
        self.assertTrue(len(shanes) >= 1)
        self.assertGreaterEqual(shanes[0]["score"], 0.75)

    def test_maximized_score_and_dual_lengths(self):
        from gregori.engine.core import enrich_shane_details, generate_continuous_alignment
        left = "ACGTACGTACGTACGTACGT" * 2
        right = rc(left)
        seq = "A" * 50 + left + "C" * 20 + right + "G" * 50
        hits, shanes = analyse_sequence(seq, step=10, lookahead=200, threshold=0.95)
        self.assertTrue(len(shanes) >= 1)
        sh = shanes[0]
        details = enrich_shane_details(seq, sh, 500, "SHaNE_1")
        self.assertIn("genomic_length_bp", sh)
        self.assertIn("length_with_voids_bp", sh)
        self.assertIn("voids_count", sh)
        self.assertEqual(sh["genomic_length_bp"], sh["end"] - sh["start"])
        self.assertGreaterEqual(sh["length_with_voids_bp"], sh["genomic_length_bp"])
        self.assertGreaterEqual(sh["score"], 0.75)
        self.assertIn("central_loop_analysis", sh)
        self.assertTrue(sh["central_loop_analysis"]["has_central_loop"])

    def test_island_thermodynamics(self):
        from gregori.engine.thermodynamics import calculate_island_thermodynamics
        arm5 = "GCGCGCGCGC"
        arm3 = rc(arm5)
        res = calculate_island_thermodynamics(arm5, arm3)
        self.assertLess(res["delta_g_37_kcal"], -5.0)
        self.assertGreater(res["tm_celsius"], 50.0)
        self.assertTrue(res["is_stable"])

    def test_central_loop_analysis_and_evolutionary_hypothesis(self):
        from gregori.engine.thermodynamics import analyze_central_loop
        # A homopolymeric or non-complementary loop: "AAAAACCCCC"
        loop_seq = "AAAAACCCCC" * 5
        res = analyze_central_loop(loop_seq)
        self.assertTrue(res["has_central_loop"])
        self.assertGreater(res["loop_length_bp"], 0)
        self.assertIn(res["gc_spatial_uniformity"], ["Evenly Distributed", "Moderately Uniform", "Clustered / Patchy"])
        self.assertGreater(res["expected_random_wc_prob"], 0.0)
        self.assertTrue(res["evolved_to_remain_unfolded"])
        self.assertEqual(res["hypothesis_badge"], "Evolved to Remain Unfolded")

    def test_central_loop_n_exclusion(self):
        from gregori.engine.thermodynamics import analyze_central_loop
        loop_with_n = "AAAAACCCCCNNNNN" * 2
        res = analyze_central_loop(loop_with_n)
        self.assertFalse(res["has_central_loop"])
        self.assertTrue(res["has_n_bases"])
        self.assertTrue(res["contains_null_bases"])
        self.assertEqual(res["hypothesis_badge"], "Excluded (Contains N)")


if __name__ == "__main__":
    unittest.main()
