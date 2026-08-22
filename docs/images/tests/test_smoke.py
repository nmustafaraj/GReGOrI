"""End-to-end smoke test for GReGOrI discovery pipeline, library building, and browser generation."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gregori.annotation.gff import load_gene_map
from gregori.annotation.overlap import superimpose_genes_on_shanes
from gregori.browser.builder import build_browser, build_library
from gregori.engine.core import analyse_sequence, inspect_sequences


class TestSmoke(unittest.TestCase):
    def test_full_pipeline_with_gene_superimposition(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            # 1. Create synthetic FASTA with an inverted repeat
            fasta_path = tmp_path / "genome.fna"
            left = "ACGTACGTACGTACGTACGT" * 2
            right = "ACGTACGTACGTACGTACGT"[::-1] * 2
            seq = "A" * 100 + left + "C" * 40 + right + "T" * 100
            fasta_path.write_text(f">NC_000001.1 [organism=Felis catus]\n{seq}\n", encoding="utf-8")

            # 2. Inspect FASTA
            report = inspect_sequences([fasta_path])
            self.assertTrue(report["valid"])
            self.assertEqual(report["sequence_count"], 1)

            # 3. Create synthetic GFF3 gene map
            gff_path = tmp_path / "genes.gff3"
            gff_path.write_text(
                "##gff-version 3\n"
                "NC_000001.1\tRefSeq\tgene\t80\t220\t.\t+\t.\tID=gene-1;gene=KIT;Dbxref=GeneID:4820\n",
                encoding="utf-8"
            )
            gene_map = load_gene_map(gff_path)
            self.assertIn("NC_000001.1", gene_map)

            # 4. Stage 1: Core discovery
            hits, shanes = analyse_sequence(seq, step=10, lookahead=200, threshold=0.95)
            self.assertTrue(len(shanes) >= 1)

            # 5. Stage 2: Superimpose genes & enrich details
            from gregori.engine.core import enrich_shane_details
            superimpose_genes_on_shanes(shanes, gene_map, "NC_000001.1", "Felis catus")
            self.assertEqual(len(shanes[0]["genes"]), 1)
            self.assertEqual(shanes[0]["genes"][0]["symbol"], "KIT")
            for s in shanes:
                enrich_shane_details(seq, s, context_flank=50)

            # 6. Build Central Library & Browser
            project = {
                "project_path": str(tmp_path / "project"),
                "assembly_key": "GCF_000181335.3",
                "species": "Felis catus",
                "metadata": {},
                "source": "custom"
            }
            Path(project["project_path"]).mkdir()
            records_data = [{
                "chromosome": "A1",
                "display_name": "A1",
                "accession": "NC_000001.1",
                "length_bp": len(seq),
                "shanes": shanes,
            }]
            lib_file = build_library(project, records_data)
            self.assertTrue(lib_file.is_file())

            # 7. Build Browser HTML
            browser_file = build_browser(ROOT, lib_file)
            self.assertTrue(browser_file.is_file())
            html_content = browser_file.read_text(encoding="utf-8")
            self.assertIn("Browser", html_content)


if __name__ == "__main__":
    unittest.main()
