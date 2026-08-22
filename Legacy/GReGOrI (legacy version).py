#!/usr/bin/env python3
"""GReGOrI v0.3.5 - legacy-centered whole-genome application.

The trusted legacy scientific functions remain the primary implementation.
This single-file build adds chromosome-wise batch processing, optional
legacy/refined comparison, saved visualizations, progress indication, and the
original interactive colored SHaNE inspection.
"""

import csv
import hashlib
import html
import platform
import shutil
import subprocess
import urllib.parse
import webbrowser
import zipfile
import gzip
import json
import os
import re
import sys
import threading
import time
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _MATPLOTLIB_AVAILABLE = True
except ImportError:
    _MATPLOTLIB_AVAILABLE = False

VERSION = "0.4.2"
FASTA_SUFFIXES = (".fa", ".fasta", ".fna", ".fa.gz", ".fasta.gz", ".fna.gz")

# ---------------------------------------------------------------------------
# Terminal and progress helpers
# ---------------------------------------------------------------------------

def configure_terminal():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


class Spinner:
    def __init__(self, message):
        self.message = message
        self.stop_event = threading.Event()
        self.thread = None

    def __enter__(self):
        if sys.stderr.isatty():
            def animate():
                frames = "|/-\\"
                index = 0
                while not self.stop_event.is_set():
                    sys.stderr.write(f"\r{frames[index % len(frames)]} {self.message}")
                    sys.stderr.flush()
                    index += 1
                    time.sleep(0.1)
            self.thread = threading.Thread(target=animate, daemon=True)
            self.thread.start()
        else:
            print(self.message)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=0.3)
            sys.stderr.write("\r" + " " * (len(self.message) + 4) + "\r")
            sys.stderr.flush()


def progress(current, total, message):
    percent = 100 if total == 0 else int(100 * current / total)
    width = 28
    done = int(width * percent / 100)
    print(f"[{'#' * done}{'-' * (width - done)}] {percent:3d}%  {message}")


# ---------------------------------------------------------------------------
# Trusted legacy utility functions
# ---------------------------------------------------------------------------

def get_reverse_complement(seq):
    complement_map = str.maketrans("ACGTNacgtn", "TGCANtgcan")
    return seq.translate(complement_map)[::-1]


def parse_length(val_str, default_val):
    val_str = val_str.strip().lower()
    if not val_str:
        return default_val
    try:
        if val_str.endswith("kb"):
            return int(float(val_str.replace("kb", "")) * 1000)
        if val_str.endswith("bp"):
            return int(val_str.replace("bp", ""))
        return int(val_str)
    except ValueError:
        return default_val


def open_fasta(filepath):
    path = Path(filepath)
    if path.name.lower().endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return path.open("r", encoding="utf-8")


def read_fasta_records(filepath):
    records = []
    header = None
    sequence = []
    with open_fasta(filepath) as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    records.append((header, "".join(sequence).upper()))
                header = line[1:].strip()
                sequence = []
            else:
                if header is None:
                    raise ValueError(f"Sequence found before FASTA header in {filepath}")
                sequence.append(line)
    if header is not None:
        records.append((header, "".join(sequence).upper()))
    return records


def calculate_score(seq1, seq2_rc):
    if not seq1 or not seq2_rc:
        return 0.0
    matches = sum(1 for a, b in zip(seq1.upper(), seq2_rc.upper()) if a == b)
    return matches / len(seq1)


def is_wc_pair(a, b):
    if a == "." or b == ".":
        return False
    a, b = a.upper(), b.upper()
    return ((a == "A" and b == "T") or (a == "T" and b == "A") or
            (a == "C" and b == "G") or (a == "G" and b == "C"))


def generate_shane_name(species, chrom, start_pos):
    words = species.split()
    initials = words[0][0].upper() + words[1][0].lower() if len(words) > 1 else species[:2].capitalize()
    return f"{initials}_SHaNE_{chrom}.{start_pos // 100000}"


def center_pad(seq, target_len):
    diff = target_len - len(seq)
    if diff <= 0:
        return seq
    left = diff // 2
    return "." * left + seq + "." * (diff - left)


def align_islands_wc(seq1, seq2):
    """Legacy dynamic programming optimized for Watson-Crick pairing."""
    L1, L2 = len(seq1), len(seq2)
    if L1 == L2 and calculate_score(seq1, get_reverse_complement(seq2)) == 1.0:
        return seq1, seq2
    score = [[0] * (L2 + 1) for _ in range(L1 + 1)]
    for i in range(L1 + 1):
        score[i][0] = -2 * i
    for j in range(L2 + 1):
        score[0][j] = -2 * j
    for i in range(1, L1 + 1):
        for j in range(1, L2 + 1):
            match_score = 2 if is_wc_pair(seq1[i - 1], seq2[j - 1]) else -1
            score[i][j] = max(score[i - 1][j - 1] + match_score,
                              score[i - 1][j] - 2,
                              score[i][j - 1] - 2)
    align1, align2 = [], []
    i, j = L1, L2
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            match_score = 2 if is_wc_pair(seq1[i - 1], seq2[j - 1]) else -1
            if score[i][j] == score[i - 1][j - 1] + match_score:
                align1.append(seq1[i - 1]); align2.append(seq2[j - 1]); i -= 1; j -= 1
                continue
        if i > 0 and (j == 0 or score[i][j] == score[i - 1][j] - 2):
            align1.append(seq1[i - 1]); align2.append("."); i -= 1
        else:
            align1.append("."); align2.append(seq2[j - 1]); j -= 1
    return "".join(align1)[::-1], "".join(align2)[::-1]


def align_loops_wc(seq1, seq2):
    """Legacy loop rule: require at least 10 consecutive WC pairs."""
    if not seq1 and not seq2:
        return "", ""
    aln1, aln2 = align_islands_wc(seq1, seq2)
    wc_m = "".join("|" if is_wc_pair(a, b) else " " for a, b in zip(aln1, aln2))
    if "||||||||||" in wc_m:
        return aln1, aln2
    width = max(len(seq1), len(seq2))
    return center_pad(seq1, width), center_pad(seq2, width)


# ---------------------------------------------------------------------------
# Trusted legacy discovery functions
# ---------------------------------------------------------------------------

def phase_1_scan(sequence, window_size, step, max_lookahead, overlapping=False):
    hits = []
    seq_len = len(sequence)
    for i in range(0, seq_len - window_size, step):
        sample = sequence[i:i + window_size]
        if "N" in sample:
            continue
        rc_sample = get_reverse_complement(sample)
        search_start = i + window_size
        search_end = min(i + max_lookahead, seq_len)
        window = sequence[search_start:search_end]
        pattern = f"(?={re.escape(rc_sample)})" if overlapping else re.escape(rc_sample)
        for match in re.finditer(pattern, window):
            hit_pos = search_start + match.start()
            hits.append({"sample_pos": i, "hit_pos": hit_pos, "distance": hit_pos - i})
    return hits


def enforce_strict_nesting(group, ratio_tolerance=50):
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


def expand_islands(chromosome, nested_seeds, threshold):
    """Trusted legacy expansion: fixed 20-bp seed window."""
    islands = []
    for seed in nested_seeds:
        s_start, s_end = seed["sample_pos"], seed["sample_pos"] + 20
        h_start, h_end = seed["hit_pos"], seed["hit_pos"] + 20
        while s_start > 0 and h_end < len(chromosome):
            test_s = chromosome[s_start - 1:s_start + 19]
            test_h = chromosome[h_end - 19:h_end + 1]
            if calculate_score(test_s, get_reverse_complement(test_h)) >= threshold:
                s_start -= 1; h_end += 1
            else:
                break
        while s_end < len(chromosome) and h_start > 0:
            test_s = chromosome[s_end - 19:s_end + 1]
            test_h = chromosome[h_start - 1:h_start + 19]
            if calculate_score(test_s, get_reverse_complement(test_h)) >= threshold:
                s_end += 1; h_start -= 1
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


def group_hits(hits, grouping_distance=10000):
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


def phase_3_island_mapping(chromosome, raw_groups, threshold, min_hits=2):
    verified_shanes = []
    for group in raw_groups:
        nested_group = enforce_strict_nesting(group)
        if len(nested_group) >= min_hits:
            islands = expand_islands(chromosome, nested_group, threshold)
            if islands:
                verified_shanes.append({"start": islands[0]["s_start"],
                                        "end": islands[0]["h_end"],
                                        "islands": islands})
    return verified_shanes


def run_legacy(sequence, window_size, step, max_lookahead, threshold, min_hits=2, overlapping=False):
    hits = phase_1_scan(sequence, window_size, step, max_lookahead, overlapping)
    groups = group_hits(hits)
    shanes = phase_3_island_mapping(sequence, groups, threshold, min_hits)
    return hits, groups, shanes


# ---------------------------------------------------------------------------
# Trusted legacy alignment and terminal presentation
# ---------------------------------------------------------------------------

def generate_continuous_alignment(chromosome, islands, buffer_len=0):
    top_seq, bot_seq, match_seq = "", "", ""
    s_start, h_end = islands[0]["s_start"], islands[0]["h_end"]
    actual_up5 = chromosome[max(0, s_start - buffer_len):s_start].lower()
    actual_up3 = chromosome[h_end:min(len(chromosome), h_end + buffer_len)].lower()
    actual_up3_rev = actual_up3[::-1]
    width = max(len(actual_up5), len(actual_up3_rev))
    up5_pad, up3_pad = center_pad(actual_up5, width), center_pad(actual_up3_rev, width)
    top_seq += up5_pad; bot_seq += up3_pad
    match_seq += "".join("|" if is_wc_pair(a, b) else " " for a, b in zip(up5_pad, up3_pad))
    start_top = s_start - len(actual_up5)
    start_bot = h_end + len(actual_up3)
    for i, island in enumerate(islands):
        sq5 = chromosome[island["s_start"]:island["s_end"]].upper()
        sq3_rev = chromosome[island["h_start"]:island["h_end"]][::-1].upper()
        sq5_aln, sq3_aln = align_islands_wc(sq5, sq3_rev)
        top_seq += sq5_aln; bot_seq += sq3_aln
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
        top_seq += loop5_aln; bot_seq += loop3_aln
        match_seq += "".join("|" if is_wc_pair(a, b) else " " for a, b in zip(loop5_aln, loop3_aln))
    return top_seq, match_seq, bot_seq, start_top, start_bot


def format_continuous_alignment(top_seq, match_seq, bot_seq, start_top, start_bot, line_length=60, colored=False):
    COLORS = {"A":"\033[96m","T":"\033[96m","C":"\033[95m","G":"\033[95m",
              "a":"\033[96m","t":"\033[96m","c":"\033[95m","g":"\033[95m"}
    RESET = "\033[0m"
    output = []
    current_top, current_bot = start_top, start_bot
    for i in range(0, len(top_seq), line_length):
        chunk_t, chunk_m, chunk_b = top_seq[i:i+line_length], match_seq[i:i+line_length], bot_seq[i:i+line_length]
        end_top = current_top + len(chunk_t.replace(".", ""))
        end_bot = current_bot - len(chunk_b.replace(".", ""))
        if colored:
            colored_top = "".join(f"{COLORS.get(base, '')}{base}{RESET}" if base != "." else "." for base in chunk_t)
            colored_bottom = "".join(f"{COLORS.get(base, '')}{base}{RESET}" if base != "." else "." for base in chunk_b)
            output.append(f"5'-3'  {colored_top}  {end_top:07d}\n       {chunk_m}\n3'-5'  {colored_bottom}  {end_bot:07d}\n")
        else:
            output.append(f"5'-3'  {chunk_t}  {end_top:07d}\n       {chunk_m}\n3'-5'  {chunk_b}  {end_bot:07d}\n")
        current_top, current_bot = end_top, end_bot
    return "\n".join(output)


def terminal_seance(sequence, shanes, species, chrom):
    while True:
        choice = input("\nDo you want to check a specific SHaNE by number? (Enter number, 'list', or 'no'): ").strip().lower()
        if choice in {"no", "quit", "q", "exit"}:
            print("Seance ended. Happy analyzing!")
            break
        if choice == "list":
            for index, shane in enumerate(shanes, 1):
                name = generate_shane_name(species, chrom, shane["start"])
                print(f"{index:3d}  {name}  {shane['start']:,}-{shane['end']:,}  islands={len(shane['islands'])}")
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(shanes):
            shane = shanes[int(choice) - 1]
            buffer_in = input("Enter buffer sequence length [500bp]: ").strip() or "500bp"
            buffer_len = parse_length(buffer_in, 500)
            name = generate_shane_name(species, chrom, shane["start"])
            top, matches, bottom, start_top, start_bot = generate_continuous_alignment(sequence, shane["islands"], buffer_len)
            print(f"\n=== Colored Continuous Alignment for {name} (+{buffer_len}bp flanks) ===")
            print(format_continuous_alignment(top, matches, bottom, start_top, start_bot, colored=True))
        else:
            print(f"Error: choose a SHaNE number between 1 and {len(shanes)}, 'list', or 'no'.")


# ---------------------------------------------------------------------------
# Outputs and visualizations
# ---------------------------------------------------------------------------

def safe_name(value):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_") or "sequence"


def write_fasta(handle, header, sequence, width=80):
    handle.write(f">{header}\n")
    for i in range(0, len(sequence), width):
        handle.write(sequence[i:i+width] + "\n")


def save_visualizations(sequence, shanes, output_dir, chrom):
    if not _MATPLOTLIB_AVAILABLE:
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(16, 2.4))
    ax.hlines(0, 0, len(sequence), color="black", linewidth=1.5)
    if shanes:
        ax.vlines([s["start"] for s in shanes], -0.5, 0.5, color="#d946ef", linewidth=2)
    ax.set_title(f"GReGOrI - SHaNE distribution - {chrom}", fontweight="bold")
    ax.set_xlabel("Absolute genomic coordinate (bp; 0-based)")
    ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(output_dir / "chromosome_overview.png", dpi=220)
    fig.savefig(output_dir / "chromosome_overview.svg")
    plt.close(fig)

    loci = output_dir / "loci"
    loci.mkdir(exist_ok=True)
    for index, shane in enumerate(shanes, 1):
        left = max(0, shane["start"] - 2000)
        right = min(len(sequence), shane["end"] + 2000)
        fig, ax = plt.subplots(figsize=(14, 3.2))
        ax.hlines(0, left, right, color="#cbd5e1", linewidth=7)
        ax.broken_barh([(shane["start"], shane["end"] - shane["start"])], (-0.15, 0.3), facecolors="#22d3ee")
        for island in shane["islands"]:
            ax.broken_barh([(island["s_start"], island["s_end"] - island["s_start"])], (0.15, 0.25), facecolors="#d946ef")
            ax.broken_barh([(island["h_start"], island["h_end"] - island["h_start"])], (-0.4, 0.25), facecolors="#8b5cf6")
        ax.set_xlim(left, right)
        ax.set_ylim(-0.65, 0.65)
        ax.set_yticks([0.27, 0, -0.27])
        ax.set_yticklabels(["5' islands", "SHaNE", "3' islands"])
        ax.set_xlabel("Genomic coordinate (bp; 0-based)")
        ax.set_title(f"SHaNE {index}: {shane['start']:,}-{shane['end']:,} | {len(shane['islands'])} island(s)", fontweight="bold")
        fig.tight_layout()
        fig.savefig(loci / f"SHaNE_{index}_locus.png", dpi=220)
        fig.savefig(loci / f"SHaNE_{index}_locus.svg")
        plt.close(fig)


def generate_outputs(sequence, shanes, species, chrom, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    fields = ["id", "name", "chromosome", "start", "end", "length", "island_count", "combined_island_length", "global_score"]
    with (output_dir / "candidates.tsv").open("w", encoding="utf-8", newline="") as data, \
         (output_dir / "candidates.bed").open("w", encoding="utf-8", newline="\n") as bed, \
         (output_dir / "candidate_sequences.fasta").open("w", encoding="utf-8", newline="\n") as fasta, \
         (output_dir / "candidate_contexts.fasta").open("w", encoding="utf-8", newline="\n") as context, \
         (output_dir / "continuous_alignments.txt").open("w", encoding="utf-8", newline="\n") as alignments, \
         (output_dir / "island_alignments.txt").open("w", encoding="utf-8", newline="\n") as islands_out:
        writer = csv.DictWriter(data, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for index, shane in enumerate(shanes, 1):
            start, end = shane["start"], shane["end"]
            name = generate_shane_name(species, chrom, start)
            body = sequence[start:end]
            combined = sum(i["s_end"] - i["s_start"] for i in shane["islands"])
            global_score = calculate_score(body, get_reverse_complement(body))
            writer.writerow({"id":f"SHaNE_{index}","name":name,"chromosome":chrom,"start":start,"end":end,
                             "length":len(body),"island_count":len(shane["islands"]),
                             "combined_island_length":combined,"global_score":f"{global_score:.4f}"})
            bed.write(f"{chrom}\t{start}\t{end}\t{name}\t0\t.\n")
            write_fasta(fasta, name, body)
            ctx_start, ctx_end = max(0, start - 500), min(len(sequence), end + 500)
            ctx = sequence[ctx_start:start].lower() + body.upper() + sequence[end:ctx_end].lower()
            write_fasta(context, f"{name}|{ctx_start}:{ctx_end}", ctx)
            top, matches, bottom, top_start, bottom_start = generate_continuous_alignment(sequence, shane["islands"])
            alignments.write(f"--- {name} Continuous Alignment ---\n")
            alignments.write(format_continuous_alignment(top, matches, bottom, top_start, bottom_start) + "\n\n")
            islands_out.write(f"--- {name} ---\n")
            for island_index, island in enumerate(shane["islands"], 1):
                arm5 = sequence[island["s_start"]:island["s_end"]]
                arm3 = sequence[island["h_start"]:island["h_end"]][::-1]
                aligned5, aligned3 = align_islands_wc(arm5, arm3)
                matchline = "".join("|" if is_wc_pair(a, b) else " " for a, b in zip(aligned5, aligned3))
                islands_out.write(f"Island {island_index}: {island['s_start']}:{island['s_end']} vs {island['h_start']}:{island['h_end']}\n")
                islands_out.write(f"5' {aligned5}\n   {matchline}\n3' {aligned3}\n\n")
    save_visualizations(sequence, shanes, output_dir, chrom)


def analyze_record(sequence, species, chrom, output_dir, window_size, step, lookahead, threshold, overlapping=False):
    with Spinner(f"Scanning {chrom} for exact reverse-complement seeds"):
        hits, groups, shanes = run_legacy(sequence, window_size, step, lookahead, threshold, overlapping=overlapping)
    progress(1, 3, f"{chrom}: {len(hits)} raw hits")
    progress(2, 3, f"{chrom}: {len(groups)} candidate groups")
    with Spinner(f"Writing chromosome-wise outputs for {chrom}"):
        generate_outputs(sequence, shanes, species, chrom, output_dir)
    progress(3, 3, f"{chrom}: {len(shanes)} SHaNEs complete")
    return {"chrom":chrom,"sequence":sequence,"hits":hits,"groups":groups,"shanes":shanes,"output":output_dir}


# ---------------------------------------------------------------------------
# Simple interactive application
# ---------------------------------------------------------------------------

def print_banner():
    """Display the case-sensitive GReGOrI application banner."""

    PINK = "\033[95m"
    SKY_BLUE = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"

    banner = [
        r"     /$$$$$$  /$$$$$$$             /$$$$$$   /$$$$$$          /$$$$$$",
        r"    /$$__  $$| $$__  $$           /$$__  $$ /$$__  $$        |_  $$_/",
        r"   | $$  \__/| $$  \ $$  /$$$$$$ | $$  \__/| $$  \ $$  /$$$$$$ | $$  ",
        r"   | $$ /$$$$| $$$$$$$/ /$$__  $$| $$ /$$$$| $$  | $$ /$$__  $$| $$  ",
        r"   | $$|_  $$| $$__  $$| $$$$$$$$| $$|_  $$| $$  | $$| $$  \__/| $$  ",
        r"   | $$  \ $$| $$  \ $$| $$_____/| $$  \ $$| $$  | $$| $$      | $$  ",
        r"   |  $$$$$$/| $$  | $$|  $$$$$$$|  $$$$$$/|  $$$$$$/| $$     /$$$$$$",
        r"    \______/ |__/  |__/ \_______/ \______/  \______/ |__/    |______/",
    ]

#    banner = [
#        r" ::::::::  :::::::::  :::::::::: ::::::::   ::::::::  :::::::::  ::::::::::: ",
#        r":+:    :+: :+:    :+: :+:       :+:    :+: :+:    :+: :+:    :+:     :+:     ",
#        r"+:+        +:+    +:+ +:+       +:+        +:+    +:+ +:+    +:+     +:+     ",
#        r":#:        +#++:++#:  +#++:++#  :#:        +#+    +:+ +#++:++#:      +#+     ",
#        r"+#+   +#+# +#+    +#+ +#+       +#+   +#+# +#+    +#+ +#+    +#+     +#+     ",
#        r"#+#    #+# #+#    #+# #+#       #+#    #+# #+#    #+# #+#    #+#     #+#    ",
#        r" ########  ###    ### ########## ########   ########  ###    ### ###########",
#    ]

    print()

    for index, line in enumerate(banner):
        colour = PINK if index < 4 else SKY_BLUE
        print(f"{colour}{line}{RESET}")

    print()
    print(
        f"{SKY_BLUE}           Genomic Repeat Grouping & "
        f"{PINK}Orientation Identifier{RESET}"
    )
    print(
        f"{WHITE}"
       # f"            [ REVERSE-COMPLEMENT DISCOVERY SYSTEM ]"
        f"{RESET}"
    )
    print(f"{PINK}{'=' * 72}{RESET}")
    print(
        f"{SKY_BLUE}"
        f"                             Version {VERSION}"
        f"{RESET}"
    )
    print(f"{PINK}{'=' * 72}{RESET}")
    print()


def get_parameters():
    species = input("Enter species name [Apis mellifera]: ").strip() or "Apis mellifera"
    seed = parse_length(input("Enter sample length [20]: ").strip() or "20", 20)
    if seed != 20:
        print("Legacy compatibility: sample length reset to 20 bp.")
        seed = 20
    step = parse_length(input("Enter sampling step size [1kb]: ").strip() or "1kb", 1000)
    lookahead = parse_length(input("Enter distance to look ahead [20kb]: ").strip() or "20kb", 20000)
    try:
        threshold = float((input("Enter island expansion threshold [0.99]: ").strip() or "0.99").replace(",", "."))
    except ValueError:
        threshold = 0.99
    return species, seed, step, lookahead, threshold



# ---------------------------------------------------------------------------
# v0.4.2 fork: retrieval, annotations, persistence, unified visualization
# ---------------------------------------------------------------------------

FASTA_SUFFIXES = (".fa", ".fasta", ".fna", ".fa.gz", ".fasta.gz", ".fna.gz")
CACHE_ROOT = Path(os.environ.get("GREGORI_CACHE", "GReGOrI_cache"))


def platform_tag():
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "windows" and machine in {"amd64", "x86_64"}:
        return "windows-x64"
    if system == "linux" and machine in {"amd64", "x86_64"}:
        return "linux-x64"
    if system == "darwin" and machine in {"arm64", "aarch64"}:
        return "macos-arm64"
    if system == "darwin":
        return "macos-x64"
    return f"{system}-{machine}"


def resolve_ncbi_tool(name):
    """Resolve future platform bundle, adjacent binary, then PATH."""
    suffix = ".exe" if os.name == "nt" else ""
    root = Path(__file__).resolve().parent
    candidates = [root / "bin" / platform_tag() / f"{name}{suffix}",
                  root / "bin" / f"{name}{suffix}", root / f"{name}{suffix}"]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    found = shutil.which(name)
    if found:
        return found
    raise RuntimeError(f"NCBI {name} was not found. Put it in bin/{platform_tag()}/, beside GReGOrI, or on PATH.")


def run_tool(name, args):
    proc = subprocess.run([resolve_ncbi_tool(name), *args], capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"{name} failed")
    return proc.stdout


class TerminalAnimation:
    def __init__(self, message, style="spinner"):
        self.message, self.style = message, style
        self.stop_event = threading.Event()
        self.thread = None

    def __enter__(self):
        if not sys.stdout.isatty():
            print(self.message)
            return self
        def animate():
            frames = ["|", "/", "-", "\\"]
            chromosome = [
                "5' islands   ===\nSHaNE        =====\n3' islands",
                "5' islands   ===  =  =\nSHaNE        =============\n3' islands             ==",
                "5' islands   ===  =  =   ===\nSHaNE        =====================\n3' islands             ==  =  ===",
            ]
            i = 0
            while not self.stop_event.is_set():
                if self.style == "shane":
                    frame = chromosome[i % len(chromosome)]
                    print("\033[3F" if i else "", end="")
                    print(f"{self.message}\n{frame}", end="", flush=True)
                else:
                    print(f"\r{frames[i % len(frames)]} {self.message}", end="", flush=True)
                i += 1; time.sleep(0.16)
        self.thread = threading.Thread(target=animate, daemon=True); self.thread.start()
        return self

    def __exit__(self, *_):
        self.stop_event.set()
        if self.thread: self.thread.join(timeout=1)
        if sys.stdout.isatty(): print("\r" + " " * 100 + "\r", end="")


def choose_fasta_files(path_text):
    p = Path(path_text)
    if p.is_file(): return [p]
    if p.is_dir():
        files = sorted(x for x in p.iterdir() if x.is_file() and x.name.lower().endswith(FASTA_SUFFIXES))
        if not files: raise ValueError(f"No FASTA files in {p}")
        return files
    raise FileNotFoundError(p)


def sequence_id(header):
    return header.split()[0]


def extract_chromosome_name(header):
    low = header.lower()
    if "mitochond" in low: return "mtDNA"
    m = re.search(r"\bchromosome\s+([^,;|\s]+)", header, re.I)
    if m: return m.group(1).rstrip(".:")
    m = re.search(r"\b(linkage\s+group|scaffold|contig|unplaced\s+scaffold)\s*[:=_-]?\s*([^,;|\s]+)", header, re.I)
    if m: return safe_name(f"{m.group(1)}_{m.group(2)}")
    return sequence_id(header)


def search_ncbi_species(species, limit=20):
    with TerminalAnimation("Contacting NCBI"):
        text = run_tool("datasets", ["summary", "genome", "taxon", species, "--as-json-lines"])
    found=[]
    for line in text.splitlines():
        try: obj=json.loads(line)
        except json.JSONDecodeError: continue
        accession=obj.get("accession") or obj.get("current_accession")
        if not accession: continue
        ai=obj.get("assembly_info",{}); org=obj.get("organism",{})
        found.append({"accession":accession,"organism":org.get("organism_name") or species,
                      "assembly_name":ai.get("assembly_name") or "unknown",
                      "level":ai.get("assembly_level") or "unknown",
                      "source":"RefSeq" if accession.startswith("GCF_") else "GenBank"})
        if len(found)>=limit: break
    return found


def find_dataset_file(root, patterns):
    files=[]
    for pattern in patterns: files.extend(Path(root).rglob(pattern))
    return max(files, key=lambda p:p.stat().st_size) if files else None


def export_metadata(cache_dir, archive, fallback):
    metadata=dict(fallback)
    try:
        tsv=run_tool("dataformat", ["tsv","genome","--package",str(archive),"--fields",
            "organism-name,assminfo-name,accession,assminfo-level,assminfo-submitter"])
        (cache_dir/"assembly_metadata.tsv").write_text(tsv,encoding="utf-8")
        lines=[x for x in tsv.splitlines() if x.strip()]
        if len(lines)>=2:
            keys=lines[0].split("\t"); vals=lines[1].split("\t")
            metadata.update(dict(zip(keys,vals)))
    except Exception as exc:
        (cache_dir/"assembly_metadata.tsv").write_text("key\tvalue\n"+"\n".join(f"{k}\t{v}" for k,v in metadata.items()),encoding="utf-8")
        metadata["dataformat_warning"]=str(exc)
    (cache_dir/"assembly_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    return metadata


def download_ncbi_accession(accession, source=None):
    accession=accession.strip().upper()
    if not re.fullmatch(r"GC[AF]_\d+\.\d+",accession): raise ValueError("Invalid GCF_/GCA_ accession")
    source=source or ("RefSeq" if accession.startswith("GCF_") else "GenBank")
    cache=CACHE_ROOT/accession; extracted=cache/"dataset"; cache.mkdir(parents=True,exist_ok=True)
    fasta=find_dataset_file(extracted,["*.fna","*.fna.gz"])
    gff=find_dataset_file(extracted,["*.gff","*.gff3","*.gff.gz","*.gff3.gz"])
    archive=cache/"ncbi_dataset.zip"
    if not fasta or not archive.exists():
        with TerminalAnimation(f"Downloading {source} genome and annotation"):
            run_tool("datasets",["download","genome","accession",accession,"--include","genome,gff3","--filename",str(archive)])
        extracted.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(archive) as zf: zf.extractall(extracted)
        fasta=find_dataset_file(extracted,["*.fna","*.fna.gz"]); gff=find_dataset_file(extracted,["*.gff","*.gff3","*.gff.gz","*.gff3.gz"])
    if not fasta: raise FileNotFoundError("NCBI package has no genomic FASTA")
    metadata=export_metadata(cache,archive,{"accession":accession,"source":source,"annotation_available":bool(gff)})
    metadata.update({"accession":accession,"source":source,"annotation_available":bool(gff),"fasta":str(fasta),"gff3":str(gff) if gff else None})
    (cache/"assembly_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    return fasta,gff,metadata


def parse_gff_attributes(text):
    attrs={}
    for item in text.split(";"):
        if "=" in item:
            k,v=item.split("=",1); attrs[k]=urllib.parse.unquote(v)
    return attrs


def load_gff_genes(path):
    genes={}
    if not path: return genes
    opener=gzip.open if str(path).endswith(".gz") else open
    with opener(path,"rt",encoding="utf-8",errors="replace") as fh:
        for line in fh:
            if not line or line.startswith("#"): continue
            cols=line.rstrip("\n").split("\t")
            if len(cols)!=9 or cols[2] not in {"gene","pseudogene"}: continue
            try: start0=int(cols[3])-1; end0=int(cols[4])
            except ValueError: continue
            a=parse_gff_attributes(cols[8]); strand=cols[6]
            gene={"seqid":cols[0],"start":start0,"end":end0,"strand":strand,
                  "transcription_start":end0-1 if strand=="-" else start0,
                  "transcription_end":start0 if strand=="-" else end0-1,
                  "id":a.get("ID","."),"symbol":a.get("gene") or a.get("Name") or ".",
                  "locus_tag":a.get("locus_tag","."),"biotype":a.get("gene_biotype") or a.get("gene_type") or cols[2]}
            genes.setdefault(cols[0],[]).append(gene)
    for seqid in genes: genes[seqid].sort(key=lambda g:g["start"])
    return genes


def annotate_shanes(shanes, genes, annotation_available):
    for s in shanes:
        overlaps=[]
        for g in genes:
            ov=max(0,min(s["end"],g["end"])-max(s["start"],g["start"]))
            if not ov: continue
            if g["start"]>=s["start"] and g["end"]<=s["end"]: rel="gene_contained_in_SHaNE"
            elif s["start"]>=g["start"] and s["end"]<=g["end"]: rel="SHaNE_contained_in_gene"
            else: rel="partial_overlap"
            x=dict(g); x.update({"overlap_bp":ov,"relationship":rel,
                "contains_transcription_start":s["start"]<=g["transcription_start"]<s["end"]})
            overlaps.append(x)
        s["gene_overlaps"]=overlaps
        s["annotation_status"]=("annotation_unavailable" if not annotation_available else
                                "annotated" if overlaps else "no_gene_overlap")


def assembly_folder(base, metadata, species, path_text):
    organism=(metadata or {}).get("organism") or (metadata or {}).get("Organism Name") or species
    assembly=(metadata or {}).get("assembly_name") or (metadata or {}).get("Assembly Name") or Path(path_text).stem
    source=(metadata or {}).get("source") or "Local"
    accession=(metadata or {}).get("accession")
    parts=[organism,assembly,source]
    if accession: parts.append(accession)
    return Path(base)/safe_name("_".join(map(str,parts)))


def analysis_signature(path_text, parameters, metadata):
    files=choose_fasta_files(path_text)
    payload={"version":VERSION,"parameters":parameters,"accession":(metadata or {}).get("accession"),
             "files":[(str(p.resolve()),p.stat().st_size,p.stat().st_mtime_ns) for p in files]}
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()


def enhanced_write(chrom_dir, chrom, seqid, shanes, annotation_available):
    enhanced=chrom_dir/"enhanced_v0.4.2"; enhanced.mkdir(parents=True,exist_ok=True)
    fields=["ID","Name","Chromosome","Sequence_ID","Start","End","Length","Island_Count","Gene_Count",
            "Gene_Symbols","Gene_IDs","Locus_Tags","Gene_Biotypes","Gene_Strands","Gene_Genomic_Starts",
            "Gene_Genomic_Ends","Gene_Transcription_Starts","Gene_Transcription_Ends","Gene_Overlap_bp",
            "Gene_Relationships","Annotation_Status"]
    with (enhanced/"annotated_SHaNE_Data.tsv").open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=fields,delimiter="\t"); w.writeheader()
        for i,s in enumerate(shanes,1):
            gs=s.get("gene_overlaps",[]); join=lambda k:";".join(str(g[k]) for g in gs) or "."
            w.writerow({"ID":f"SHaNE_{i}","Name":f"SHaNE_{i}","Chromosome":chrom,"Sequence_ID":seqid,
                "Start":s["start"],"End":s["end"],"Length":s["end"]-s["start"],"Island_Count":len(s["islands"]),
                "Gene_Count":len(gs),"Gene_Symbols":join("symbol"),"Gene_IDs":join("id"),"Locus_Tags":join("locus_tag"),
                "Gene_Biotypes":join("biotype"),"Gene_Strands":join("strand"),"Gene_Genomic_Starts":join("start"),
                "Gene_Genomic_Ends":join("end"),"Gene_Transcription_Starts":join("transcription_start"),
                "Gene_Transcription_Ends":join("transcription_end"),"Gene_Overlap_bp":join("overlap_bp"),
                "Gene_Relationships":join("relationship"),"Annotation_Status":s["annotation_status"]})
    payload={"chromosome":chrom,"sequence_id":seqid,"annotation_available":annotation_available,"shanes":shanes}
    (enhanced/"candidates.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")


def chromosome_complete(chrom_dir):
    legacy=chrom_dir/"legacy_v0.4"
    enhanced=chrom_dir/"enhanced_v0.4.2"
    needed=[legacy/"candidates.tsv",legacy/"candidate_sequences.fasta",legacy/"continuous_alignments.txt",
            legacy/"chromosome_overview.png",enhanced/"annotated_SHaNE_Data.tsv",enhanced/"candidates.json",
            chrom_dir/"chromosome_result.json",chrom_dir/"COMPLETE"]
    return all(p.exists() for p in needed)


def save_result_stub(chrom_dir,result,seqid):
    payload={k:result[k] for k in ("chrom","hits","groups","shanes")}
    payload["sequence_id"]=seqid; payload["length_bp"]=len(result["sequence"])
    (chrom_dir/"chromosome_result.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    (chrom_dir/"COMPLETE").write_text("complete\n",encoding="utf-8")


def load_result_stub(chrom_dir):
    return json.loads((chrom_dir/"chromosome_result.json").read_text(encoding="utf-8"))


def write_overlap_table(results, enhanced_root):
    fields=["Chromosome","Sequence_ID","SHaNE_ID","SHaNE_Start","SHaNE_End","Gene_ID","Gene_Symbol","Locus_Tag",
            "Gene_Start","Gene_End","Strand","Transcription_Start","Transcription_End","Biotype","Overlap_bp","Relationship"]
    with (enhanced_root/"SHaNE_gene_overlaps.tsv").open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=fields,delimiter="\t"); w.writeheader()
        for r in results:
            for i,s in enumerate(r["shanes"],1):
                for g in s.get("gene_overlaps",[]):
                    w.writerow({"Chromosome":r["chrom"],"Sequence_ID":r["sequence_id"],"SHaNE_ID":f"SHaNE_{i}",
                        "SHaNE_Start":s["start"],"SHaNE_End":s["end"],"Gene_ID":g["id"],"Gene_Symbol":g["symbol"],
                        "Locus_Tag":g["locus_tag"],"Gene_Start":g["start"],"Gene_End":g["end"],"Strand":g["strand"],
                        "Transcription_Start":g["transcription_start"],"Transcription_End":g["transcription_end"],
                        "Biotype":g["biotype"],"Overlap_bp":g["overlap_bp"],"Relationship":g["relationship"]})


def generate_browser(results, enhanced_root, metadata):
    data=json.dumps({"metadata":metadata or {},"results":results},separators=(",",":"))
    template="""<!doctype html><meta charset="utf-8"><title>GReGOrI SHaNE Browser</title>
<style>body{font:14px Segoe UI;background:#f5f7fb;margin:0;color:#172033}header{background:linear-gradient(100deg,#c332db,#20bad1);color:white;padding:18px}main{display:grid;grid-template-columns:240px 1fr;gap:16px;padding:16px}aside,.card{background:white;border-radius:10px;padding:14px;box-shadow:0 2px 10px #0001}button{display:block;width:100%;padding:7px;border:0;background:white;text-align:left}button:hover{background:#e9f8fb}svg{width:100%;height:190px}.pink{fill:#d23ce6}.cyan{fill:#27c7dc}.violet{fill:#8054ed}.gene{fill:#20735a}.axis{stroke:#9aa8bb}</style>
<header><h2>GReGOrI SHaNE Browser</h2><div id="meta"></div></header><main><aside><b>Chromosomes</b><div id="nav"></div></aside><section><div class="card"><h3 id="title"></h3><svg id="overview" viewBox="0 0 1000 190"></svg></div><div class="card"><h3 id="detailtitle">Select a SHaNE</h3><svg id="detail" viewBox="0 0 1000 230"></svg><div id="genes"></div></div></section></main>
<script>const D=__DATA__,N='http://www.w3.org/2000/svg';const E=(n,a={})=>{let e=document.createElementNS(N,n);for(let k in a)e.setAttribute(k,a[k]);return e};let R=null;
meta.textContent=[D.metadata.organism,D.metadata.assembly_name,D.metadata.source,D.metadata.accession].filter(Boolean).join(' | ');D.results.forEach((r,i)=>{let b=document.createElement('button');b.textContent=`${r.chrom}: ${r.shanes.length} SHaNEs`;b.onclick=()=>showChr(i);nav.appendChild(b)});
function showChr(i){R=D.results[i];title.textContent=`Chromosome ${R.chrom} — ${R.length_bp.toLocaleString()} bp`;overview.innerHTML='';overview.append(E('line',{x1:50,y1:90,x2:950,y2:90,class:'axis','stroke-width':8}));R.shanes.forEach((s,j)=>{let x=50+s.start/R.length_bp*900,w=Math.max(3,(s.end-s.start)/R.length_bp*900),q=E('rect',{x,y:55,width:w,height:70,class:'pink'});q.onclick=()=>detail(j);overview.append(q)})}
function detail(j){let s=R.shanes[j],lo=s.start,hi=s.end,dx=p=>70+(p-lo)/(hi-lo)*860;detailtitle.textContent=`SHaNE ${j+1}: ${lo.toLocaleString()}–${hi.toLocaleString()}`;detail.innerHTML='';detail.append(E('rect',{x:70,y:85,width:860,height:50,class:'cyan'}));s.islands.forEach(a=>{detail.append(E('rect',{x:dx(a.s_start),y:45,width:Math.max(2,dx(a.s_end)-dx(a.s_start)),height:40,class:'pink'}));detail.append(E('rect',{x:dx(a.h_start),y:135,width:Math.max(2,dx(a.h_end)-dx(a.h_start)),height:40,class:'violet'}))});genes.innerHTML=s.gene_overlaps.length?s.gene_overlaps.map(g=>`<p><b>${g.symbol}</b> (${g.strand}) ${g.start.toLocaleString()}–${g.end.toLocaleString()} | ${g.relationship} | ${g.overlap_bp.toLocaleString()} bp</p>`).join(''):`<p>${s.annotation_status}</p>`}if(D.results.length)showChr(0);</script>"""
    (enhanced_root/"GReGOrI_SHaNE_browser.html").write_text(template.replace("__DATA__",data),encoding="utf-8")


def analyze_assembly(path_text,species,base_root,seed,step,lookahead,threshold,metadata=None,gff_path=None):
    params={"seed":seed,"step":step,"lookahead":lookahead,"threshold":threshold}
    root=assembly_folder(base_root,metadata,species,path_text); legacy_root=root/"legacy_v0.4"; enhanced=root/"enhanced_v0.4.2"; temp=root/".gregori_work"
    for p in (legacy_root,enhanced,temp): p.mkdir(parents=True,exist_ok=True)
    sig=analysis_signature(path_text,params,metadata)
    manifest_path=root/"analysis_manifest.json"
    manifest={"version":VERSION,"signature":sig,"status":"running","metadata":metadata or {},"parameters":params,"completed_chromosomes":[]}
    if manifest_path.exists():
        try:
            old=json.loads(manifest_path.read_text(encoding="utf-8"))
            if old.get("signature")==sig: manifest=old
        except Exception: pass
    manifest_path.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    genes_by_seq=load_gff_genes(gff_path); annotation_available=bool(gff_path)
    results=[]; seen={}
    for fasta in choose_fasta_files(path_text):
        for header,sequence in read_fasta_records(fasta):
            chrom=extract_chromosome_name(header); seqid=sequence_id(header); seen[chrom]=seen.get(chrom,0)+1
            if seen[chrom]>1: chrom=f"{chrom}_{seen[chrom]}"
            chrom_dir=root/safe_name(chrom); legacy_dir=chrom_dir/"legacy_v0.4"
            if chromosome_complete(chrom_dir):
                print(f"[resume] {chrom}: complete, reusing stored chromosome results")
                results.append(load_result_stub(chrom_dir)); continue
            print(f"\nProcessing {chrom} ({len(sequence):,} bp)")
            (temp/"current_chromosome.json").write_text(json.dumps({"chromosome":chrom,"sequence_id":seqid,"status":"processing"},indent=2),encoding="utf-8")
            with TerminalAnimation(f"Mapping SHaNEs on {chrom}","shane"):
                result=analyze_record(sequence,species,chrom,legacy_dir,seed,step,lookahead,threshold)
            annotate_shanes(result["shanes"],genes_by_seq.get(seqid,[]),annotation_available)
            enhanced_write(chrom_dir,chrom,seqid,result["shanes"],annotation_available)
            save_result_stub(chrom_dir,result,seqid)
            stub=load_result_stub(chrom_dir); results.append(stub)
            manifest.setdefault("completed_chromosomes",[]).append(chrom)
            manifest_path.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    write_overlap_table(results,enhanced); generate_browser(results,enhanced,metadata)
    # Preserve legacy summary naming in the legacy branch without rewriting chromosome files.
    with (legacy_root/"whole_genome_summary.tsv").open("w",encoding="utf-8",newline="") as fh:
        w=csv.writer(fh,delimiter="\t"); w.writerow(["chromosome","length_bp","raw_hits","candidate_groups","shanes"])
        for r in results: w.writerow([r["chrom"],r["length_bp"],len(r["hits"]),len(r["groups"]),len(r["shanes"])])
    (legacy_root/"whole_genome_summary.json").write_text(json.dumps({"version":VERSION,"chromosomes":[{"chromosome":r["chrom"],"length_bp":r["length_bp"],"shanes":len(r["shanes"])} for r in results]},indent=2),encoding="utf-8")
    if metadata:
        (enhanced/"assembly_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
        with (enhanced/"assembly_metadata.tsv").open("w",encoding="utf-8",newline="") as fh:
            w=csv.writer(fh,delimiter="\t"); w.writerow(["key","value"]); w.writerows((k,v) for k,v in metadata.items())
    manifest.update({"status":"complete","completed_chromosomes":[r["chrom"] for r in results]})
    manifest_path.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    current=temp/"current_chromosome.json"
    if current.exists(): current.unlink()
    print(f"\nAssembly results: {root.resolve()}")
    print(f"Browser: {(enhanced/'GReGOrI_SHaNE_browser.html').resolve()}")
    if input("Open the unified SHaNE browser now? [Y/n]: ").strip().lower() not in {"n","no"}:
        webbrowser.open((enhanced/"GReGOrI_SHaNE_browser.html").resolve().as_uri())
    return results


def main():
    configure_terminal(); print_banner()
    print("1. Analyze local FASTA or whole-genome FASTA")
    print("2. Analyze a folder of chromosome FASTAs")
    print("3. Search species on NCBI")
    print("4. Download RefSeq accession")
    print("5. Download GenBank accession")
    print("6. Exit")
    choice=input("Choose mode [1]: ").strip() or "1"
    if choice=="6": return
    species,seed,step,lookahead,threshold=get_parameters(); metadata=None; gff=None
    try:
        if choice in {"1","2"}:
            path_text=input("Enter FASTA file or FASTA folder: ").strip()
        elif choice=="3":
            query=input(f"Species to search [{species}]: ").strip() or species
            assemblies=search_ncbi_species(query)
            for i,a in enumerate(assemblies,1): print(f"{i}. {a['accession']} | {a['source']} | {a['assembly_name']} | {a['level']}")
            n=int(input("Choose assembly number [1]: ").strip() or "1"); selected=assemblies[n-1]
            path_text,gff,metadata=download_ncbi_accession(selected["accession"],selected["source"]); metadata.update(selected)
        elif choice in {"4","5"}:
            source="RefSeq" if choice=="4" else "GenBank"; accession=input(f"Enter {source} accession: ").strip()
            path_text,gff,metadata=download_ncbi_accession(accession,source); metadata.setdefault("organism",species)
        else: raise ValueError("Unknown menu choice")
        base=input("Enter results library [GReGOrI_results]: ").strip() or "GReGOrI_results"
        analyze_assembly(path_text,species,base,seed,step,lookahead,threshold,metadata,gff)
    except (FileNotFoundError,ValueError,RuntimeError,zipfile.BadZipFile) as exc:
        print(f"\nError: {exc}"); sys.exit(1)


if __name__ == "__main__":
    main()
