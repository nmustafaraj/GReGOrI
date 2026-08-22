import csv
import gzip
import re
from pathlib import Path
from typing import Any, Iterator

from .alignment import (
    align_islands_wc,
    align_loops_wc,
    calculate_score,
    center_pad,
    get_reverse_complement,
    is_wc_pair,
    pairline,
    rc,
    similarity,
)
from .plotting import is_plotting_available, save_visualizations

FASTA_EXTENSIONS = {".fa", ".fasta", ".fna", ".fas", ".fsa", ".seq", ".txt", ".fa.gz", ".fasta.gz", ".fna.gz", ".fas.gz"}


def expand_paths(inputs: list[str | Path]) -> list[Path]:
    """Expand list of file and directory paths to individual FASTA paths."""
    resolved: list[Path] = []
    for item in inputs:
        s = str(item).strip().strip('"').strip("'")
        if not s:
            continue
        try:
            p = Path(s).expanduser().resolve()
            if p.is_file():
                resolved.append(p)
            elif p.is_dir():
                for f in p.rglob("*"):
                    if f.is_file() and any(f.name.lower().endswith(ext) for ext in FASTA_EXTENSIONS):
                        resolved.append(f)
        except Exception:
            pass
    return sorted(set(resolved))


def inspect_sequences(paths: list[str | Path], limits: dict[str, Any] | None = None) -> dict[str, Any]:
    """Inspect input FASTA files and return preflight summary."""
    expanded = expand_paths(paths)
    file_count = len(expanded)
    seq_count = 0
    total_bases = 0
    species_set = set()
    violations: list[str] = []

    for p in expanded:
        try:
            for header, seq in records(p):
                seq_count += 1
                total_bases += len(seq)
                spec = species_from_header(header)
                if spec != "Unknown":
                    species_set.add(spec)
        except Exception as exc:
            violations.append(f"Error reading {p.name}: {exc}")

    is_valid = file_count > 0 and seq_count > 0
    if not is_valid and not violations:
        violations.append("No valid FASTA sequence records found in specified paths.")

    return {
        "valid": is_valid,
        "files": [str(p) for p in expanded],
        "file_count": file_count,
        "sequence_count": seq_count,
        "total_bases": total_bases,
        "total_mb": total_bases / 1e6,
        "species": sorted(species_set) if species_set else ["Unknown"],
        "violations": violations,
    }


def open_fasta(filepath: str | Path):
    """Open plain text or gzip-compressed FASTA file."""
    path = Path(filepath)
    if path.name.lower().endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return path.open("r", encoding="utf-8")


def sanitize_sequence(raw: str) -> str:
    """Uppercase and clean nucleotide sequence."""
    return re.sub(r"[^ACGTNacgtn]", "", raw).upper()


def accession_from_header(header: str) -> str:
    """Extract clean, cross-platform filesystem-safe accession token from FASTA header line."""
    first = header.split()[0].lstrip(">")
    if "|" in first:
        for p in first.split("|"):
            clean = p.split(":")[0]
            if len(clean) >= 3 and clean.lower() not in ("ref", "gi", "gb", "emb", "dbj"):
                return clean
    return re.sub(r"[^A-Za-z0-9_.-]", "_", first).strip("._") or "sequence"


def species_from_header(header: str) -> str:
    """Extract species or organism from FASTA header."""
    m = re.search(r"\[organism=([^\]]+)\]", header, re.I)
    if m:
        return m.group(1)
    parts = header.lstrip(">").split()
    if len(parts) > 2:
        cand = re.sub(r"[^A-Za-z0-9_ -]", "", " ".join(parts[1:3])).strip()
        if len(cand) > 3 and not any(k in cand.lower() for k in ("chromosome", "scaffold", "contig", "complete", "genome")):
            return cand
    return "Unknown"


def records(filepath: str | Path) -> Iterator[tuple[str, str]]:
    """Yield (header, sequence) records from a FASTA file."""
    header = None
    seq_chunks: list[str] = []
    with open_fasta(filepath) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    yield header, "".join(seq_chunks).upper()
                header = line[1:].strip()
                seq_chunks = []
            else:
                seq_chunks.append(line)
    if header is not None:
        yield header, "".join(seq_chunks).upper()


def phase_1_scan(
    sequence: str,
    window_size: int = 20,
    step: int = 1000,
    max_lookahead: int = 20000,
    overlapping: bool = False,
    lookahead: int | None = None,
    control: Any = None,
    emit: Any = None,
    base_done: int = 0,
    total_bases: int = 0,
    seq_index: int = 1,
    seq_total: int = 1,
    **kwargs: Any,
) -> list[dict[str, int]]:
    """Scan sequence for exact reverse-complement seed pairs with live progress reporting."""
    actual_lookahead = lookahead if (lookahead is not None and not isinstance(lookahead, bool)) else max_lookahead
    hits = []
    seq_len = len(sequence)
    last_emit_pos = 0

    for i in range(0, seq_len - window_size, step):
        if control and i % (step * 10) == 0:
            control.safe_point({"phase": "scanning", "position": i, "sequence_index": seq_index})

        if emit and (i - last_emit_pos >= max(50000, step * 20) or i + step >= seq_len - window_size):
            last_emit_pos = i
            completed = base_done + i
            pct = (completed / total_bases * 100) if total_bases else 0
            emit(
                "scan_progress",
                sequence_index=seq_index,
                sequence_count=seq_total,
                completed_bases=completed,
                total_bases=total_bases,
                percent=pct,
                hits_found=len(hits),
            )

        sample = sequence[i : i + window_size]
        if "N" in sample:
            continue
        rc_sample = get_reverse_complement(sample)
        search_start = i + window_size
        search_end = min(i + actual_lookahead, seq_len)
        window = sequence[search_start:search_end]
        pattern = f"(?={re.escape(rc_sample)})" if overlapping else re.escape(rc_sample)
        for match in re.finditer(pattern, window):
            hit_pos = search_start + match.start()
            hits.append({"sample_pos": i, "hit_pos": hit_pos, "distance": hit_pos - i})

    return hits


def enforce_strict_nesting(group: list[dict[str, int]], ratio_tolerance: int = 50) -> list[dict[str, int]]:
    """Filter candidate group for strictly collinear anti-parallel contraction."""
    group = sorted(group, key=lambda x: x["sample_pos"])
    valid_subsequences = []
    for i in range(len(group)):
        current_path = [group[i]]
        for j in range(i + 1, len(group)):
            prev = current_path[-1]
            curr = group[j]
            d_samp = curr["sample_pos"] - prev["sample_pos"]
            d_hit = curr["hit_pos"] - prev["hit_pos"]
            if d_samp > 0 and d_hit < 0 and curr["sample_pos"] < curr["hit_pos"]:
                exp_dist = prev["distance"] - 2 * d_samp
                if abs(curr["distance"] - exp_dist) <= ratio_tolerance:
                    current_path.append(curr)
        valid_subsequences.append(current_path)
    return max(valid_subsequences, key=len) if valid_subsequences else []


def expand_islands(
    chromosome: str,
    nested_seeds: list[dict[str, int]],
    threshold: float = 0.99,
) -> list[dict[str, int]]:
    """Trusted legacy expansion: fixed 20-bp seed window."""
    islands = []
    for seed in nested_seeds:
        s_start, s_end = seed["sample_pos"], seed["sample_pos"] + 20
        h_start, h_end = seed["hit_pos"], seed["hit_pos"] + 20
        while s_start > 0 and h_end < len(chromosome):
            test_s = chromosome[s_start - 1 : s_start + 19]
            test_h = chromosome[h_end - 19 : h_end + 1]
            if calculate_score(test_s, get_reverse_complement(test_h)) >= threshold:
                s_start -= 1
                h_end += 1
            else:
                break
        while s_end < len(chromosome) and h_start > 0:
            test_s = chromosome[s_end - 19 : s_end + 1]
            test_h = chromosome[h_start - 1 : h_start + 19]
            if calculate_score(test_s, get_reverse_complement(test_h)) >= threshold:
                s_end += 1
                h_start -= 1
            else:
                break
        islands.append({"s_start": s_start, "s_end": s_end, "h_start": h_start, "h_end": h_end})
    islands.sort(key=lambda x: x["s_start"])
    merged = []
    for island in islands:
        if not merged:
            merged.append(island)
        else:
            last = merged[-1]
            if island["s_start"] <= last["s_end"]:
                last["s_end"] = max(last["s_end"], island["s_end"])
                last["h_start"] = min(last["h_start"], island["h_start"])
                last["h_end"] = max(last["h_end"], island["h_end"])
            else:
                merged.append(island)
    return merged


def group_hits(hits: list[dict[str, int]], grouping_distance: int = 10000) -> list[list[dict[str, int]]]:
    """Group nearby seed hits into candidate arrays."""
    if not hits:
        return []
    raw_groups, current_group = [], [hits[0]]
    for hit in hits[1:]:
        if hit["sample_pos"] - current_group[-1]["sample_pos"] <= grouping_distance:
            current_group.append(hit)
        else:
            if len(current_group) >= 2:
                raw_groups.append(current_group)
            current_group = [hit]
    if len(current_group) >= 2:
        raw_groups.append(current_group)
    return raw_groups


def phase_3_island_mapping(
    chromosome: str,
    raw_groups: list[list[dict[str, int]]],
    threshold: float = 0.99,
    min_hits: int = 2,
) -> list[dict[str, Any]]:
    """Map and expand islands for each verified nested candidate group."""
    verified_shanes = []
    for group in raw_groups:
        nested_group = enforce_strict_nesting(group)
        if len(nested_group) >= min_hits:
            islands = expand_islands(chromosome, nested_group, threshold)
            if islands:
                start = islands[0]["s_start"]
                end = islands[0]["h_end"]
                body = chromosome[start:end]
                verified_shanes.append({
                    "start": start,
                    "end": end,
                    "length_bp": end - start,
                    "islands": islands,
                    "score": similarity(body, rc(body)),
                    "genes": [],
                })
    return verified_shanes


def run_legacy(
    sequence: str,
    window_size: int = 20,
    step: int = 1000,
    max_lookahead: int = 20000,
    threshold: float = 0.99,
    min_hits: int = 2,
    overlapping: bool = False,
    control: Any = None,
    emit: Any = None,
    base_done: int = 0,
    total_bases: int = 0,
    seq_index: int = 1,
    seq_total: int = 1,
    **kwargs: Any,
) -> tuple[list[dict[str, int]], list[dict[str, Any]]]:
    """Execute complete 3-phase SHaNE discovery pipeline with live event emission."""
    hits = phase_1_scan(
        sequence=sequence,
        window_size=window_size,
        step=step,
        max_lookahead=max_lookahead,
        overlapping=overlapping,
        control=control,
        emit=emit,
        base_done=base_done,
        total_bases=total_bases,
        seq_index=seq_index,
        seq_total=seq_total,
    )
    if control:
        control.safe_point({"phase": "grouping_hits", "sequence_index": seq_index})
    groups = group_hits(hits)
    if control:
        control.safe_point({"phase": "expanding_islands", "sequence_index": seq_index})
    shanes = phase_3_island_mapping(sequence, groups, threshold, min_hits)
    return hits, shanes


def analyse_sequence(
    sequence: str,
    window_size: int = 20,
    step: int = 1000,
    lookahead: int = 20000,
    threshold: float = 0.99,
    min_hits: int = 2,
    overlapping: bool = False,
    control: Any = None,
    emit: Any = None,
    base_done: int = 0,
    total_bases: int = 0,
    seq_index: int = 1,
    seq_total: int = 1,
    **kwargs: Any,
) -> tuple[list[dict[str, int]], list[dict[str, Any]]]:
    """Alias for run_legacy."""
    return run_legacy(
        sequence=sequence,
        window_size=window_size,
        step=step,
        max_lookahead=lookahead,
        threshold=threshold,
        min_hits=min_hits,
        overlapping=overlapping,
        control=control,
        emit=emit,
        base_done=base_done,
        total_bases=total_bases,
        seq_index=seq_index,
        seq_total=seq_total,
        **kwargs,
    )


scan_seeds = phase_1_scan
filter_strict_nesting = enforce_strict_nesting


def generate_continuous_alignment(
    chromosome: str,
    islands: list[dict[str, int]],
    buffer_len: int = 0,
) -> tuple[str, str, str, int, int]:
    """Produce 5' and 3' folded alignment strings with reverse-oriented 3' arm."""
    top_seq, bot_seq, match_seq = "", "", ""
    s_start, h_end = islands[0]["s_start"], islands[0]["h_end"]
    actual_up5 = chromosome[max(0, s_start - buffer_len) : s_start].lower()
    actual_up3 = chromosome[h_end : min(len(chromosome), h_end + buffer_len)].lower()
    actual_up3_rev = actual_up3[::-1]
    if actual_up5 or actual_up3_rev:
        up5_pad, up3_pad = align_loops_wc(actual_up5, actual_up3_rev)
        top_seq += up5_pad
        bot_seq += up3_pad
        match_seq += "".join("|" if is_wc_pair(a, b) else " " for a, b in zip(up5_pad, up3_pad))
    start_top = s_start - len(actual_up5)
    start_bot = h_end + len(actual_up3)

    for i, island in enumerate(islands):
        sq5 = chromosome[island["s_start"] : island["s_end"]].upper()
        sq3_rev = chromosome[island["h_start"] : island["h_end"]][::-1].upper()
        sq5_aln, sq3_aln = align_islands_wc(sq5, sq3_rev)
        top_seq += sq5_aln
        bot_seq += sq3_aln
        match_seq += "".join("|" if is_wc_pair(a, b) else " " for a, b in zip(sq5_aln, sq3_aln))

        if i < len(islands) - 1:
            next_island = islands[i + 1]
            loop5 = chromosome[island["s_end"]:next_island["s_start"]].lower()
            loop3_rev = chromosome[next_island["h_end"]:island["h_start"]][::-1].lower()
        else:
            center = chromosome[island["s_end"]:island["h_start"]].lower()
            midpoint = len(center) // 2
            loop5, loop3_rev = center[:midpoint], center[midpoint:][::-1]

        loop5_aln, loop3_aln = align_loops_wc(loop5, loop3_rev)
        top_seq += loop5_aln
        bot_seq += loop3_aln
        match_seq += "".join("|" if is_wc_pair(a, b) else " " for a, b in zip(loop5_aln, loop3_aln))

    return top_seq, match_seq, bot_seq, start_top, start_bot


def format_continuous_alignment(
    top_seq: str,
    match_seq: str,
    bot_seq: str,
    start_top: int,
    start_bot: int,
    line_length: int = 60,
) -> str:
    """Format continuous alignment into 3-line blocks matching the legacy layout."""
    output = []
    current_top, current_bot = start_top, start_bot
    for i in range(0, len(top_seq), line_length):
        chunk_t = top_seq[i : i + line_length]
        chunk_m = match_seq[i : i + line_length]
        chunk_b = bot_seq[i : i + line_length]
        end_top = current_top + len(chunk_t.replace(".", ""))
        end_bot = current_bot - len(chunk_b.replace(".", ""))
        output.append(f"5'-3'  {chunk_t}  {end_top:07d}\n       {chunk_m}\n3'-5'  {chunk_b}  {end_bot:07d}\n")
        current_top, current_bot = end_top, end_bot
    return "\n".join(output).rstrip()


def generate_island_alignments(chromosome: str, shane_name: str, islands: list[dict[str, int]]) -> str:
    """Generate per-island Watson-Crick alignments with reverse-oriented 3' arms."""
    lines = [f"--- {shane_name} ---"]
    for idx, island in enumerate(islands, 1):
        arm5 = chromosome[island["s_start"] : island["s_end"]]
        arm3 = chromosome[island["h_start"] : island["h_end"]][::-1]
        aligned5, aligned3 = align_islands_wc(arm5, arm3)
        matchline = "".join("|" if is_wc_pair(a, b) else " " for a, b in zip(aligned5, aligned3))
        lines.append(f"Island {idx}: {island['s_start']}:{island['s_end']} vs {island['h_start']}:{island['h_end']}")
        lines.append(f"5' {aligned5}\n   {matchline}\n3' {aligned3}\n")
    return "\n".join(lines).rstrip()


def enrich_shane_details(seq: str, shane: dict[str, Any], context_flank: int = 500, shane_name: str = "") -> dict[str, Any]:
    """Enrich a SHaNE with flanking context sequences, folded Watson-Crick alignments, and maximized scores."""
    start = shane["start"]
    end = shane["end"]
    genomic_len = end - start
    avail_up = min(start, context_flank)
    avail_down = min(len(seq) - end, context_flank)

    flank_left = seq[start - avail_up : start].lower()
    body = seq[start:end].upper()
    flank_right = seq[end : end + avail_down].lower()
    context_sequence = flank_left + body + flank_right

    islands = shane.get("islands", [])
    if islands:
        top_seq, match_seq, bot_seq, start_top, start_bot = generate_continuous_alignment(seq, islands, avail_up)
        folded = format_continuous_alignment(top_seq, match_seq, bot_seq, start_top, start_bot)
        island_alns = generate_island_alignments(seq, shane_name or "SHaNE", islands)

        # Candidate fold without flank buffer to compute maximized score & length with voids
        c_top, c_match, c_bot, _, _ = generate_continuous_alignment(seq, islands, buffer_len=0)
        voids_count = c_top.count(".") + c_bot.count(".")
        length_with_voids = genomic_len + voids_count
        wc_matches = sum(1 for a, b in zip(c_top, c_bot) if is_wc_pair(a, b))
        aligned_len = len(c_top)
        maximized_score = round(wc_matches / aligned_len, 4) if aligned_len else 0.0
    else:
        folded = ""
        island_alns = ""
        voids_count = 0
        length_with_voids = genomic_len
        maximized_score = round(calculate_score(body, rc(body)), 4)

    # Comprehensive interisland and whole-SHaNE branching structure analysis
    from .interisland import analyze_shane_branching
    from .thermodynamics import calculate_island_thermodynamics, analyze_central_loop

    for isl in islands:
        arm5 = seq[isl["s_start"] : isl["s_end"]]
        arm3 = seq[isl["h_start"] : isl["h_end"]]
        isl["thermodynamics"] = calculate_island_thermodynamics(arm5, arm3)

    if islands:
        inner_5p = max(isl["s_end"] for isl in islands)
        inner_3p = min(isl["h_start"] for isl in islands)
        central_loop_seq = seq[inner_5p:inner_3p] if inner_3p > inner_5p else ""
    else:
        central_loop_seq = body

    central_loop_data = analyze_central_loop(central_loop_seq)

    branch_analysis = analyze_shane_branching(seq, islands, shane_start=start, min_stem=5)
    overall_branching = branch_analysis["topology"]
    branch_count = branch_analysis["branch_count"]
    branches = branch_analysis["branches"]
    branching_aln = branch_analysis["branching_alignment"]

    shane["score"] = maximized_score
    shane["genomic_length_bp"] = genomic_len
    shane["length_with_voids_bp"] = length_with_voids
    shane["voids_count"] = voids_count
    shane["branching_topology"] = overall_branching
    shane["branch_count"] = branch_count
    shane["branches"] = branches
    shane["central_loop_analysis"] = central_loop_data

    details = {
        "candidate_sequence": body,
        "context_sequence": context_sequence,
        "available_upstream_bp": avail_up,
        "available_downstream_bp": avail_down,
        "folded_alignment": folded,
        "island_alignment": island_alns,
        "branching_alignment": branching_aln,
        "genomic_length_bp": genomic_len,
        "length_with_voids_bp": length_with_voids,
        "voids_count": voids_count,
        "maximized_score": maximized_score,
        "branching_topology": overall_branching,
        "branch_count": branch_count,
        "branches": branches,
        "central_loop_analysis": central_loop_data,
    }
    shane["details"] = details
    return details


def write_fasta(handle, header: str, sequence: str, width: int = 80) -> None:
    handle.write(f">{header}\n")
    for i in range(0, len(sequence), width):
        handle.write(sequence[i : i + width] + "\n")


def write_outputs(
    output_dir: str | Path,
    chrom: str,
    seq: str,
    shanes: list[dict[str, Any]],
    context_flank: int = 500,
) -> Path:
    """Generate candidates.tsv, candidates.bed, FASTA files, and alignment files."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    tsv_file = out_path / "candidates.tsv"
    bed_file = out_path / "candidates.bed"
    seq_file = out_path / "candidate_sequences.fasta"
    ctx_file = out_path / "candidate_contexts.fasta"
    aln_file = out_path / "continuous_alignments.txt"
    isl_file = out_path / "island_alignments.txt"

    fields = [
        "id",
        "name",
        "chromosome",
        "start",
        "end",
        "length",
        "length_with_voids",
        "voids_count",
        "island_count",
        "combined_island_length",
        "global_score",
    ]

    with tsv_file.open("w", encoding="utf-8", newline="") as tf, \
         bed_file.open("w", encoding="utf-8", newline="\n") as bf, \
         seq_file.open("w", encoding="utf-8", newline="\n") as sf, \
         ctx_file.open("w", encoding="utf-8", newline="\n") as cf, \
         aln_file.open("w", encoding="utf-8", newline="\n") as af, \
         isl_file.open("w", encoding="utf-8", newline="\n") as ifile:

        writer = csv.DictWriter(tf, fieldnames=fields, delimiter="\t")
        writer.writeheader()

        for idx, shane in enumerate(shanes, 1):
            start = shane["start"]
            end = shane["end"]
            name = shane.get("systematic_name") or f"SHaNE_{chrom}_{idx}"
            body = seq[start:end]
            islands = shane.get("islands", [])
            combined_len = sum(max(0, x["s_end"] - x["s_start"]) for x in islands)

            enrich_shane_details(seq, shane, context_flank, name)

            writer.writerow({
                "id": f"SHaNE_{idx}",
                "name": name,
                "chromosome": chrom,
                "start": start,
                "end": end,
                "length": len(body),
                "length_with_voids": shane.get("length_with_voids_bp", len(body)),
                "voids_count": shane.get("voids_count", 0),
                "island_count": len(islands),
                "combined_island_length": combined_len,
                "global_score": f"{shane.get('score', 0.0):.4f}",
            })

            bf.write(f"{chrom}\t{start}\t{end}\t{name}\t0\t.\n")
            write_fasta(sf, name, body.upper())

            ctx_start = max(0, start - context_flank)
            ctx_end = min(len(seq), end + context_flank)
            ctx = seq[ctx_start:start].lower() + body.upper() + seq[end:ctx_end].lower()
            write_fasta(cf, f"{name}|{ctx_start}:{ctx_end}", ctx)

            if shane.get("details", {}).get("folded_alignment"):
                af.write(f"--- {name} Continuous Alignment ---\n")
                af.write(shane["details"]["folded_alignment"] + "\n\n")
            if shane.get("details", {}).get("island_alignment"):
                ifile.write(shane["details"]["island_alignment"] + "\n\n")

    return out_path

