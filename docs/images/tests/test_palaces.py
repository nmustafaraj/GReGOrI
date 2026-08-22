"""Unit tests for Palaces Enterprise architecture: Identity, Naming, Rich Library, and Reports."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gregori.palaces.identity import stable_id
from gregori.palaces.naming import barcode, legacy_name
from gregori.palaces.rich_library import build as build_rich_library
from gregori.palaces.sequence_report import load as load_seq_report


class TestPalaces(unittest.TestCase):
    def test_stable_identity(self):
        sid = stable_id("GCF_000181335.3", "NC_018723.3", 100, 500)
        self.assertEqual(sid, "GCF_000181335.3|NC_018723.3|100|500")

    def test_legacy_naming(self):
        name = legacy_name("Felis catus", "X", 270996)
        self.assertEqual(name, "Fc_SHaNE_X.2")

    def test_barcode(self):
        bc = barcode("GCF_1", "NC_1", 10, 20)
        self.assertTrue(bc.startswith("SHN-"))

    def test_sequence_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "report.tsv"
            p.write_text(
                "RefSeq accession\tSequence role\tAssigned molecule\tLength\n"
                "NC_000001.1\tassembled-molecule\t1\t10000\n"
                "NW_000002.1\tunlocalized-scaffold\tX\t500\n",
                encoding="utf-8"
            )
            report_data = load_seq_report(p)
            self.assertIn("NC_000001.1", report_data)
            self.assertEqual(report_data["NC_000001.1"]["chromosome_group"], "1")
            self.assertEqual(report_data["NW_000002.1"]["chromosome_group"], "X")

    def test_rich_library_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            project = {
                "project_path": str(tmp_path),
                "assembly_key": "GCF_TEST",
                "species": "Felis catus",
                "metadata": {},
                "source": "custom"
            }
            records = [{
                "accession": "NC_018723.3",
                "chromosome": "A1",
                "display_name": "A1",
                "length_bp": 1000,
                "shanes": [{
                    "start": 100,
                    "end": 300,
                    "islands": [{"s_start": 100, "s_end": 150, "h_start": 250, "h_end": 300}],
                    "genes": [{"symbol": "KIT", "gene_id": "4820", "overlap_bp": 50, "relationship": "partial_overlap"}],
                    "annotation_status": "annotated",
                    "details": {"context_sequence": "", "folded_alignment": "", "island_alignment": ""}
                }]
            }]
            lib_path = build_rich_library(project, records)
            self.assertTrue(lib_path.is_file())
            data = json.loads(lib_path.read_text(encoding="utf-8"))
            self.assertTrue(data["validation"]["ok"])
            self.assertEqual(len(data["shanes"]), 1)
            self.assertEqual(data["shanes"][0]["stable_id"], "GCF_TEST|NC_018723.3|100|300")


if __name__ == "__main__":
    unittest.main()
