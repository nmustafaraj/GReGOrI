"""GReGOrI Gene Annotation and Overlap Engine."""
from __future__ import annotations

from .gff import (
    inspect_gff,
    load_gene_map,
    parse_attributes,
)
from .ncbi import (
    check_ncbi_tools,
    download_ncbi_package,
    get_assembly_sequence_summary,
    install_ncbi_tools,
    search_ncbi_assemblies,
)
from .overlap import (
    find_overlapping_genes,
    superimpose_genes_on_shanes,
)
