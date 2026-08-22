from __future__ import annotations
import gzip, urllib.parse
from pathlib import Path

def attrs(text):
    out={}
    for item in text.split(';'):
        if '=' in item:
            k,v=item.split('=',1);out[k]=urllib.parse.unquote(v)
    return out

def load_gff3(path, expected_accessions=None):
    if not path:return {},{'annotation_status':'annotation_unavailable'}
    expected=set(expected_accessions or [])
    opener=gzip.open if str(path).endswith('.gz') else open
    genes={};feature_counts={};seen=set()
    with opener(path,'rt',encoding='utf-8',errors='replace') as fh:
        for line in fh:
            if not line or line.startswith('#'):continue
            c=line.rstrip('\n').split('\t')
            if len(c)!=9:continue
            seen.add(c[0]);feature_counts[c[2]]=feature_counts.get(c[2],0)+1
            if c[2] not in {'gene','pseudogene'}:continue
            a=attrs(c[8]);start,end=int(c[3])-1,int(c[4]);strand=c[6]
            db=[x for x in (a.get('Dbxref') or '').split(',') if x]
            gid=next((x.split(':',1)[1] for x in db if x.startswith('GeneID:')),None)
            item={'feature_id':a.get('ID','.'),'gene_id':gid,'symbol':a.get('gene') or a.get('Name') or '.',
                  'locus_tag':a.get('locus_tag','.'),'biotype':a.get('gene_biotype') or a.get('gene_type') or c[2],
                  'strand':strand,'genomic_start':start,'genomic_end':end,
                  'transcription_start':end-1 if strand=='-' else start,
                  'transcription_end':start if strand=='-' else end-1,
                  'dbxrefs':db}
            if gid:item['ncbi_url']=f'https://www.ncbi.nlm.nih.gov/gene/{gid}'
            genes.setdefault(c[0],[]).append(item)
    missing=sorted(expected-seen) if expected else []
    return genes,{'annotation_status':'validated','feature_counts':feature_counts,'sequence_accessions_seen':len(seen),'unmapped_expected_accessions':missing,'coordinate_system':'GFF3 1-based inclusive -> internal 0-based half-open'}

def annotate(shanes, genes, available):
    for s in shanes:
        overlaps=[]
        for g in genes:
            left=max(s['start'],g['genomic_start']);right=min(s['end'],g['genomic_end'])
            if left>=right:continue
            x=dict(g);x['overlap_start']=left;x['overlap_end']=right;x['overlap_bp']=right-left
            if g['genomic_start']>=s['start'] and g['genomic_end']<=s['end']:rel='gene_contained_in_SHaNE'
            elif s['start']>=g['genomic_start'] and s['end']<=g['genomic_end']:rel='SHaNE_contained_in_gene'
            elif g['genomic_start']<s['start']:rel='partial_left_overlap'
            else:rel='partial_right_overlap'
            x['relationship']=rel;overlaps.append(x)
        s['genes']=overlaps;s['annotation_status']='annotation_unavailable' if not available else ('annotated' if overlaps else 'no_gene_overlap')
    return shanes
