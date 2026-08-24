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

## 1. Theoretical Framework & The SHaNE Concept

Under standard Karlin-Altschul alignment statistics across an independent four-letter nucleotide background, two 1 kb sequences require approximately 30–35% sequence identity to achieve nominal statistical significance ($E$-value $< 0.05$). By contrast, a **Strict complementarity Hairpin-like Nested Element (SHaNE)** represents an operational category of multi-kilobase genomic architectures delimited by discrete islands of high, near-perfect Watson-Crick base-pairing.

The architectural designation encompasses three core biophysical and computational principles:

* **Strict Complementarity**: Emphasizes rigorous Watson-Crick base-pairing across discrete island stems rather than generalized sequence similarity or loose homology.
* **Nested Architecture**: Captures an organizational structure wherein outer and inner complementary island stems flank and partition internal unbonded sequence intervals, dynamic voids, and localized branching hairpins.
* **Structural Realism**: Recognizes that *in vivo* physiological conformations of multi-kilobase inverted repeats remain subject to chromosomal topology, nucleosome occupancy, and cellular state, describing the sequence-level inverted architecture without presuming an obligate constitutive folded state in chromatin.

### Evolutionary Analysis & Purifying Selection

Large-scale inverted repeats introduce potential topological instability during DNA replication and transcription. Evaluating cross-species conservation, syntenic persistence, and sequence divergence of these nested inverted elements across evolutionary lineages provides a rigorous comparative framework to examine whether specific SHaNE architectures are conserved under purifying selection.

---

## 2. Hypothetical Biological Functions

While the physical existence of multi-kilobase inverted repeats is verifiable computationally and experimentally, their exact *in vivo* cellular utilities represent active scientific hypotheses subject to ongoing experimental validation:

* **Gene Duplication & Functional Innovation**: Multi-kilobase inverted arms frequently encompass entire genes or regulatory cassettes. They provide natural structural substrates for non-allelic homologous recombination (NAHR), initiating gene duplication events, neo-functionalization, and rapid regulatory diversification.
* **Chromatin Architecture & Heterochromatin-to-Euchromatin Transition**: Under physiological negative supercoiling ($\sigma \approx -0.06$), the spontaneous extrusion of giant cruciform or hairpin loops can alter local topological writhe, displacing canonical nucleosomes and promoting chromatin decondensation—hypothetically facilitating the conversion of transcriptionally silent heterochromatin into accessible euchromatin.
* **Proximal Promoter & Regulatory Topological Hubs**: Inverted arms bring distal regulatory sequences and transcription factor binding sites (TFBS) into spatial proximity at the stem base, potentially functioning as insulator boundaries or super-enhancer scaffolds for proximal flanking genes.
* **Central Loop Mutational Hotspots**: Unbonded single-stranded DNA (ssDNA) exposed within giant central loops is intrinsically vulnerable to hydrolytic cytosine deamination ($\text{C} \to \text{U}$), APOBEC/AID cytidine deaminase editing, and transcription-replication conflicts, potentially acting as localized evolutionary mutation generators.

---

## 3. Interactive Web Application & Analysis Workflows

GReGOrI provides a modern, responsive web application connecting high-throughput backend discovery with interactive browser telemetry.

<p align="center">
  <img src="docs/images/homepage%20(EHaB%20is%20inactive).png" alt="GReGOrI Main Dashboard & Project Hub" width="100%">
</p>

The platform supports three standard analysis workflows:

* **Custom Analysis**: High-throughput whole-genome discovery on local FASTA files or directories of scaffold sequences with user-configurable parameters.
* **NCBI Analysis**: Direct integration with the NCBI Datasets API to search, download, and analyze reference assemblies and GFF3 gene annotations automatically.
* **Chain Analysis**: Multi-run exploration chaining parameter permutations across sliding search windows and expansion thresholds.

<p align="center">
  <img src="docs/images/NCBI%20sourced%20genomes%20data%20analysis.png" alt="NCBI Sourced Genomes Data Analysis" width="100%">
</p>

### Built-in 1-Click NCBI Datasets Installer

The interface features an integrated, self-updating installer button for the official NCBI `datasets` and `dataformat` command-line binaries. When opening the NCBI workflow, GReGOrI automatically checks binary availability and offers 1-click downloads directly from NCBI FTP servers, auto-configuring system paths across Windows, Linux, and macOS platforms.

---

## 4. Multi-Chromosome Discovery & Grouped Scaffold Output

GReGOrI executes high-throughput discovery across whole-genome assemblies, organizing results by chromosome, linkage group, or unplaced scaffold.

<p align="center">
  <img src="docs/images/Grouped%20Sequences%20Output.png" alt="Grouped Sequences Output" width="100%">
</p>

The project manager incorporates real-time lifecycle controls:

* **Safe Checkpoints & Pausing**: Pause running whole-genome analyses at safe chromosome boundaries and resume seamlessly without loss of computed structures.
* **Restart & Rerun**: Restart interrupted or failed runs, or rerun completed projects under updated sensitivity parameters.
* **Multi-Format Export**: Generates standardized JSON libraries, GFF3 annotation patches, and standalone interactive browser bundles.

---

## 5. The Standalone Interactive SHaNE Browser

Each analyzed assembly compiles into a self-contained, dependency-free interactive HTML browser providing comprehensive structural and genomic telemetry.

<p align="center">
  <img src="docs/images/SHaNE%20chromosomal%20atlas.png" alt="SHaNE Chromosomal Atlas" width="100%">
</p>

### Chromosomal Atlas & Multi-Track Ideograms

The browser maps discovered SHaNEs across whole chromosomes with interactive coordinate zooming, highlighted inverted repeat spans, and superimposed gene model tracks.

<p align="center">
  <img src="docs/images/Stat%20Gears%20and%20graphic%20view.png" alt="Telemetry Gauge Rings and Distribution Telemetry" width="100%">
</p>

### Telemetry Gauge Rings & Dynamic Quantile Distribution

* **Telemetry Gauge Rings**: Instant distribution metrics for multi-island elements ($\text{Islands} \ge 2$), gene-crossing architectures ($\text{Gene-crossing} \ge 1$), Watson-Crick score thresholds, and GC content percentages. Clicking any ring dynamically filters the entire genomic view.
* **Quantile Distribution Overlays**: Continuous metrics are partitioned using dynamic sample quantiles ($Q_0 \dots Q_k$) with arithmetic mean ($\mu$) centerlines and empirical standard deviation ($\mu \pm 1\sigma$, central 68.2%) dispersion bands to identify typical architectures from extreme structural outliers.

<p align="center">
  <img src="docs/images/automated%20in-Genome%20Data%20Viewer-annotation.png" alt="Automated In-Genome Data Viewer & Annotation" width="100%">
</p>

---

## 6. Deep Element Inspection & Multi-Layer Biophysical Telemetry

Clicking any candidate SHaNE opens an extensive multi-tab inspection modal presenting detailed biophysical, thermodynamic, and topological properties:

### 1. Discrete Watson-Crick Island Stems

<p align="center">
  <img src="docs/images/island%20data%20viewer.png" alt="Island Data Viewer" width="100%">
</p>

Visualizes individual complementary duplex islands, their genomic coordinate spans, mismatch rates, and localized thermodynamic melting profiles.

### 2. Complete Secondary Structure Duplex Fold

<p align="center">
  <img src="docs/images/complete%20Structure%20Fold(optimised).png" alt="Complete Structure Fold (Optimized)" width="100%">
</p>

Renders the full Watson-Crick base-pair ladder alignment with dynamic void phase-shift insertions across opposing 5′ and 3′ arms.

### 3. Central Loop Analysis & The "Evolved to Remain Unfolded" Model

<p align="center">
  <img src="docs/images/central%20,,loop,,%20analysis.png" alt="Central Loop Analysis" width="100%">
</p>

Evaluates whether the unbonded central sequence between the innermost 5′ and 3′ stems is depleted in self-complementarity, testing the hypothesis that central loop domains evolved under negative selection to remain open and single-stranded, avoiding replication fork stalling and topological shear.

### 4. Putative Branching Hairpin Annotator

<p align="center">
  <img src="docs/images/putative%20branching%20annotator.png" alt="Putative Branching Annotator" width="100%">
</p>

Systematically detects localized secondary hairpins within interisland intervals or flanking arms, classifying topologies into unbranched, 3-way, 4-way, and multi-branch junction configurations.

### 5. Gene-Crossing Overlap Engine

<p align="center">
  <img src="docs/images/genes-crossed%20window.png" alt="Genes-Crossed Window" width="100%">
</p>

Intersects SHaNE genomic coordinates with RefSeq and Ensembl annotations, quantifying overlap across exons, introns, CDS, and UTRs with direct hyperlinks to NCBI Gene pages.

### 6. Raw Sequence Inspector

<p align="center">
  <img src="docs/images/the%20raw%20sequence.png" alt="Raw Sequence Inspector" width="100%">
</p>

Displays full-resolution nucleotide sequences with color-coded Watson-Crick base highlighting, GC content indicators, and genomic coordinate indices.

---

## 7. Mathematical Formulations & Algorithmic Methods

### Inverted Repeat Detection & Watson-Crick Duplex Alignment

GReGOrI detects candidate SHaNEs using inverted repeat alignment algorithms with dynamic phase-shift void minimization. The maximized Watson-Crick score ($S$) is defined as:

$$\text{Score } (S) = \frac{\text{Canonical A-T + G-C Watson-Crick Pairings}}{\text{Total Duplex Alignment Length}}$$

Dynamic voids ($\texttt{.}$) are phase-shift gap insertions dynamically computed via dynamic programming to optimize interisland duplex complementarity across opposing forward and reverse-complement arms without crossing over.

### Duplex Nearest-Neighbor Thermodynamics & Melting Temperature ($T_m$)

Thermodynamic stability of complementary island duplex stems is calculated using unified nearest-neighbor DNA parameters at 37°C in 50 mM monovalent cation concentration ($[\text{Na}^+] = 50\text{ mM}$), with oligonucleotide concentration $C_T = 0.2\ \mu\text{M}$:

$$\Delta G^\circ_{37} = \Delta H^\circ - T \cdot \Delta S^\circ$$

$$T_m\ (^\circ\text{C}) = 81.5 + 16.6 \cdot \log_{10}([\text{Na}^+]) + 0.41 \cdot (\text{\\% GC}) - \left(\frac{500}{\text{Length}}\right) - 0.61 \cdot (\text{\\% mismatch})$$

> ### ⚠️ Critical Scientific Warning: Thermodynamic Limitations & Biological Context
> **The thermodynamic free energy ($\Delta G^\circ_{37}$) and melting temperature ($T_m$) metrics computed by GReGOrI are derived under standardized in vitro physical parameters ($T = 37^\circ\text{C}$, $[\text{Na}^+] = 50\text{ mM}$, $C_T = 0.2\ \mu\text{M}$), representative of standard mammalian / human homeothermic somatic conditions.**
> 
> When analyzing non-mammalian genomes—such as poikilothermic insects (*Apis mellifera*), reptiles, psychrophilic or thermophilic bacteria, plants, or extremophiles—these calculations represent a standardized comparative reference rather than the true physiological stability *in vivo*. In living cells, chromatin folding, histone and non-histone protein binding, nuclear macromolecular crowding, variable divalent cation concentrations ($[\text{Mg}^{2+}]$), and polyamines substantially alter duplex energetics. Users must interpret these values within their specific biological context and avoid assuming constitutive in vivo duplex formation.

### Central Loop Analysis & Evolutionary Non-Folding

For SHaNEs possessing a central unbonded region between the innermost 5′ and 3′ island stems, GReGOrI evaluates whether sequence composition has evolved under negative selection against ectopic self-folding:

$$\text{Expected Random Pairing: } P_{\text{rand}} = 2 \cdot (f_A \cdot f_T + f_G \cdot f_C) \quad \text{for nucleotide frequencies } f_N$$

$$\text{Actual Direct Score: } S_{\text{dir}} = \text{Direct un-gapped foldover Watson-Crick match \%}$$

$$\text{Actual Optimized Score: } S_{\text{opt}} = \text{DP-aligned dynamic void Watson-Crick match \%}$$

If a central loop contains unsequenced or ambiguous null ($\texttt{N}$) bases, thermodynamic and self-folding statistical calculations are strictly bypassed to prevent artifactual scoring.

### Primary Literature Citations

* **Karlin, S., & Altschul, S. F. (1990).** *Methods for assessing the statistical significance of molecular sequence features by using general scoring schemes.* **Proc. Natl. Acad. Sci. USA**, 87(6), 2264–2268. DOI: [10.1073/pnas.87.6.2264](https://doi.org/10.1073/pnas.87.6.2264)
* **Karlin, S., & Altschul, S. F. (1993).** *Applications and statistics for multiple high-scoring segments in molecular sequences.* **Proc. Natl. Acad. Sci. USA**, 90(12), 5873–5877. DOI: [10.1073/pnas.90.12.5873](https://doi.org/10.1073/pnas.90.12.5873)
* **Altschul, S. F., Gish, W., Miller, W., Myers, E. W., & Lipman, D. J. (1990).** *Basic local alignment search tool.* **Journal of Molecular Biology**, 215(3), 403–410. DOI: [10.1016/S0022-2836(05)80360-2](https://doi.org/10.1016/S0022-2836(05)80360-2)
* **SantaLucia, J. (1998).** *A unified view of polymer, dumbbell, and oligonucleotide DNA nearest-neighbor thermodynamics.* **Proc. Natl. Acad. Sci. USA**, 95(4), 1460–1465. DOI: [10.1073/pnas.95.4.1460](https://doi.org/10.1073/pnas.95.4.1460)
* **SantaLucia, J., & Hicks, D. (2004).** *The thermodynamics of DNA structural motifs.* **Annu. Rev. Biophys. Biomol. Struct.**, 33, 415–440. DOI: [10.1146/annurev.biophys.32.110601.141800](https://doi.org/10.1146/annurev.biophys.32.110601.141800)
* **Owczarzy, R., et al. (2004).** *Effects of sodium ions on DNA duplex oligomers: Improved predictions of melting temperatures.* **Biochemistry**, 43(12), 3537–3554. DOI: [10.1021/bi034621r](https://doi.org/10.1021/bi034621r)
* **Voineagu, I., Narayanan, V., Lobachev, K. S., & Mirkin, S. M. (2008).** *Inverted repeats: a source of genomic instability in eukaryotic genomes.* **Nature Reviews Genetics**, 9(10), 738–749. DOI: [10.1038/nrg2438](https://doi.org/10.1038/nrg2438)
* **Sinden, R. R. (1994).** *DNA Structure and Function.* Academic Press. ISBN: 978-0-12-645750-6.

---

## 8. Parameter Recommendations & Exploration Guide

### Recommended Search Parameters

For exploratory discovery across eukaryotic genomes, we recommend an initial forward search window of **40 kb** with a **99% complementarity score threshold** and a **1 kb sampling step**. Empirical benchmarks demonstrate that 1 kb stepping successfully mines the vast majority of coherent structural lineages while delivering optimal throughput. The most compelling, structurally stable SHaNEs typically span within the **~20 kb range** with high core duplex island complementarity.

### Pushing a SHaNE to Its Maximal Physical Limits

To discover the outermost boundaries and farthest stretches of a candidate SHaNE lineage, **maintain the search window at the default (20–40 kb) while lowering the island expansion threshold (e.g. from 0.99 down to 0.95 or 0.85)**. Lowering the expansion threshold triggers continuous *peripheral expansion* along opposing 5′ and 3′ arms, expanding the structure to its physical limits without introducing false distant matches.

### Caveats at Ultra-Long Lookahead Distances (>70–80 kb)

Caution is advised when extending lookahead search windows beyond 70–80 kb. At these extreme distances, isolated matches can occasionally emerge without intervening complementary islands, as well as complex tandem repeating arms.

---

## 9. GReGOrI (legacy version) Interactive Web Console

For users conducting targeted manual inspections or testing legacy parameter configurations, GReGOrI includes a dedicated retro web console interface for [`GReGOrI (legacy version).py`](Legacy/GReGOrI%20(legacy%20version).py).

The console operates inside an unbuffered interactive Python subprocess connected to the browser via streaming REST endpoints. Each console session is assigned an **isolated temporary filesystem sandbox**, ensuring that all intermediate working files and cache directories generated during exploration are automatically purged upon tab closure or session interruption.

---

## 10. Quick Start & Command Line Interface

### 1-Click Launch (Web Interface)

Double-click [`Start_GReGOrI.bat`](Start_GReGOrI.bat) on Windows or execute:

```bash
py launcher.py
```

The application starts the local HTTP backend and connects to the interactive GUI at `http://127.0.0.1:8765/`.

### CLI Command Reference

```bash
# 1. Whole-genome discovery analysis
py -m gregori analyze genome.fasta --species "Apis mellifera" --output ./results

# 2. Discovery with automatic GFF3 gene superimposition
py -m gregori analyze genome.fasta --species "Apis mellifera" --gff genes.gff3 --output ./results

# 3. Interactive color terminal chromosome inspector
py -m gregori inspect chromosome.fasta

# 4. Build standalone interactive SHaNE Browser HTML
py -m gregori browser results/central_library/GReGOrI_SHaNE_library.json --open

# 5. Superimpose and patch assembly-locked NCBI annotations
py -m gregori annotate ./results --patch-browser --open

# 6. Launch Web Interface on a custom port
py -m gregori gui --port 9000
```

---

## 11. Architecture & Module Structure

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
├── docs/images/                # Documentation screenshots & header banner
│
├── Legacy/                     # Original standalone terminal console script
│   └── GReGOrI (legacy version).py
│
├── bin/windows-x64/            # NCBI command-line utilities (datasets.exe, dataformat.exe)
└── tests/                      # Unified Test Suite (Engine, Browser, Annotation, Lifecycle, Smoke)
```

---

## 12. Running the Automated Test Suite

```bash
py -m unittest discover tests
```

Executes the comprehensive unit and integration test suite across core discovery algorithms, dynamic programming alignment, thermodynamic profiling, gene overlap calculators, Palaces rich library validation, project lifecycle mutations, NCBI annotation pipelines, and browser rendering.

---

## 13. License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)** — see the [`LICENSE`](LICENSE) file for complete terms.

*For commercial licensing, enterprise integrations, or proprietary dual-licensing inquiries, please contact the author.*

---

## 14. Author & Citation

**Neim Mustafaraj**  
*GReGOrI: Genomic Repeat Grouping & Orientation Identifier* (2026).

---

## 15. Acknowledgements & AI Assistance Disclosure

The computational architecture, mathematical algorithms, and scientific framework of GReGOrI were conceived and directed by **Neim Mustafaraj**. Generative artificial intelligence systems (including Google DeepMind's Gemini, Antigravity coding assistants and Microsoft's Copilot) were utilized as pair-programming and refactoring tools during software development, aiding in code optimization, documentation formatting, test suite authoring, and UI refinement. All biological concepts, algorithmic logic, and computational outputs were curated, validated, and verified by the author.
