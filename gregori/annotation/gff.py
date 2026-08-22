"""GFF3 and GTF gene annotation parsing and assembly validation."""
from __future__ import annotations

import gzip
import re
import urllib.parse
from collections import defaultdict
from pathlib import Path
from typing import Any

ACCESSION_RX = re.compile(r"GC[AF]_\d+\.\d+")


def open_text(path: str | Path):
    """Open plain or gzipped text file."""
    p = Path(path)
    if str(p).endswith(".gz"):
        return gzip.open(p, "rt", encoding="utf-8", errors="replace")
    return p.open("r", encoding="utf-8", errors="replace")


def parse_attributes(text: str) -> dict[str, str]:
    """Parse GFF3 (key=value) or GTF (key "value") attribute strings."""
    attrs = {}
    for part in text.strip().split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            key, value = part.split("=", 1)
            attrs[key.strip()] = urllib.parse.unquote(value.strip().strip('"'))
        elif " " in part:
            key, value = part.split(" ", 1)
            attrs[key.strip()] = urllib.parse.unquote(value.strip().strip('"'))
    return attrs


def extract_gene_id(attrs: dict[str, str]) -> str | None:
    """Extract standard NCBI or Ensembl Gene ID from attributes."""
    # Check Dbxref / dbxref for GeneID:xxxx
    for key in ("Dbxref", "dbxref", "db_xref"):
        val = attrs.get(key, "")
        match = re.search(r"(?:^|[,;])GeneID:(\d+)(?:[,;]|$)", val)
        if match:
            return match.group(1)
        match_ens = re.search(r"(?:^|[,;])Ensembl:([A-Za-z0-9_.-]+)(?:[,;]|$)", val)
        if match_ens:
            return match_ens.group(1)

    for key in ("GeneID", "gene_id"):
        val = attrs.get(key)
        if val and val != ".":
            return val

    # ID attribute if it represents a gene
    raw_id = attrs.get("ID", "")
    if raw_id.startswith("gene-"):
        return raw_id[5:]
    return raw_id if raw_id and raw_id != "." else None


def extract_symbol(attrs: dict[str, str]) -> str:
    """Extract gene symbol / name from attributes."""
    for key in ("gene", "gene_symbol", "Name", "symbol", "gene_name", "locus_tag"):
        val = attrs.get(key)
        if val and val != ".":
            return val
    return "."


def extract_locus_tag(attrs: dict[str, str]) -> str:
    """Extract locus tag from attributes."""
    return attrs.get("locus_tag") or attrs.get("old_locus_tag") or "."


def extract_biotype(attrs: dict[str, str], default_type: str = "gene") -> str:
    """Extract biotype (protein_coding, lncRNA, pseudogene, etc.)."""
    return (
        attrs.get("gene_biotype")
        or attrs.get("biotype")
        or attrs.get("gene_type")
        or default_type
    )


def extract_description(attrs: dict[str, str]) -> str:
    """Extract product or description."""
    return attrs.get("description") or attrs.get("product") or attrs.get("Note") or "."


def load_gene_map(gff_path: str | Path) -> dict[str, list[dict[str, Any]]]:
    """Parse a GFF3 or GTF file into a dictionary of deduplicated gene records keyed by seqid.
    
    Strictly parses primary 'gene' and 'pseudogene' features, ignoring mRNA/transcript sub-features
    to avoid multi-feature over-annotation duplicates.
    """
    if not gff_path or not Path(gff_path).is_file():
        return {}

    genes = defaultdict(list)
    seen_keys = set()
    found_primary_genes = False

    # Pass 1: Parse primary 'gene' and 'pseudogene' features
    with open_text(gff_path) as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) != 9:
                continue
            feature = cols[2].casefold()
            if feature not in {"gene", "pseudogene"}:
                continue
            
            found_primary_genes = True
            seqid = cols[0]
            try:
                start = int(cols[3]) - 1
                end = int(cols[4])
            except ValueError:
                continue
            if end <= start:
                continue

            strand = cols[6]
            attrs = parse_attributes(cols[8])
            gid = extract_gene_id(attrs)
            symbol = extract_symbol(attrs)
            locus = extract_locus_tag(attrs)

            # Deduplication key
            dedup_key = (seqid, gid if gid else (symbol, start, end))
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            genes[seqid].append({
                "seqid": seqid,
                "start": start,
                "end": end,
                "strand": strand,
                "gene_id": gid or ".",
                "symbol": symbol,
                "locus_tag": locus,
                "biotype": extract_biotype(attrs, feature),
                "description": extract_description(attrs),
                "dbxref": attrs.get("Dbxref") or attrs.get("db_xref") or ".",
                "feature_type": feature,
            })

    # Pass 2: Fallback only if no explicit 'gene' or 'pseudogene' lines exist
    if not found_primary_genes:
        with open_text(gff_path) as handle:
            for line in handle:
                if not line or line.startswith("#"):
                    continue
                cols = line.rstrip("\n").split("\t")
                if len(cols) != 9:
                    continue
                feature = cols[2].casefold()
                if feature not in {"transcript", "mrna", "rna"}:
                    continue
                seqid = cols[0]
                try:
                    start = int(cols[3]) - 1
                    end = int(cols[4])
                except ValueError:
                    continue
                if end <= start:
                    continue

                strand = cols[6]
                attrs = parse_attributes(cols[8])
                gid = extract_gene_id(attrs)
                symbol = extract_symbol(attrs)
                locus = extract_locus_tag(attrs)

                dedup_key = (seqid, gid if gid else (symbol, start, end))
                if dedup_key in seen_keys:
                    continue
                seen_keys.add(dedup_key)

                genes[seqid].append({
                    "seqid": seqid,
                    "start": start,
                    "end": end,
                    "strand": strand,
                    "gene_id": gid or ".",
                    "symbol": symbol,
                    "locus_tag": locus,
                    "biotype": extract_biotype(attrs, feature),
                    "description": extract_description(attrs),
                    "dbxref": attrs.get("Dbxref") or attrs.get("db_xref") or ".",
                    "feature_type": feature,
                })

    for seqid in genes:
        genes[seqid].sort(key=lambda g: (g["start"], g["end"]))
    return dict(genes)


def inspect_gff(path: str | Path, expected_accession: str | None = None) -> dict[str, Any]:
    """Validate GFF3 assembly provenance and feature content."""
    genes = 0
    seqids = set()
    features = set()
    header_accessions = set()
    header_lines = []

    try:
        with open_text(path) as handle:
            for line_no, line in enumerate(handle, 1):
                if line.startswith("#"):
                    if line_no <= 200:
                        header_lines.append(line.rstrip())
                        header_accessions.update(ACCESSION_RX.findall(line))
                    continue
                cols = line.rstrip("\n").split("\t")
                if len(cols) != 9:
                    continue
                seqids.add(cols[0])
                feature = cols[2].casefold()
                features.add(feature)
                if feature in {"gene", "pseudogene"}:
                    genes += 1
    except (OSError, UnicodeError, gzip.BadGzipFile) as exc:
        return {
            "valid": False,
            "reason": f"unreadable: {exc}",
            "genes": 0,
            "seqids": set(),
            "header_accessions": set(),
        }

    path_accessions = set(ACCESSION_RX.findall(str(Path(path).resolve())))
    proven_accessions = header_accessions | path_accessions
    generated_track = bool(features) and features.issubset({"biological_region", "inverted_repeat"})
    wrong_assembly = (
        bool(proven_accessions)
        and expected_accession is not None
        and expected_accession not in proven_accessions
    )

    valid = genes > 0 and not generated_track and not wrong_assembly
    reason = "ok" if valid else (
        "no genes found" if genes == 0 else
        "appears to be generated output track" if generated_track else
        f"annotations do not match expected accession {expected_accession}" if wrong_assembly else "invalid"
    )

    return {
        "valid": valid,
        "reason": reason,
        "genes": genes,
        "seqids": seqids,
        "header_accessions": header_accessions,
        "path_accessions": path_accessions,
        "features": features,
    }
