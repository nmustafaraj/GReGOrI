from __future__ import annotations
from collections import Counter

def validate(library):
    errors=[];warnings=[];shanes=library.get('shanes',[])
    for sid,n in Counter(s.get('stable_id') for s in shanes).items():
        if not sid:errors.append('SHaNE without stable_id')
        elif n>1:errors.append(f'duplicate stable_id: {sid}')
    for s in shanes:
        sid=s.get('stable_id','unknown');c=s.get('coordinates') or {};start,end=c.get('start'),c.get('end')
        if not isinstance(start,int) or not isinstance(end,int) or start<0 or end<=start:errors.append(f'{sid}: invalid coordinates');continue
        if s.get('length_bp')!=end-start:errors.append(f'{sid}: length mismatch')
        if len(s.get('islands',[]))!=s.get('island_count'):errors.append(f'{sid}: island count mismatch')
        for x in s.get('islands',[]):
            fs,fe=x['s_start'],x['s_end'];hs,he=x['h_start'],x['h_end']
            if not(start<=fs<fe<=end and start<=hs<he<=end):errors.append(f'{sid}: island outside SHaNE')
        d=s.get('details')
        if not isinstance(d,dict):errors.append(f'{sid}: details object missing')
        else:
            for key in ('context_sequence','folded_alignment','island_alignment'):
                if key not in d:errors.append(f'{sid}: details.{key} missing')
        st=s.get('annotation_status');genes=s.get('genes',[])
        if st=='annotated' and not genes:errors.append(f'{sid}: annotated without genes')
        if st=='no_gene_overlap' and genes:errors.append(f'{sid}: genes present with no_gene_overlap')
        if not s.get('ncbi_region_url'):warnings.append(f'{sid}: NCBI region URL missing')
    return {'ok':not errors,'shane_count':len(shanes),'error_count':len(errors),'warning_count':len(warnings),'errors':errors,'warnings':warnings}
