"""NCBI Datasets CLI and REST API integration for assembly metadata and sequence retrieval."""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


def natural_key(text: str) -> list[int | str]:
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", str(text))]


def check_ncbi_tools() -> dict[str, Any]:
    """Check availability of bundled or system NCBI binaries."""
    ds = resolve_binary("datasets")
    df = resolve_binary("dataformat")
    return {
        "datasets": str(ds) if ds else None,
        "dataformat": str(df) if df else None,
        "ready": bool(ds),
    }


def install_ncbi_tools() -> dict[str, Any]:
    """Download and install NCBI datasets + dataformat CLI binaries for this platform."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if "windows" in system:
        os_dir = "windows-x64"
        suffix = ".exe"
        base_url = "https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/windows-amd64/"
    elif "linux" in system:
        os_dir = "linux-x64"
        suffix = ""
        base_url = "https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/"
    elif "arm" in machine or "aarch" in machine:
        os_dir = "macos-arm64"
        suffix = ""
        base_url = "https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/mac_arm64/"
    else:
        os_dir = "macos-x64"
        suffix = ""
        base_url = "https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/mac_amd64/"

    root = Path(__file__).resolve().parents[2]
    bin_dir = root / "bin" / os_dir
    bin_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, Any] = {}
    for tool in ("datasets", "dataformat"):
        dest = bin_dir / f"{tool}{suffix}"
        url = f"{base_url}{tool}{suffix}"
        if dest.is_file() and dest.stat().st_size > 0:
            results[tool] = {"status": "already_installed", "path": str(dest)}
            continue
        try:
            import urllib.request as _req
            tmp = dest.with_suffix(".tmp")
            _req.urlretrieve(url, str(tmp))
            tmp.replace(dest)
            if suffix == "":
                os.chmod(dest, 0o755)
            results[tool] = {"status": "installed", "path": str(dest)}
        except Exception as exc:
            results[tool] = {"status": "error", "error": str(exc)}

    status = check_ncbi_tools()
    return {"tools": results, "ready": status["ready"], "datasets": status["datasets"], "dataformat": status["dataformat"]}


def resolve_binary(name: str) -> Path | None:
    """Locate bundled CLI binary in bin/ directory or on system PATH."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    os_dir = "windows-x64" if "windows" in system else "linux-x64" if "linux" in system else "macos-arm64" if "arm" in machine or "aarch" in machine else "macos-x64"
    exe_name = f"{name}.exe" if "windows" in system else name

    root = Path(__file__).resolve().parents[2]
    bundled = root / "bin" / os_dir / exe_name
    if bundled.is_file() and os.access(bundled, os.X_OK | os.R_OK):
        return bundled

    which = shutil.which(name)
    return Path(which) if which else None


def run_ncbi_tool(name: str, args: list[str], timeout: int = 120) -> str:
    """Execute an NCBI tool (datasets, dataformat) and return stdout."""
    bin_path = resolve_binary(name)
    if not bin_path:
        raise FileNotFoundError(
            f"NCBI tool '{name}' could not be located in bin/ or PATH."
        )

    cmd = [str(bin_path)] + args
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"NCBI command {' '.join(cmd)} failed (exit {proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout


def search_ncbi_assemblies(query: str, limit: int = 30) -> list[dict[str, Any]]:
    """Search NCBI Genome assemblies by species taxon or accession."""
    query = query.strip()
    if not query:
        return []

    # Check if direct accession
    if query.startswith(("GCF_", "GCA_")):
        args = ["summary", "genome", "accession", query, "--as-json-lines"]
    else:
        args = ["summary", "genome", "taxon", query, "--as-json-lines", "--limit", str(limit)]

    try:
        raw_output = run_ncbi_tool("datasets", args)
    except Exception as e:
        # Fallback to direct REST API if binary invocation fails
        return search_ncbi_assemblies_rest(query, limit)

    results = []
    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            reports = data.get("reports") or [data] if "accession" in data else []
            for item in reports:
                acc = item.get("accession")
                if not acc:
                    continue
                org = item.get("organism", {})
                info = item.get("assembly_info", {})
                source = "RefSeq" if acc.startswith("GCF_") else "GenBank"
                results.append({
                    "accession": acc,
                    "species": org.get("organism_name") or org.get("common_name") or "Unknown",
                    "tax_id": org.get("tax_id"),
                    "assembly_name": info.get("assembly_name") or acc,
                    "assembly_level": info.get("assembly_level", "Unknown"),
                    "source": source,
                    "release_date": info.get("release_date"),
                })
        except Exception:
            continue
    return results[:limit]


def search_ncbi_assemblies_rest(query: str, limit: int = 30) -> list[dict[str, Any]]:
    """REST API fallback for querying NCBI datasets."""
    encoded = urllib.parse.quote(query)
    url = f"https://api.ncbi.nlm.nih.gov/datasets/v2/genome/taxon/{encoded}/dataset_report?page_size={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "GReGOrI/0.5"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            reports = data.get("reports", [])
            results = []
            for item in reports:
                acc = item.get("accession")
                if not acc:
                    continue
                org = item.get("organism", {})
                info = item.get("assembly_info", {})
                results.append({
                    "accession": acc,
                    "species": org.get("organism_name") or "Unknown",
                    "tax_id": org.get("tax_id"),
                    "assembly_name": info.get("assembly_name") or acc,
                    "assembly_level": info.get("assembly_level", "Unknown"),
                    "source": "RefSeq" if acc.startswith("GCF_") else "GenBank",
                    "release_date": info.get("release_date"),
                })
            return results
    except Exception:
        return []


def get_assembly_sequence_summary(accession: str) -> list[dict[str, Any]]:
    """Extract chromosome and sequence hierarchy directly via datasets report."""
    args = ["summary", "genome", "accession", accession, "--report", "sequence", "--as-json-lines"]
    raw = run_ncbi_tool("datasets", args, timeout=60)
    sequences = []

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
            acc = item.get("refseq_accession") or item.get("genbank_accession") or item.get("accession")
            if not acc:
                continue

            chr_name = item.get("chr_name") or item.get("chromosome_name") or ""
            role = item.get("role") or ""
            loc_type = item.get("assigned_molecule_location_type") or ""
            length_bp = int(item.get("length") or 0)

            # Explicit classification: Chromosomes (including assigned/unlocalized scaffolds), Mitochondrial, Unplaced
            is_mito = loc_type.lower() == "mitochondrion" or chr_name.upper() in {"MT", "MITO", "MITOCHONDRION", "M"}
            is_chrom = not is_mito and bool(chr_name) and chr_name.lower() not in {"unplaced", "na", "none", "un", ""} and "unplaced" not in role.lower()

            if is_mito:
                group = "Mitochondrial"
                category = "mitochondrion"
                display = "MT"
                clean_chr = "MT"
            elif is_chrom:
                is_primary = (role == "assembled-molecule" or role.lower() == "chromosome")
                group = "Chromosomes"
                category = "chromosome" if is_primary else "unlocalized"
                display = chr_name if is_primary else acc
                clean_chr = chr_name
            else:
                group = "Unplaced Scaffolds & Contigs"
                category = "unplaced"
                display = acc
                clean_chr = "Scaffold"

            header = f"{acc} {clean_chr} ({role})" if clean_chr != "Scaffold" and display != clean_chr else (f"{acc} {display} ({role})" if display != acc else f"{acc} ({role})")
            sequences.append({
                "accession": acc,
                "refseq_accession": item.get("refseq_accession"),
                "genbank_accession": item.get("genbank_accession"),
                "header": header,
                "display_name": display,
                "chr_name": clean_chr,
                "length_bp": length_bp,
                "group": group,
                "category": category,
                "role": role,
                "is_chromosome": is_chrom,
                "is_primary": is_chrom and (role == "assembled-molecule" or role.lower() == "chromosome"),
                "is_mitochondrion": is_mito,
                "is_unplaced": not is_chrom and not is_mito,
                "sort_order": item.get("sort_order", 999),
            })
        except Exception:
            continue

    def seq_sort_key(s):
        if s["is_chromosome"]:
            grp_rank = 0
        elif s["is_mitochondrion"]:
            grp_rank = 1
        else:
            grp_rank = 2
        name = s.get("chr_name", "").upper()
        if name.startswith("LG") and name[2:].isdigit():
            ch_rank = (0, int(name[2:]), "")
        elif name.isdigit():
            ch_rank = (0, int(name), "")
        elif name in {"X", "Y", "Z", "W"}:
            ch_rank = (2, 0, name)
        elif name in {"MT", "MITO", "MITOCHONDRION", "M"}:
            ch_rank = (3, 0, name)
        else:
            ch_rank = (1, 0, natural_key(name))
        primary_rank = 0 if s.get("is_primary") else 1
        return (grp_rank, ch_rank, primary_rank, -s["length_bp"])

    sequences.sort(key=seq_sort_key)
    return sequences


def download_ncbi_package(accession: str, cache_dir: str | Path) -> dict[str, Any]:
    """Download full genomic FASTA, GFF3 gene annotations, and sequence report."""
    cache = Path(cache_dir) / accession
    archive = cache / "ncbi_dataset.zip"
    data = cache / "dataset"
    cache.mkdir(parents=True, exist_ok=True)

    if not archive.exists() or archive.stat().st_size == 0:
        try:
            run_ncbi_tool(
                "datasets",
                ["download", "genome", "accession", accession, "--include", "genome,gff3,seq-report", "--filename", str(archive)],
                timeout=1200,
            )
        except Exception:
            # Fallback if GFF3 is unavailable
            run_ncbi_tool(
                "datasets",
                ["download", "genome", "accession", accession, "--include", "genome,seq-report", "--filename", str(archive)],
                timeout=1200,
            )

    if not data.exists() or not list(data.glob("*")):
        with zipfile.ZipFile(archive) as package:
            package.extractall(data)

    fasta_files = list(data.rglob("*.fna")) + list(data.rglob("*.fa"))
    fasta = fasta_files[0] if fasta_files else None

    # Search for all GFF/GFF3 extensions (gff, gff3, gff.gz, gff3.gz)
    gff_patterns = ("*.gff", "*.gff3", "*.gff.gz", "*.gff3.gz")
    gff_candidates = []
    for pat in gff_patterns:
        gff_candidates.extend(data.rglob(pat))

    gff = next((g for g in gff_candidates if "genomic" in g.name.lower()), None) or (gff_candidates[0] if gff_candidates else None)
    seq_reports = list(data.rglob("*sequence_report*.jsonl")) + list(data.rglob("*sequence_report*.tsv"))
    seqreport = seq_reports[0] if seq_reports else None

    if not fasta:
        raise RuntimeError(f"NCBI package for {accession} contains no genomic FASTA (.fna).")

    return {
        "fasta": str(fasta),
        "gff3": str(gff) if gff else None,
        "sequence_report": str(seqreport) if seqreport else None,
    }
