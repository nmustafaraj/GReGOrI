"""Unit tests for gene annotation, GFF3 parsing, and overlap calculation."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gregori.annotation.gff import inspect_gff, load_gene_map, parse_attributes
from gregori.annotation.overlap import find_overlapping_genes, superimpose_genes_on_shanes


class TestAnnotation(unittest.TestCase):
    def test_parse_attributes(self):
        attrs = parse_attributes("ID=gene-KIT;Dbxref=GeneID:4820;gene=KIT;gene_biotype=protein_coding")
        self.assertEqual(attrs.get("ID"), "gene-KIT")
        self.assertEqual(attrs.get("gene"), "KIT")
        self.assertEqual(attrs.get("gene_biotype"), "protein_coding")

    def test_load_gene_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "test.gff3"
            p.write_text(
                "##gff-version 3\n"
                "NC_000001.1\tRefSeq\tgene\t100\t500\t.\t+\t.\tID=gene-1;gene=BRCA1;GeneID:1001\n"
                "NC_000001.1\tRefSeq\tpseudogene\t600\t800\t.\t-\t.\tID=gene-2;gene=BRCA2P;GeneID:1002\n",
                encoding="utf-8"
            )
            genes = load_gene_map(p)
            self.assertIn("NC_000001.1", genes)
            self.assertEqual(len(genes["NC_000001.1"]), 2)
            self.assertEqual(genes["NC_000001.1"][0]["symbol"], "BRCA1")

    def test_load_gene_map_deduplication(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "isoforms.gff3"
            p.write_text(
                "##gff-version 3\n"
                "NC_000001.1\tRefSeq\tgene\t1000\t5000\t.\t+\t.\tID=gene-ABC1;Dbxref=GeneID:12345;gene=ABC1;gene_biotype=protein_coding\n"
                "NC_000001.1\tRefSeq\tmRNA\t1000\t5000\t.\t+\t.\tID=rna-ABC1-1;Parent=gene-ABC1;Dbxref=GeneID:12345;gene=ABC1\n"
                "NC_000001.1\tRefSeq\tmRNA\t1000\t4500\t.\t+\t.\tID=rna-ABC1-2;Parent=gene-ABC1;Dbxref=GeneID:12345;gene=ABC1\n"
                "NC_000001.1\tRefSeq\tmRNA\t1200\t5000\t.\t+\t.\tID=rna-ABC1-3;Parent=gene-ABC1;Dbxref=GeneID:12345;gene=ABC1\n"
                "NC_000001.1\tRefSeq\texon\t1000\t1500\t.\t+\t.\tID=exon-1;Parent=rna-ABC1-1\n",
                encoding="utf-8"
            )
            genes = load_gene_map(p)
            self.assertEqual(len(genes["NC_000001.1"]), 1)
            self.assertEqual(genes["NC_000001.1"][0]["symbol"], "ABC1")
            self.assertEqual(genes["NC_000001.1"][0]["gene_id"], "12345")

    def test_find_overlapping_genes(self):
        seq_genes = [
            {"start": 100, "end": 500, "strand": "+", "gene_id": "101", "symbol": "GENE1", "biotype": "protein_coding"},
            {"start": 600, "end": 900, "strand": "-", "gene_id": "102", "symbol": "GENE2", "biotype": "lncRNA"},
        ]
        # Overlapping with GENE1
        ov = find_overlapping_genes(seq_genes, 200, 300, species="Test")
        self.assertEqual(len(ov), 1)
        self.assertEqual(ov[0]["symbol"], "GENE1")
        self.assertEqual(ov[0]["relationship"], "SHaNE_contained_in_gene")

        # Overlapping with GENE2
        ov2 = find_overlapping_genes(seq_genes, 550, 700, species="Test")
        self.assertEqual(len(ov2), 1)
        self.assertEqual(ov2[0]["symbol"], "GENE2")
        self.assertEqual(ov2[0]["relationship"], "partial_overlap_right")

    def test_superimpose_genes(self):
        genes_by_chrom = {
            "NC_1": [{"start": 100, "end": 300, "strand": "+", "gene_id": "1", "symbol": "G1", "biotype": "gene"}]
        }
        shanes = [{"start": 50, "end": 400, "islands": []}]
        superimpose_genes_on_shanes(shanes, genes_by_chrom, "NC_1", "Test")
        self.assertEqual(len(shanes[0]["genes"]), 1)
        self.assertEqual(shanes[0]["genes"][0]["symbol"], "G1")
        self.assertEqual(shanes[0]["genes"][0]["relationship"], "gene_contained_in_SHaNE")


    def test_get_assembly_sequence_summary(self):
        from unittest.mock import patch
        from gregori.annotation.ncbi import get_assembly_sequence_summary

        mock_jsonl = (
            '{"assembly_accession":"GCF_018350175.1","assigned_molecule_location_type":"Chromosome","chr_name":"A1","genbank_accession":"CM031412.1","length":239367248,"refseq_accession":"NC_058368.1","role":"assembled-molecule","sort_order":1}\n'
            '{"assembly_accession":"GCF_018350175.1","assigned_molecule_location_type":"Chromosome","chr_name":"A1","genbank_accession":"NW0001.1","length":50000,"refseq_accession":"NW_0001.1","role":"unlocalized-scaffold","sort_order":2}\n'
            '{"assembly_accession":"GCF_018350175.1","assigned_molecule_location_type":"Chromosome","chr_name":"X","genbank_accession":"CM031429.1","length":126427096,"refseq_accession":"NC_058385.1","role":"assembled-molecule","sort_order":19}\n'
            '{"assembly_accession":"GCF_018350175.1","assigned_molecule_location_type":"Mitochondrion","chr_name":"MT","genbank_accession":"U20753.1","length":17009,"refseq_accession":"NC_001700.1","role":"assembled-molecule","sort_order":21}\n'
            '{"assembly_accession":"GCF_018350175.1","assigned_molecule_location_type":"na","chr_name":"","genbank_accession":"NW0002.1","length":20000,"refseq_accession":"NW_0002.1","role":"unplaced-scaffold","sort_order":9999}\n'
        )
        with patch("gregori.annotation.ncbi.run_ncbi_tool", return_value=mock_jsonl):
            seqs = get_assembly_sequence_summary("GCF_018350175.1")
            self.assertEqual(len(seqs), 5)
            # Primary chromosome A1
            self.assertEqual(seqs[0]["accession"], "NC_058368.1")
            self.assertEqual(seqs[0]["group"], "Chromosomes")
            self.assertEqual(seqs[0]["chr_name"], "A1")
            self.assertEqual(seqs[0]["display_name"], "A1")
            self.assertTrue(seqs[0]["is_chromosome"])
            self.assertTrue(seqs[0]["is_primary"])
            # Unlocalized scaffold belonging to A1
            self.assertEqual(seqs[1]["accession"], "NW_0001.1")
            self.assertEqual(seqs[1]["group"], "Chromosomes")
            self.assertEqual(seqs[1]["chr_name"], "A1")
            self.assertEqual(seqs[1]["display_name"], "NW_0001.1")
            self.assertTrue(seqs[1]["is_chromosome"])
            self.assertFalse(seqs[1]["is_primary"])
            self.assertEqual(seqs[1]["category"], "unlocalized")
            # Chromosome X
            self.assertEqual(seqs[2]["group"], "Chromosomes")
            self.assertEqual(seqs[2]["chr_name"], "X")
            # Mitochondrial
            self.assertEqual(seqs[3]["group"], "Mitochondrial")
            self.assertEqual(seqs[3]["display_name"], "MT")
            # Truly unplaced scaffold
            self.assertEqual(seqs[4]["accession"], "NW_0002.1")
            self.assertEqual(seqs[4]["group"], "Unplaced Scaffolds & Contigs")
            self.assertEqual(seqs[4]["category"], "unplaced")
            self.assertFalse(seqs[4]["is_chromosome"])
            self.assertTrue(seqs[4]["is_unplaced"])

    def test_sequence_report_scaffold_grouping(self):
        import tempfile
        from gregori.palaces.sequence_report import load as load_seq_report, fallback as fallback_seq_record

        csv_content = (
            "Sequence-Name\tSequence-Role\tAssigned-Molecule\tRefSeq-Accn\tLength\n"
            "LG1\tassembled-molecule\tLG1\tNC_037638.1\t27754200\n"
            "NW_020555788.1\tunlocalized-scaffold\tLG2\tNW_020555788.1\t3988\n"
            "NW_020555859.1\tunplaced-scaffold\tna\tNW_020555859.1\t486754\n"
        )
        with tempfile.NamedTemporaryFile("w+", suffix=".tsv", delete=False, encoding="utf-8") as tf:
            tf.write(csv_content)
            tf.flush()
            tpath = tf.name

        report = load_seq_report(tpath)
        self.assertEqual(report["NC_037638.1"]["chromosome_group"], "LG1")
        self.assertEqual(report["NC_037638.1"]["display_name"], "LG1")
        self.assertTrue(report["NC_037638.1"]["is_chromosome"])

        # Unlocalized scaffold NW_020555788.1 belongs to LG2
        self.assertEqual(report["NW_020555788.1"]["chromosome_group"], "LG2")
        self.assertEqual(report["NW_020555788.1"]["display_name"], "NW_020555788.1")
        self.assertTrue(report["NW_020555788.1"]["is_chromosome"])

        # Unplaced scaffold NW_020555859.1
        self.assertEqual(report["NW_020555859.1"]["chromosome_group"], "Unplaced")
        self.assertEqual(report["NW_020555859.1"]["display_name"], "NW_020555859.1")
        self.assertFalse(report["NW_020555859.1"]["is_chromosome"])


if __name__ == "__main__":
    unittest.main()
