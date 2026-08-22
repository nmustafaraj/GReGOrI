from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from .identity import stable_id
from .validate import validate
from ..engine.thermodynamics import analyze_central_loop


def build(project, records, sequence_map=None, annotation_audit=None):
    assembly = project.get("assembly_accession") or project.get("assembly_key")
    species = project.get("species", "Unknown")
    sequence_map = sequence_map or {}
    seqs = []
    shanes = []

    for record in records:
        acc = record["accession"]
        meta = sequence_map.get(acc, {})
        group = meta.get("chromosome_group") or record.get("chromosome") or "Other"
        display = meta.get("display_name") or record.get("display_name") or acc
        seqs.append({
            "sequence_accession": acc,
            "display_name": display,
            "chromosome_group": group,
            "length_bp": record["length_bp"],
            "sequence_role": meta.get("sequence_role"),
            "hierarchy_source": meta.get("hierarchy_source", "record"),
        })

        for i, s in enumerate(record.get("shanes", []), 1):
            start, end = int(s["start"]), int(s["end"])
            sid = stable_id(assembly, acc, start, end)
            islands = s.get("islands", [])

            # Normalize superimposed genes
            raw_genes = s.get("genes", [])
            normalized_genes = []
            for g in raw_genes:
                gs = int(g.get("genomic_start", g.get("start", start)))
                ge = int(g.get("genomic_end", g.get("end", end)))
                sym = g.get("symbol") or g.get("feature_id") or g.get("gene_id") or "."
                gid = g.get("gene_id", ".")
                url = g.get("ncbi_url") or (f"https://www.ncbi.nlm.nih.gov/gene/{gid}" if gid != "." else f"https://www.ncbi.nlm.nih.gov/gene/?term={quote(sym)}")
                normalized_genes.append({
                    "gene_id": gid,
                    "symbol": sym,
                    "locus_tag": g.get("locus_tag", "."),
                    "feature_id": sym,
                    "biotype": g.get("biotype", "gene"),
                    "strand": g.get("strand", "+"),
                    "start": gs,
                    "end": ge,
                    "genomic_start": gs,
                    "genomic_end": ge,
                    "overlap_bp": int(g.get("overlap_bp", min(end, ge) - max(start, gs))),
                    "relationship": g.get("relationship", "partial_overlap"),
                    "ncbi_url": url,
                })

            details = s.get("details") or {}
            details = {k: details.get(k, "") for k in ("candidate_sequence", "context_sequence", "folded_alignment", "island_alignment")} | {
                k: v for k, v in details.items() if k not in {"candidate_sequence", "context_sequence", "folded_alignment", "island_alignment"}
            }
            systematic = s.get("systematic_name") or s.get("name") or f"{species}_{display}_SHaNE_{i}"

            pad = max(1000, round((end - start) * 0.10))
            lo = max(1, start + 1 - pad)
            hi = end + pad
            marks = [f"{start + 1}:{end}|{systematic}|8592A8"]
            for idx_isl, a in enumerate(islands, 1):
                marks.append(f"{int(a.get('s_start', start)) + 1}:{int(a.get('s_end', end))}|I{idx_isl}_5p|EE3EDC")
                marks.append(f"{int(a.get('h_start', start)) + 1}:{int(a.get('h_end', end))}|I{idx_isl}_3p|28D4ED")
            ncbi_q = quote(acc)
            marks_str = quote(",".join(marks), safe=":,|")
            region_url = f"https://www.ncbi.nlm.nih.gov/nuccore/{ncbi_q}?report=graph&v={lo}:{hi}&mk={marks_str}&content=4"

            candidate_seq = details.get("candidate_sequence") or s.get("candidate_sequence") or ""
            if islands and candidate_seq:
                i5 = max(isl["s_end"] for isl in islands) - start
                i3 = min(isl["h_start"] for isl in islands) - start
                central_loop_seq = candidate_seq[i5:i3] if (i3 > i5 and i5 >= 0 and i3 <= len(candidate_seq)) else ""
            else:
                central_loop_seq = candidate_seq

            if central_loop_seq:
                central_loop_data = analyze_central_loop(central_loop_seq)
            else:
                cl_existing = s.get("central_loop_analysis") or details.get("central_loop_analysis") or {}
                if cl_existing.get("loop_seq"):
                    central_loop_data = analyze_central_loop(cl_existing["loop_seq"])
                else:
                    central_loop_data = cl_existing

            details["central_loop_analysis"] = central_loop_data

            shanes.append({
                "systematic_name": systematic,
                "stable_id": sid,
                "short_id": s.get("barcode_id") or f"SHaNE_{i}",
                "assembly_accession": assembly,
                "species": species,
                "chromosome_group": group,
                "sequence_display_name": display,
                "sequence_accession": acc,
                "coordinates": {"start": start, "end": end},
                "length_bp": end - start,
                "genomic_length_bp": s.get("genomic_length_bp", end - start),
                "length_with_voids_bp": s.get("length_with_voids_bp", end - start),
                "voids_count": s.get("voids_count", 0),
                "score": s.get("score", 0),
                "gc_content_percent": s.get("gc_content_percent", 0),
                "island_count": len(islands),
                "total_island_length_bp": sum(max(0, x["s_end"] - x["s_start"]) for x in islands),
                "islands": islands,
                "branching_topology": s.get("branching_topology") or details.get("branching_topology", "unbranched"),
                "branch_count": s.get("branch_count", len(s.get("branches", []))),
                "branches": s.get("branches", details.get("branches", [])),
                "central_loop_analysis": central_loop_data,
                "genes": normalized_genes,
                "annotation_status": s.get("annotation_status", "annotated" if normalized_genes else "no_gene_overlap"),
                "ncbi_region_url": region_url,
                "details": details,
                "availability": {k: bool(v) for k, v in details.items()},
                "provenance": s.get("provenance", {}),
            })

    lib = {
        "library_format": "GReGOrI-SHaNE-Library",
        "library_version": "5.0-palaces",
        "coordinate_system": "0-based,end-exclusive",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "assemblies": [{
            "species": species,
            "name": project.get("metadata", {}).get("assembly_name") or assembly,
            "source": project.get("source"),
            "accession": assembly,
        }],
        "sequence_records": seqs,
        "shanes": shanes,
        "annotation_audit": annotation_audit or {},
    }

    report = validate(lib)
    lib["validation"] = report
    if not report["ok"]:
        raise ValueError("Palaces publication gate failed: " + "; ".join(report["errors"][:10]))

    out = Path(project["project_path"]) / "central_library"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "GReGOrI_SHaNE_library.json"
    path.write_text(json.dumps(lib, indent=2), encoding="utf-8")
    (out / "validation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path
