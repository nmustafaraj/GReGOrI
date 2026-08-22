"""Native file and directory selection dialogs with Tkinter."""
from __future__ import annotations


def pick_paths(kind: str = "files") -> list[str]:
    """Open native file or directory selection dialog and return selected absolute paths."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return []

    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        if kind == "folder":
            val = [filedialog.askdirectory(title="Select FASTA Folder")]
        elif kind == "gene_map":
            val = list(filedialog.askopenfilenames(
                title="Select Gene Map / GFF3 File",
                filetypes=[("Gene Annotations", "*.gff *.gff3 *.gtf *.gff.gz *.gff3.gz *.gtf.gz"), ("All Files", "*.*")],
            ))
        else:
            val = list(filedialog.askopenfilenames(
                title="Select FASTA Files",
                filetypes=[("FASTA", "*.fa *.fasta *.fna *.fas *.fa.gz *.fasta.gz *.fna.gz"), ("All Files", "*.*")],
            ))
        root.destroy()
        return [str(x) for x in val if x]
    except Exception:
        return []
