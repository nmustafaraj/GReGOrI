from __future__ import annotations
import csv,json,re
from pathlib import Path

def tsv_candidates(path):
 out={}
 with open(path,encoding='utf-8',errors='replace') as fh:
  rows=csv.DictReader(fh,delimiter='\t')
  for r in rows:
   try:start=int(r.get('Start') or r.get('start'));end=int(r.get('End') or r.get('end'))
   except Exception:continue
   key=(r.get('Sequence_ID') or r.get('Sequence') or r.get('Chromosome') or r.get('chromosome'),start,end);out[key]=r
 return out
def bed_candidates(path):
 out={}
 with open(path,encoding='utf-8',errors='replace') as fh:
  for line in fh:
   if not line.strip() or line.startswith(('#','track','browser')):continue
   c=line.rstrip().split('\t')
   if len(c)>=3:out[(c[0],int(c[1]),int(c[2]))]=c
 return out
def gff_candidates(path):
 out={};islands={}
 with open(path,encoding='utf-8',errors='replace') as fh:
  for line in fh:
   if not line.strip() or line.startswith('#'):continue
   c=line.rstrip().split('\t')
   if len(c)!=9:continue
   attrs=dict(x.split('=',1) for x in c[8].split(';') if '=' in x)
   if c[2]=='biological_region':out[(c[0],int(c[3])-1,int(c[4]))]=attrs
   elif c[2]=='inverted_repeat':islands.setdefault(attrs.get('Parent',''),[]).append((c[0],int(c[3])-1,int(c[4]),c[6],attrs.get('Arm')))
 return out,islands
def json_candidates(path):
 data=json.loads(Path(path).read_text(encoding='utf-8'));items=data.get('shanes') or data.get('candidates') or []
 seq=data.get('sequence_id') or data.get('sequence_accession')
 return {(x.get('sequence_accession') or seq,x['start'] if 'start' in x else x['coordinates']['start'],x['end'] if 'end' in x else x['coordinates']['end']):x for x in items}
def compare(tsv=None,bed=None,gff=None,json_path=None):
 sets={}
 if tsv:sets['tsv']=set(tsv_candidates(tsv))
 if bed:sets['bed']=set(bed_candidates(bed))
 if gff:sets['gff']=set(gff_candidates(gff)[0])
 if json_path:sets['json']=set(json_candidates(json_path))
 union=set().union(*sets.values()) if sets else set();intersection=set.intersection(*sets.values()) if sets else set();missing={name:sorted(union-values) for name,values in sets.items()}
 return {'ok':all(not x for x in missing.values()),'artifact_counts':{k:len(v) for k,v in sets.items()},'shared_count':len(intersection),'union_count':len(union),'missing_by_artifact':missing}
