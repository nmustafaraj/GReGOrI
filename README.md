<p align="center">
  <img src="docs/images/banner.png" alt="GReGOrI: SHaNE Retrieval" width="100%">
</p>

<h1 align="center">GReGOrI: Genomic Repeat Grouping & Orientation Identifier</h1>

<p align="center">
  <b>A high-throughput scientific software suite for whole-genome discovery, dynamic programming duplex alignment, gene annotation superimposition, nearest-neighbor thermodynamic profiling, and interactive visualization of SHaNEs (Strict complementarity Hairpin-like Nested Elements).</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPLv3">
  <img src="https://img.shields.io/badge/Python-3.9%2B-cyan.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Bioinformatics-Genomics-brightgreen.svg" alt="Genomics">
  <img src="https://img.shields.io/badge/NCBI-Datasets%20Integrated-blueviolet.svg" alt="NCBI Datasets">
</p>

---

## What is a SHaNE?

Under standard Karlin-Altschul alignment statistics over a four-letter nucleotide background, two 1 kb sequences require approximately 30–35% sequence identity to achieve nominal statistical significance. By contrast, a **Strict complementarity Hairpin-like Nested Element (SHaNE)** represents an operational category of multi-kilobase genomic architectures delimited by discrete islands of high, near-perfect Watson-Crick base-pairing. 

The designation emphasizes three core properties. **Strict Complementarity** prioritizes exact Watson-Crick base-pairing across discrete island stems over generalized sequence similarity. **Nested Architecture** reflects an organizational structure where outer and inner complementary island stems flank and partition internal unbonded sequence intervals or localized branching hairpins. **Structural Realism** evaluates the sequence-level inverted repeat topology without presuming an obligate constitutive folded state in chromatin, acknowledging the physiological influences of chromosomal topology, nucleosome occupancy, and cellular state.

---

## Quick Start

### 1. Launch the Interactive Web Application

To launch the local web server and open the interactive graphical interface in your default browser, double-click [`Start_GReGOrI.bat`](Start_GReGOrI.bat) on Windows or execute the launcher directly:

```bash
py launcher.py
```

The application initializes a local HTTP server and connects to the interactive interface at `http://127.0.0.1:8765/`.

### 2. Command Line Interface

GReGOrI provides a modular command-line suite for automated high-throughput execution across compute clusters and standalone environments:

```bash
# Execute whole-genome discovery analysis
py -m gregori analyze genome.fasta --species "Apis mellifera" --output ./results

# Run discovery with automatic GFF3/GTF gene superimposition
py -m gregori analyze genome.fasta --species "Apis mellifera" --gff genes.gff3 --output ./results

# Interactive color terminal inspection of single chromosomes
py -m gregori inspect chromosome.fasta

# Build the standalone interactive SHaNE Browser HTML
py -m gregori browser results/central_library/GReGOrI_SHaNE_library.json --open

# Superimpose and patch assembly-locked NCBI annotations
py -m gregori annotate ./results --patch-browser --open

# Launch the Web Interface on a custom port
py -m gregori gui --port 9000
```

---

## Two-Stage Analytical Pipeline

The discovery and characterization workflow operates in two consecutive stages designed for analytical rigor and computational efficiency.

### Stage 1: Core Inverted Repeat Discovery & Duplex Thermodynamics

The discovery engine identifies inverted repeat candidates using high-throughput $k$-mer seed scanning paired with dynamic phase-shift void minimization. Candidate arms are evaluated under dynamic programming alignments to maximize Watson-Crick complementarity across opposing forward and reverse-complement strands without crossing over. Thermodynamic stability across complementary island stems is quantified using unified nearest-neighbor DNA parameters at 37°C in 50 mM monovalent cation concentrations, deriving empirical free energy ($\Delta G^\circ_{37}$) and salt-adjusted duplex melting temperatures ($T_m$). Central unbonded loops are evaluated against random base-pairing expectations to assess whether sequences have evolved under negative selection against ectopic self-folding.

### Stage 2: Gene Map Superimposition & Browser Assembly

When genomic annotations are supplied or retrieved directly from NCBI Datasets, candidate SHaNE coordinates are intersected against RefSeq and Ensembl structural gene models. The intersection engine executes bisect interval overlap analysis across coding sequences, exons, introns, and untranslated regions, determining complete containment or partial crossing events. The resulting dataset compiles into a centralized library format alongside a standalone, dependency-free interactive HTML browser.

---

## Interactive Capabilities & Legacy Console

The unified web interface coordinates analysis workflows, automated NCBI assembly searches, and parameter explorations. Users can pause analyses at safe chromosome checkpoints, resume interrupted jobs, or rerun parameter sweeps with updated thresholds. 

The bundled SHaNE Browser provides interactive chromosome ideograms, circular telemetry gauges, and dynamic quantile distribution graphs with arithmetic mean centerlines and empirical standard deviation dispersion bounds. Elements can be inspected in deep secondary structure views with base-pair ladder alignments and direct NCBI Gene hyperlinks.

For retro terminal environments, the software also includes **GReGOrI (legacy version)**, which runs inside a dedicated dark-themed browser console operating within an isolated temporary sandbox that safely purges all working files upon session closure.

---

## Architecture & Module Structure

```
GReGOrI/
├── pyproject.toml              # PEP 517/621 packaging metadata (v1.0.0)
├── LICENSE                     # GNU General Public License v3.0 (GPLv3)
├── Start_GReGOrI.bat           # 1-click Windows GUI launcher
├── launcher.py                 # Root GUI launcher script
├── README.md                   # Software documentation
│
├── gregori/                    # Unified Core Python Package
│   ├── engine/                 # Discovery engine, DP alignments, thermodynamics, terminal inspector
│   ├── annotation/             # GFF3/GTF parser, overlap engine, NCBI datasets integration
│   ├── browser/                # Standalone interactive SHaNE Browser builders & themes
│   ├── palaces/                # Enterprise architecture (Identity, Naming, Library)
│   ├── server/                 # Local HTTP server, project controller, native file dialogs
│   └── cli.py                  # Standardized multi-command CLI
│
├── frontend/                   # Web GUI Frontend Assets
│   ├── index.html              # Modern interactive web application
│   ├── legacy.html             # Retro dark interactive web console for legacy execution
│   └── assets/                 # Branding and graphical assets
│
├── docs/images/                # Documentation header banner
│
├── Legacy/                     # Original standalone terminal console script
│   └── GReGOrI (legacy version).py
│
├── bin/windows-x64/            # NCBI command-line utilities (datasets.exe, dataformat.exe)
└── tests/                      # Unified Test Suite (Engine, Browser, Annotation, Lifecycle, Smoke)
```

---

## Running the Automated Test Suite

To verify installation integrity and run the full test suite across discovery algorithms, dynamic programming alignment, thermodynamic profiling, gene overlaps, project lifecycle states, and browser rendering:

```bash
py -m unittest discover tests
```

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. For complete terms, please refer to the [`LICENSE`](LICENSE) file.

For commercial licensing, enterprise integrations, or proprietary dual-licensing inquiries, please contact the author directly.

---

## Author & Citation

**Neim Mustafaraj**  
*GReGOrI: Genomic Repeat Grouping & Orientation Identifier* (2026).

