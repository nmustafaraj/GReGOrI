from __future__ import annotations
import json
from pathlib import Path
from .regression import compare

def run(project_path):
 root=Path(project_path);candidates={
  'tsv':next(iter(root.rglob('candidates.tsv')),None),
  'bed':next(iter(root.rglob('candidates.bed')),None),
  'gff':next(iter(root.rglob('*SHaNEs.gff3')),None),
  'json_path':next(iter(root.rglob('chromosome_result.json')),None)}
 usable={k:str(v) for k,v in candidates.items() if v}
 report=compare(**usable) if len(usable)>=2 else {'ok':True,'status':'insufficient_existing_artifacts_for_cross_comparison','artifacts':usable}
 out=root/'science_validation.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8');return report
