# GReGOrI: Genomic Repeat Grouping & Orientation Identifier

**GReGOrI** is a high-throughput scientific software suite for whole-genome discovery, dynamic programming duplex alignment, gene annotation superimposition, nearest-neighbor thermodynamic profiling, and interactive visualization of **SHaNEs** (Strict complementarity Hairpin-like Nested Elements).

---

## Quick Start

### 1. Launch the Web Interface (1-Click)
Double-click [`Start_GReGOrI.bat`](Start_GReGOrI.bat) or run:
```bash
py launcher.py
```
This starts the local HTTP backend and opens the modern Palaces interactive web application at `http://127.0.0.1:8765/`.

### 2. Command Line Interface (`py -m gregori`)

```bash
# 1. Run whole-genome discovery analysis
py -m gregori analyze genome.fasta --species "Apis mellifera" --output ./results

# 2. Run analysis with Gene Map (GFF3/GTF) for automatic gene superimposition
py -m gregori analyze genome.fasta --species "Apis mellifera" --gff genes.gff3 --output ./results

# 3. Interactive color terminal inspection
py -m gregori inspect chromosome.fasta

# 4. Build standalone interactive SHaNE Browser v4.2 HTML
py -m gregori browser results/central_library/GReGOrI_SHaNE_library.json --open

# 5. Correct/superimpose assembly-locked NCBI gene annotations
py -m gregori annotate ./results --patch-browser --open

# 6. Launch Web Interface on a custom port
py -m gregori gui --port 9000
```

---

## Two-Stage Analysis Workflow

1. **Stage 1 — Core Discovery**:
   - High-throughput seed scanning (`k=20`, step sampling, lookahead window).
   - Strict collinear geometric nesting enforcing distance contraction slopes.
   - Dynamic island expansion under configurable complementarity thresholds.
   - Watson-Crick dynamic programming alignment and loop folding statistics.
   - Unified nearest-neighbor duplex thermodynamics ($\Delta G^\circ_{37}$, $T_m$).

2. **Stage 2 — Gene Map Superimposition**:
   - If an annotation map is available (either auto-downloaded from NCBI or provided via **Browse Gene Map / GFF3**):
     - Parses genes, pseudogenes, biotypes, and symbols.
     - Runs fast bisect interval overlap analysis (`gene_contained_in_SHaNE`, `SHaNE_contained_in_gene`, `partial_overlap`).
     - Links each gene to direct NCBI Gene pages.
   - Generates the centralized `GReGOrI_SHaNE_library.json` and interactive **SHaNE Browser v4.2** with superimposed genes clearly highlighted.

---

## Project Lifecycle & Management

- **Pause & Resume**: Pause running analyses at safe chromosome checkpoints and resume seamlessly.
- **Restart**: Cleanly restart any interrupted, cancelled, or failed analysis run.
- **Rerun**: Rerun completed analyses with updated parameters.
- **Delete**: Remove any project in any state from the workspace into trash.

---

## Architecture & Module Structure

```
GReGOrI/
├── pyproject.toml              # PEP 517/621 packaging metadata
├── LICENSE                     # MIT Open-Source License
├── Start_GReGOrI.bat           # 1-click Windows GUI launcher
├── launcher.py                 # Root GUI launcher script
├── README.md                   # Software documentation
│
├── gregori/                    # Unified Core Python Package
│   ├── engine/                 # Core discovery, DP alignments, thermodynamics, plotting, terminal inspector
│   ├── annotation/             # GFF3/GTF parser, overlap engine, NCBI datasets integration
│   ├── browser/                # Standalone interactive SHaNE Browser v4.2 builders & themes
│   ├── palaces/                # Enterprise Palaces architecture (Identity, Naming, Library)
│   ├── server/                 # Local HTTP server, project controller, native file dialogs
│   └── cli.py                  # Standardized multi-command CLI
│
├── frontend/                   # Web GUI Frontend Assets
│   ├── index.html              # Modern Palaces interactive web app
│   ├── legacy.html             # Retro dark interactive web console for Legacy GReGOrI
│   └── assets/                 # GReGOrI and SHaNE branding assets
│
├── Legacy/                     # Original standalone terminal console script
│   └── GReGOrI_v0.4.2_Legacy.py
│
├── bin/windows-x64/            # NCBI command-line utilities (datasets.exe, dataformat.exe)
└── tests/                      # Unified Test Suite (Engine, Browser, Annotation, Lifecycle, Smoke)
```

---

## Running the Automated Test Suite

```bash
py -m unittest discover tests
```
Runs the comprehensive unit and integration test suite across the discovery engine, dynamic programming duplex alignment, gene overlap calculator, Palaces rich library validation, project lifecycle mutations, NCBI annotation pipelines, and end-to-end browser smoke tests.

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)** — see the [`LICENSE`](LICENSE) file for details.

*For commercial licensing, enterprise integration, or proprietary dual-licensing inquiries, contact the author.*

---

## Author & Citation

**Neim Mustafaraj**  
*GReGOrI: Genomic Repeat Grouping & Orientation Identifier* (2026).

