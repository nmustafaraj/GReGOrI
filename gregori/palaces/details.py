from __future__ import annotations
import re

def parse_fasta(path):
    out=[];header=None;seq=[]
    with open(path,encoding='utf-8',errors='replace') as fh:
        for raw in fh:
            line=raw.strip()
            if not line:continue
            if line.startswith('>'):
                if header is not None:out.append((header,''.join(seq)))
                header=line[1:];seq=[]
            else:seq.append(line)
    if header is not None:out.append((header,''.join(seq)))
    return out

def coordinates(header):
    nums=[int(x.replace(',','')) for x in re.findall(r'(?<![A-Za-z])\d[\d,]*',header)]
    return (nums[-2],nums[-1]) if len(nums)>=2 else None

def match_fasta(records, accession, start, end, name=None):
    exact=[];by_name=[]
    for h,s in records:
        c=coordinates(h)
        if accession in h and c and c==(start,end):exact.append(s)
        elif name and h.split()[0]==name:by_name.append(s)
    if len(exact)==1:return exact[0],'accession_coordinates'
    if len(by_name)==1:return by_name[0],'unique_name_fallback'
    return '', 'ambiguous_or_missing'

def alignment_blocks(text):
    pattern=re.compile(r'(?m)^(?:---\s*)?((?:[A-Za-z]{1,3}_)?SHaNE_[A-Za-z0-9_.-]+).*?$')
    matches=list(pattern.finditer(text));out=[]
    for i,m in enumerate(matches):out.append((m.group(1),text[m.start():matches[i+1].start() if i+1<len(matches) else len(text)].strip()))
    return out
