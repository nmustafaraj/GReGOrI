from __future__ import annotations
import csv, json, re
from pathlib import Path

def _first(row, *names):
    low = {str(k).lower().replace(' ', '_').replace('-', '_'): v for k, v in row.items()}
    for name in names:
        v = low.get(name.lower().replace(' ', '_').replace('-', '_'))
        if v not in (None, '', 'na', 'NA'): return str(v)
    return ''

def _classify(row):
    role = _first(row, 'sequence_role', 'role').lower()
    molecule = _first(row, 'chr_name', 'chromosome_name', 'assigned_molecule', 'assigned_molecule_location/type', 'assigned_molecule_location_type', 'chromosome')
    name = _first(row, 'ucsc_style_name', 'sequence_name', 'name')
    acc = _first(row, 'refseq_accession', 'genbank_accession', 'accession')
    text = ' '.join(map(str, row.values())).lower()

    if 'mitochond' in text or 'mtdna' in text:
        return 'Mitochondrion', 'MT'
    if 'chloroplast' in text or 'plastid' in text:
        return 'Chloroplast', 'Pt'

    is_unloc = 'unlocalized' in role or 'unlocalized' in text
    is_unplaced = 'unplaced' in role or 'unplaced' in text

    # 1. Assigned molecule / chromosome (e.g. 1, 19, LG1, X, Chr1)
    if molecule and molecule.lower() not in {'na', 'unplaced-scaffold', 'none', 'unplaced', 'un', ''}:
        group = re.sub(r'^(?:chromosome|linkage\s+group)\s*', '', molecule, flags=re.I).strip()
        display = group if (role in {'assembled-molecule', 'chromosome'} and not is_unloc and not is_unplaced) else (name or acc)
        return group, display

    # 2. Linkage groups (e.g. LG1, LG2)
    m_lg = re.search(r'\blinkage\s+group\s*[:=_-]?\s*([A-Za-z0-9_]+)\b', text, re.I)
    if m_lg:
        lg = m_lg.group(1).rstrip('.:')
        display = lg if (role in {'assembled-molecule', 'chromosome'} and not is_unloc and not is_unplaced) else (name or acc)
        return lg, display

    # 3. Chromosome pattern in text
    m_chr = re.search(r'\b(?:chromosome|chrom|chr)\s*[:=_-]?\s*([A-Za-z0-9_]+)\b', text, re.I)
    if m_chr:
        val = m_chr.group(1).rstrip('.:')
        if val.lower() not in {'sequence', 'shotgun', 'primary', 'scaffold', 'unplaced', 'contig', 'na', 'none'}:
            display = val if (role in {'assembled-molecule', 'chromosome'} and not is_unloc and not is_unplaced) else (name or acc)
            return val, display

    if is_unplaced or 'scaffold' in text or 'contig' in text:
        return 'Unplaced', name or acc

    return 'Other', name or acc

def _rows(path):
    path = Path(path)
    text = path.read_text(encoding='utf-8', errors='replace')
    if path.suffix.lower() in {'.jsonl', '.json'} or text.lstrip().startswith(('{', '[')):
        data = json.loads(text) if text.lstrip().startswith('[') else [json.loads(x) for x in text.splitlines() if x.strip()]
        if isinstance(data, dict):
            data = data.get('reports') or data.get('sequences') or [data]
        return data
    sample = text[:4096]
    delimiter = '\t' if sample.count('\t') >= sample.count(',') else ','
    return list(csv.DictReader(text.splitlines(), delimiter=delimiter))

def load(path):
    result = {}
    for row in _rows(path):
        acc = _first(row, 'refseq_accession', 'accession', 'genbank_accession', 'refseq_accn', 'genbank_accn', 'sequence_name')
        if not acc:
            continue
        group, display = _classify(row)
        role = _first(row, 'sequence_role', 'role')
        is_chrom = group not in {'Unplaced', 'Other', 'Mitochondrion', 'Chloroplast'}
        rec = {
            'sequence_accession': acc,
            'chromosome_group': group,
            'display_name': display,
            'sequence_role': role,
            'is_chromosome': is_chrom,
            'length_bp': int(_first(row, 'length', 'length_bp') or 0),
            'assigned_molecule': _first(row, 'assigned_molecule', 'chromosome'),
        }
        for alias in [acc, _first(row, 'refseq_accn', 'refseq_accession'), _first(row, 'genbank_accn', 'genbank_accession'), _first(row, 'sequence_name', 'name'), _first(row, 'ucsc_style_name')]:
            if alias and alias not in {'na', 'NA', 'none', ''}:
                result[alias] = rec
    return result

def fallback(header, accession):
    text = header or ''
    low = text.lower()
    acc = accession or text.split()[0]

    # 1. Mitochondrion
    if 'mitochond' in low or 'mtdna' in low:
        return {'chromosome_group': 'Mitochondrion', 'display_name': 'MT', 'sequence_accession': acc, 'is_chromosome': True, 'hierarchy_source': 'header_fallback'}

    # 2. Chloroplast / Plastid
    if 'chloroplast' in low or 'plastid' in low:
        return {'chromosome_group': 'Chloroplast', 'display_name': 'Pt', 'sequence_accession': acc, 'is_chromosome': True, 'hierarchy_source': 'header_fallback'}

    is_unlocalized = 'unlocalized' in low
    is_unplaced = 'unplaced' in low

    # 3. Associated Linkage Group / Group (e.g. associated_to_Group10, associated_to_LG10)
    m_assoc = re.search(r'\bassociated[_\s-]+to[_\s-]+(?:group|lg)?\s*([A-Za-z0-9_]+)\b', text, re.I)
    if m_assoc:
        grp = m_assoc.group(1).rstrip('.:')
        lg = f"LG{grp}" if grp.isdigit() else grp
        return {'chromosome_group': lg, 'display_name': acc, 'sequence_accession': acc, 'is_chromosome': True, 'hierarchy_source': 'header_fallback'}

    # 4. Linkage Group (e.g. linkage group LG1, LG2)
    m_lg = re.search(r'\blinkage\s+group\s*[:=_-]?\s*([A-Za-z0-9_]+)\b', text, re.I)
    if m_lg:
        lg = m_lg.group(1).rstrip('.:')
        display = lg if not is_unlocalized and not is_unplaced and not acc.startswith(('NW_', 'NT_')) else acc
        return {'chromosome_group': lg, 'display_name': display, 'sequence_accession': acc, 'is_chromosome': True, 'hierarchy_source': 'header_fallback'}

    # 5. Chromosome (e.g. chromosome 1, chr 1, ChrX, chromosome 2L)
    m_chr = re.search(r'\b(?:chromosome|chrom|chr)\s*[:=_-]?\s*([A-Za-z0-9_]+)\b', text, re.I)
    if m_chr:
        val = m_chr.group(1).rstrip('.:')
        if val.lower() not in {'sequence', 'shotgun', 'primary', 'scaffold', 'unplaced', 'contig', 'na', 'none'}:
            display = val if not is_unlocalized and not is_unplaced and not acc.startswith(('NW_', 'NT_')) else acc
            return {'chromosome_group': val, 'display_name': display, 'sequence_accession': acc, 'is_chromosome': True, 'hierarchy_source': 'header_fallback'}

    if is_unplaced or 'scaffold' in low or 'contig' in low:
        return {'chromosome_group': 'Unplaced', 'display_name': acc, 'sequence_accession': acc, 'is_chromosome': False, 'hierarchy_source': 'header_fallback'}

    return {'chromosome_group': acc, 'display_name': acc, 'sequence_accession': acc, 'is_chromosome': False, 'hierarchy_source': 'header_fallback'}

