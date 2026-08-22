"""Unit tests for project lifecycle mutations (create, pause, resume, cancel, restart, rerun, delete)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import gregori.server.controller as ctrl


class TestLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.orig_projects = ctrl.PROJECTS
        self.orig_trash = ctrl.TRASH
        ctrl.PROJECTS = Path(self.tmp_dir.name) / "projects"
        ctrl.TRASH = Path(self.tmp_dir.name) / "trash"
        ctrl.setup_workspace()

    def tearDown(self):
        ctrl.PROJECTS = self.orig_projects
        ctrl.TRASH = self.orig_trash
        self.tmp_dir.cleanup()

    def test_job_lifecycle_mutations(self):
        # Create a mock job
        fasta = Path(self.tmp_dir.name) / "test.fna"
        fasta.write_text(">NC_1.1 [organism=Test species]\n" + "ACGT"*500 + "\n", encoding="utf-8")

        data = {
            "input_paths": [str(fasta)],
            "step": 1000,
            "lookahead": 20000,
            "threshold": 0.99,
        }
        manifest = ctrl.create_job(data, source="custom", launch=False)
        pid = manifest["project_id"]
        self.assertEqual(manifest["status"], "queued")

        # 1. Pause
        res = ctrl.mutate_project("pause", pid)
        self.assertEqual(res["status"], "pausing")

        # 2. Resume
        res = ctrl.mutate_project("resume", pid)
        self.assertEqual(res["status"], "analysing")

        # 3. Cancel
        res = ctrl.mutate_project("cancel", pid)
        self.assertEqual(res["status"], "cancelling")

        # 4. Restart cancelled/interrupted job
        ctrl.update_manifest(pid, status="interrupted")
        with patch("threading.Thread"):
            res = ctrl.mutate_project("restart", pid)
            self.assertEqual(res["status"], "queued")

        # 5. Delete in non-complete state
        del_res = ctrl.mutate_project("delete", pid)
        self.assertEqual(del_res["deleted"], pid)
        self.assertFalse((ctrl.PROJECTS / pid).exists())

        # 6. Re-create and restart the exact same job after deletion
        remake_manifest = ctrl.create_job(data, source="custom", launch=False)
        self.assertEqual(remake_manifest["project_id"], pid)
        self.assertEqual(remake_manifest["status"], "queued")
        self.assertTrue((ctrl.PROJECTS / pid).exists())

        # 7. Start job again while folder exists (clean reset without 'already exists' error)
        restart_manifest = ctrl.create_job(data, source="custom", launch=False)
        self.assertEqual(restart_manifest["project_id"], pid)
        self.assertEqual(restart_manifest["status"], "queued")

    def test_ncbi_job_creation(self):
        data = {
            "assembly_key": "GCF_018350175.1",
            "species": "Felis catus",
            "selected_sequences": ["NC_058368.1"],
            "step": 1000,
            "lookahead": 20000,
            "threshold": 0.99,
        }
        manifest = ctrl.create_job(data, source="ncbi", launch=False)
        self.assertEqual(manifest["source"], "ncbi")
        self.assertEqual(manifest["status"], "queued")
        self.assertEqual(manifest["species"], "Felis catus")
        self.assertEqual(manifest["assembly_key"], "GCF_018350175.1")


    def test_superimpose_genes_mutation(self):
        # Setup mock project with library
        fasta = Path(self.tmp_dir.name) / "test.fna"
        fasta.write_text(">NC_1.1 [organism=Test species]\n" + "ACGT"*500 + "\n", encoding="utf-8")
        data = {"input_paths": [str(fasta)], "step": 1000, "lookahead": 20000, "threshold": 0.99}
        manifest = ctrl.create_job(data, source="custom", launch=False)
        pid = manifest["project_id"]

        # Create mock library
        lib_dir = ctrl.PROJECTS / pid / "central_library"
        lib_dir.mkdir(parents=True, exist_ok=True)
        lib_data = {
            "library_format": "GReGOrI-SHaNE-Library",
            "assemblies": [{"species": "Test species", "accession": "NC_1.1", "name": "NC_1.1"}],
            "sequence_records": [{"sequence_accession": "NC_1.1", "display_name": "NC_1.1", "chromosome_group": "NC_1.1", "length_bp": 2000}],
            "shanes": [{
                "systematic_name": "Test_SHaNE_1",
                "stable_id": "sid_1",
                "sequence_accession": "NC_1.1",
                "coordinates": {"start": 100, "end": 500},
                "islands": [],
                "genes": [],
                "details": {},
            }],
        }
        (lib_dir / "GReGOrI_SHaNE_library.json").write_text(json.dumps(lib_data), encoding="utf-8")

        # Create mock GFF3
        gff3 = Path(self.tmp_dir.name) / "genes.gff3"
        gff3.write_text("NC_1.1\tRefSeq\tgene\t200\t400\t.\t+\t.\tID=gene1;gene=ABC1\n", encoding="utf-8")

        # Run superimpose-genes mutation
        res = ctrl.mutate_project("superimpose-genes", pid, gff3=str(gff3))
        self.assertEqual(res["summary"]["genes_crossed"], 1)
        self.assertEqual(res["card"]["genes_superimposed"], 1)
        self.assertEqual(res["card"]["gene_discovery_status"], "completed")

        # Verify updated library
        updated_lib = json.loads((lib_dir / "GReGOrI_SHaNE_library.json").read_text(encoding="utf-8"))
        shane = updated_lib["shanes"][0]
        self.assertEqual(len(shane["genes"]), 1)
    def test_rerun_resets_completed_bases_and_percent(self):
        fasta = Path(self.tmp_dir.name) / "test.fna"
        fasta.write_text(">NC_1.1 [organism=Test species]\n" + "ACGT"*500 + "\n", encoding="utf-8")
        data = {"input_paths": [str(fasta)], "step": 1000, "lookahead": 20000, "threshold": 0.99}
        manifest = ctrl.create_job(data, source="custom", launch=False)
        pid = manifest["project_id"]

        # Simulate complete state
        ctrl.update_manifest(pid, status="complete", completed_utc=ctrl.utc_now(), summary={"genome_size_bp": 2000, "sequences": 1, "shanes": 5})
        ctrl.update_card(pid, status="complete", completed_bases=2000, percent_complete=100.0, shanes_discovered=5)
        (ctrl.PROJECTS / pid / "events.jsonl").write_text('{"event": "job_complete"}\n', encoding="utf-8")

        card_before = ctrl.read_card(pid)
        self.assertEqual(card_before["status"], "complete")
        self.assertEqual(card_before["percent_complete"], 100.0)

        # Trigger Rerun
        with patch("threading.Thread"):
            ctrl.mutate_project("rerun", pid)

        # Verify card and manifest were cleanly reset
        card_after = ctrl.read_card(pid)
        self.assertEqual(card_after["status"], "queued")
        self.assertEqual(card_after["completed_bases"], 0)
        self.assertEqual(card_after["percent_complete"], 0.0)
        self.assertEqual(card_after["shanes_discovered"], 0)
        self.assertFalse((ctrl.PROJECTS / pid / "events.jsonl").exists())

    def test_safe_point_pause_card_sync(self):
        fasta = Path(self.tmp_dir.name) / "test.fna"
        fasta.write_text(">NC_1.1 [organism=Test species]\n" + "ACGT"*500 + "\n", encoding="utf-8")
        data = {"input_paths": [str(fasta)], "step": 1000, "lookahead": 20000, "threshold": 0.99}
        manifest = ctrl.create_job(data, source="custom", launch=False)
        pid = manifest["project_id"]

        control = ctrl.Control(pid)
        ctrl.FLAGS[pid] = {"pause": False, "cancel": False}

        # Normal safe_point
        control.safe_point({"phase": "test"})
        self.assertEqual(ctrl.read_manifest(pid)["status"], "queued")

    def test_custom_analysis_inspect_and_worker_execution(self):
        # Create a FASTA with quotes and spaces in path
        fasta = Path(self.tmp_dir.name) / "custom_sample.fasta"
        fasta.write_text(">scaffold_1 [organism=Apis mellifera]\n" + "ACGT"*600 + "\n", encoding="utf-8")

        # Test inspection
        rep = ctrl.inspect_sequences([f' "{str(fasta)}" '])
        self.assertTrue(rep["valid"])
        self.assertEqual(rep["file_count"], 1)
        self.assertEqual(rep["sequence_count"], 1)
        self.assertEqual(rep["species"], ["Apis mellifera"])

        # Create and execute job
        data = {
            "input_paths": rep["files"],
            "step": 1000,
            "lookahead": 20000,
            "threshold": 0.99,
            "species": "Apis mellifera",
        }
        manifest = ctrl.create_job(data, source="custom", launch=False)
        self.assertEqual(manifest["source"], "custom")

        # Execute worker
        ctrl.execute_worker(manifest["project_id"])
        finished = ctrl.read_manifest(manifest["project_id"])
        self.assertEqual(finished["status"], "complete")
        self.assertEqual(finished["summary"]["genome_size_bp"], 2400)


if __name__ == "__main__":
    unittest.main()
