"""Unified, modular Methods and Exploration Guide documentation for GReGOrI and SHaNE Browser."""

def get_methods_html() -> str:
    return """<div id="method-shane-concept" class="methods-section">
<h3>1. SHaNE Concept &amp; Theoretical Framework <span class="methods-badge badge-theory">Theoretical Framework</span></h3>
<p>Under standard Karlin-Altschul alignment statistics over a four-letter nucleotide background, two 1 kb sequences require ~30–35% sequence identity to achieve nominal statistical significance (E-value &lt; 0.05). By contrast, a <b><b>S</b>trict complementarity <b>H</b>airpin-like <b>N</b>ested <b>E</b>lement (<b>SHaNE</b>)</b> is defined as an operational category of <b>multi-kilobase genomic architectures delimited by discrete islands of high, near-perfect Watson-Crick complementarity</b>.</p>
<p><b>Nomenclature &amp; Biophysical Context:</b><br>
The designation—<b><b>S</b>trict complementarity <b>H</b>airpin-like <b>N</b>ested <b>E</b>lement (<b>SHaNE</b>)</b>—accounts for the architectural organization and physical constraints of multi-kilobase inverted sequences. <b>Strict Complementarity</b> emphasizes rigorous Watson-Crick base-pairing across discrete island stems rather than general sequence similarity. <b>Nested Architecture</b> reflects an organization where outer and inner complementary island stems flank and partition internal unbonded sequence intervals or localized branching hairpins. <b>Structural Realism</b> recognizes that in vivo physiological conformations of multi-kilobase inverted repeats remain subject to chromosomal topology, nucleosome occupancy, and cellular state, describing the sequence-level inverted architecture without presuming an obligate constitutive folded state in chromatin.</p>
<p><b>Evolutionary Analysis:</b><br>
Large-scale inverted repeats introduce potential topological instability during DNA replication and transcription. Evaluating the cross-species conservation, syntenic persistence, and sequence divergence of these nested inverted elements across evolutionary lineages provides a framework to examine whether specific architectures are subject to purifying selection.</p>
<div class="methods-ref"><b>Primary Literature &amp; Alignment Statistics:</b><br>
Karlin, S., &amp; Altschul, S. F. (1990). <i>Methods for assessing the statistical significance of molecular sequence features by using general scoring schemes</i>. <b>Proc. Natl. Acad. Sci. USA</b>, 87(6), 2264–2268. DOI: <a href="https://doi.org/10.1073/pnas.87.6.2264" target="_blank">10.1073/pnas.87.6.2264</a><br><br>
Karlin, S., &amp; Altschul, S. F. (1993). <i>Applications and statistics for multiple high-scoring segments in molecular sequences</i>. <b>Proc. Natl. Acad. Sci. USA</b>, 90(12), 5873–5877. DOI: <a href="https://doi.org/10.1073/pnas.90.12.5873" target="_blank">10.1073/pnas.90.12.5873</a><br><br>
Altschul, S. F., Gish, W., Miller, W., Myers, E. W., &amp; Lipman, D. J. (1990). <i>Basic local alignment search tool</i>. <b>Journal of Molecular Biology</b>, 215(3), 403–410. DOI: <a href="https://doi.org/10.1016/S0022-2836(05)80360-2" target="_blank">10.1016/S0022-2836(05)80360-2</a>
</div>
</div>
<div id="method-hypotheses" class="methods-section">
<h3>2. Hypothetical Biological Functions <span class="methods-badge badge-spec">Hypothetical / Speculative</span></h3>
<p>While the physical existence of multi-kilobase inverted repeats is verifiable computationally and experimentally, their exact in vivo cellular utilities remain active hypotheses that require direct experimental testing.</p>
<p><b>Gene Duplication &amp; Functional Innovation (Hypothetical):</b> Multi-kilobase inverted arms frequently encompass entire genes or regulatory cassettes. They provide natural structural substrates for non-allelic homologous recombination (NAHR), initiating gene duplication events, neo-functionalization, and rapid regulatory diversification.</p>
<p><b>Chromatin Architecture &amp; Heterochromatin-to-Euchromatin Transition (Hypothetical):</b> Under physiological negative supercoiling (σ ≈ -0.06), the spontaneous extrusion of giant cruciform or hairpin loops can alter local topological writhe, displacing canonical nucleosomes and promoting chromatin decondensation—hypothetically converting transcriptionally silent heterochromatin into accessible euchromatin.</p>
<p><b>Proximal Promoter &amp; Regulatory Topological Hubs (Hypothetical):</b> Inverted arms bring distal regulatory sequences and transcription factor binding sites (TFBS) into spatial proximity at the stem base, potentially functioning as insulator boundaries or super-enhancer scaffolds for proximal flanking genes.</p>
<p><b>Central Loop Mutational Hotspots (Hypothetical):</b> Unbonded single-stranded DNA (ssDNA) exposed within giant central loops is intrinsically vulnerable to hydrolytic cytosine deamination (C → U), APOBEC/AID cytidine deaminase editing, and transcription-replication conflicts, potentially acting as localized evolutionary mutation generators.</p>
<div class="methods-ref"><b>Conceptual References &amp; Chromatin Biophysics:</b><br>
Sinden, R. R. (1994). <i>DNA Structure and Function</i>. Academic Press. ISBN: 978-0-12-645750-6.<br>
Voineagu, I., Narayanan, V., Lobachev, K. S., &amp; Mirkin, S. M. (2008). <i>Inverted repeats: a source of genomic instability in eukaryotic genomes</i>. <b>Nature Reviews Genetics</b>, 9(10), 738–749. DOI: <a href="https://doi.org/10.1038/nrg2438" target="_blank">10.1038/nrg2438</a>
</div>
</div>
<div id="method-duplex" class="methods-section">
<h3>3. Inverted Repeat Detection &amp; Watson-Crick Duplex Alignment <span class="methods-badge badge-lit">Algorithmic Method</span></h3>
<p>GReGOrI detects candidate SHaNEs using inverted repeat alignment algorithms with dynamic phase-shift void minimization. The maximized Watson-Crick score (S) is defined as:</p>
<div style="font-family:Consolas,monospace;background:#050a18;padding:10px 14px;border-radius:6px;margin:8px 0;color:#25d9f4;font-size:12px;">Score (S) = (Canonical A-T + G-C Watson-Crick Pairings) / Total Duplex Alignment Length</div>
<p>Dynamic voids (<code style="color:#8fa5c8;">.</code>) are phase-shift gap insertions dynamically computed via dynamic programming to optimize interisland duplex complementarity across opposing forward and reverse-complement arms without crossing over.</p>
</div>
<div id="method-thermo" class="methods-section">
<h3>4. Duplex Nearest-Neighbor Thermodynamics &amp; Melting Temperature (T<sub>m</sub>) <span class="methods-badge badge-lit">Peer-Reviewed Literature</span></h3>
<p>Thermodynamic stability of complementary island duplex stems is calculated using unified nearest-neighbor DNA parameters at 37°C in 50 mM monovalent cation concentration ([Na<sup>+</sup>] = 50 mM), with oligonucleotide concentration C<sub>T</sub> = 0.2 μM:</p>
<div style="font-family:Consolas,monospace;background:#050a18;padding:10px 14px;border-radius:6px;margin:8px 0;color:#32d399;font-size:12px;line-height:1.7;">ΔG°₃₇ = ΔH° - T · ΔS°<br>T<sub>m</sub> (°C) = 81.5 + 16.6 · log₁₀([Na⁺]) + 0.41 · (%GC) - (500 / Length) - 0.61 · (%mismatch)</div>
<div class="methods-ref"><b>Primary Literature Citations:</b><br>
SantaLucia, J. (1998). <i>A unified view of polymer, dumbbell, and oligonucleotide DNA nearest-neighbor thermodynamics</i>. <b>Proc. Natl. Acad. Sci. USA</b>, 95(4), 1460–1465. DOI: <a href="https://doi.org/10.1073/pnas.95.4.1460" target="_blank">10.1073/pnas.95.4.1460</a><br><br>
SantaLucia, J., &amp; Hicks, D. (2004). <i>The thermodynamics of DNA structural motifs</i>. <b>Annu. Rev. Biophys. Biomol. Struct.</b>, 33, 415–440. DOI: <a href="https://doi.org/10.1146/annurev.biophys.32.110601.141800" target="_blank">10.1146/annurev.biophys.32.110601.141800</a><br><br>
Owczarzy, R., You, Y., Moreira, B. G., Manthey, J. A., Huang, L., Behlke, M. A., &amp; Walder, J. A. (2004). <i>Effects of sodium ions on DNA duplex oligomers: Improved predictions of melting temperatures</i>. <b>Biochemistry</b>, 43(12), 3537–3554. DOI: <a href="https://doi.org/10.1021/bi034621r" target="_blank">10.1021/bi034621r</a>
</div>
</div>
<div id="method-loop" class="methods-section">
<h3>5. Central Loop Analysis &amp; Evolutionary Non-Folding <span class="methods-badge badge-theory">Mathematical Model &amp; Hypothesis</span></h3>
<p>For SHaNEs possessing a central unbonded region between the innermost 5′ and 3′ island stems, GReGOrI evaluates whether sequence composition has evolved under negative selection against ectopic self-folding:</p>
<div style="font-family:Consolas,monospace;background:#050a18;padding:10px 14px;border-radius:6px;margin:8px 0;color:#25d9f4;font-size:12px;line-height:1.7;">Expected Random Pairing: P<sub>rand</sub> = 2 · (f<sub>A</sub> · f<sub>T</sub> + f<sub>G</sub> · f<sub>C</sub>) for nucleotide frequencies f<sub>N</sub><br>Actual Direct Score: S<sub>dir</sub> = Direct un-gapped foldover Watson-Crick match %<br>Actual Optimized Score: S<sub>opt</sub> = DP-aligned dynamic void Watson-Crick match %</div>
<p><b>Why Sequences Evolve to Remain Unfolded:</b><br>
While multi-kilobase inverted repeats possess theoretical potential for secondary structure folding, in vivo chromosomal DNA is constrained by replication, transcription, and chromatin compaction. Unregulated, ectopic intra-loop folding could stall replication forks, impede transcription, or trigger severe topological shear. Consequently, central loop domains often exhibit nucleotide composition that is depleted in self-complementarity (where actual pairing S<sub>opt</sub> is significantly below random expectation P<sub>rand</sub>), having <b>"evolved to remain unfolded"</b>—preserving an open, flexible single-stranded state to prevent aberrant folding under native physiological conditions.</p>
<p style="font-size:11.5px;color:#8fa5c8;margin-top:6px;"><i>*Quality Control Note:</i> If a central loop contains unsequenced/ambiguous null (<code>N</code>) bases, thermodynamic and self-folding statistical calculations are strictly bypassed to prevent artifactual scoring.</p>
</div>
<div id="method-branch" class="methods-section">
<h3>6. Branching Hairpin Topology Classification <span class="methods-badge badge-lit">Algorithmic Method</span></h3>
<p>Internal secondary hairpin branches within interisland intervals or flanking arms are identified by systematic local inverted-repeat search. Structural topologies are classified into unbranched (canonical single-hairpin stem), 3-way, 4-way, and multi-branch junction architectures.</p>
</div>
<div id="method-genes" class="methods-section">
<h3>7. Genomic Annotation &amp; Gene-Crossing <span class="methods-badge badge-lit">Genomic Standard</span></h3>
<p>SHaNE genomic coordinates are intersected against NCBI RefSeq and Ensembl structural gene annotations to identify complete and partial overlaps across coding sequences, exons, introns, and untranslated regions (UTRs).</p>
</div>
<div id="method-quantiles" class="methods-section">
<h3>8. Quantile Grouping, Mean (μ), and Standard Deviation (±1σ) <span class="methods-badge badge-lit">Statistical Methods</span></h3>
<p>To accurately visualize metrics that span wide numerical ranges (such as SHaNE size spanning from 500 bp to 80+ kb, score, or GC percentage), GReGOrI applies sample quantile partitioning along with parametric distribution overlays.</p>
<p><b>Adaptive Quantile Binning:</b> Continuous metrics are partitioned using dynamic sample quantiles (Q<sub>0</sub> to Q<sub>k</sub>), ensuring that sparse and dense regions of the population are grouped equitably without distorting distribution contours or obscuring low-frequency outliers.</p>
<p><b>Mean (μ) Centerline:</b> The arithmetic mean of the metric distribution is computed across the population and projected as a vertical dashed line with an active value badge at the top of the telemetry chart.</p>
<p><b>Standard Deviation Zone (±1σ):</b> The empirical standard deviation (σ) is rendered as a distinct semi-transparent zone spanning [μ - σ, μ + σ]. This visually delineates the central 68.2% dispersion of typical elements from extreme structural variants.</p>
</div>
<div id="method-recommendations" class="methods-section">
<h3>9. Parameter Recommendations &amp; Practical Exploration Guide <span class="methods-badge badge-lit">Exploration Guide</span></h3>
<p><b>Recommended Search Parameters:</b><br>
We recommend an exploration forward search window of <b>40 kb</b> and a <b>99% complementarity score threshold</b> with varying search sampling steps (though <b>1 kb sampling stepping mines out the vast majority of structures</b>). Our empirical benchmarks across diverse eukaryotic assemblies demonstrate that the most compelling, structurally coherent SHaNEs span within the <b>~20 kb range</b> and consistently possess core duplex islands of very high Watson-Crick complementarity.</p>

<p><b>Caveats at Ultra-Long Lookahead Distances (&gt;70–80 kb):</b><br>
Caution is advised when extending search windows to 70–80+ kb. At these extreme lookaheads, isolated 70 kb-distant matches can occasionally pop out with no other visible intervening internal complementary islands, as well as SHaNE architectures possessing tandem repeating arms (which the software handles in experimental beta mode).</p>

<p><b>RECOMMENDATION — Pushing a SHaNE to Its Maximal Physical Limits:</b><br>
To discover the farthest stretches and comprehensive boundaries of a candidate SHaNE lineage, <b>keep the search window at the default (20–40 kb) BUT lower the island expansion score (e.g. from 0.99 down to 0.95 or 0.85)</b>. Lowering the expansion threshold triggers a continuous <i>peripheral expansion</i> along both 5′ and 3′ arms that pushes the structure to its true physical limits without introducing false distant matches.</p>

<p style="font-size:11.5px;color:var(--muted);margin-top:6px;border-top:1px solid #1c2e4d;padding-top:6px;">
<b>*Note on Default Parameters:</b> The default parameters (1,000 bp sampling step, 20 kb window, 0.99 score threshold) are specifically engineered not to deliver the most exhaustive possible results, but to provide the <b>fastest</b> (1 kb sampling) and <b>safest / highest-confidence</b> (99% score threshold) baseline detection.
</p>
</div>
<div id="method-legacy-terminal" class="legacy-terminal-card" onclick="launchLegacyTerminal()" title="Run Legacy GReGOrI in a terminal console">
  Run Legacy GReGOrI
</div>"""
