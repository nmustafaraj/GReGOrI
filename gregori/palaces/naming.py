from __future__ import annotations
import hashlib,re

def species_initials(species):
    words=re.findall(r'[A-Za-z]+',species or '')
    if len(words)>=2:return words[0][0].upper()+words[1][0].lower()
    return ''.join(words)[:2].capitalize() or 'Un'

def legacy_name(species, display_name, start):
    clean_chrom = re.sub(r'^(?:chromosome|linkage\s+group)\s*', '', str(display_name or 'un'), flags=re.I).strip()
    clean_chrom = clean_chrom.replace(' ', '_') or 'un'
    return f'{species_initials(species)}_SHaNE_{clean_chrom}.{int(start)//100000}'

def stable_id(assembly,accession,start,end):
    return f'{assembly}|{accession}|{int(start)}|{int(end)}'

def barcode(assembly,accession,start,end):
    value=stable_id(assembly,accession,start,end).encode('utf-8')
    return 'SHN-'+hashlib.sha1(value).hexdigest()[:10]
