"""GReGOrI Scientific Discovery Engine."""
from __future__ import annotations

from .alignment import (
    align_islands_wc,
    align_loops_wc,
    format_alignment,
    get_reverse_complement,
    is_wc_pair,
    pairline,
    rc,
    similarity,
)
from .core import (
    analyse_sequence,
    enrich_shane_details,
    expand_islands,
    expand_paths,
    group_hits,
    inspect_sequences,
    open_fasta,
    records,
    scan_seeds,
    write_outputs,
)
from .pipeline import (
    run_single_sequence_pipeline,
    run_whole_genome_batch_pipeline,
)
from .plotting import is_plotting_available, save_visualizations
from .terminal import (
    Spinner,
    configure_terminal,
    interactive_terminal_inspect,
    print_progress,
)
