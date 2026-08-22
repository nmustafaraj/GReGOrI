"""Refines Browser v4.1 into Browser v4.2 publishing finish with enhanced toolbars and formatting."""
from __future__ import annotations
import argparse, re, shutil, webbrowser
from pathlib import Path

CSS = r'''
/* Browser v4.2 publishing finish */
:root{--space-1:8px;--space-2:12px;--space-3:16px;--space-4:24px;--separator:#304564;--amber:#f59e0b;--gold:#fbbf24}
main{padding-top:16px}.utility-bar{display:flex;justify-content:space-between;align-items:center;gap:10px;margin:0 0 var(--space-3)}.utility-left,.utility-right{display:flex;align-items:center;gap:8px}.utility-bar button{min-height:36px}
.filter-panel{padding:18px 18px 16px!important}
select{appearance:none;-webkit-appearance:none;background-image:linear-gradient(45deg,transparent 50%,var(--cyan) 50%),linear-gradient(135deg,var(--cyan) 50%,transparent 50%);background-position:calc(100% - 15px) 50%,calc(100% - 10px) 50%;background-size:5px 5px,5px 5px;background-repeat:no-repeat;padding-right:30px}input[type=number]{color-scheme:dark}
.summary{margin:12px 2px 12px}.rings{margin:0 0 var(--space-4)!important;gap:12px!important}.graph-panel{margin:0 0 var(--space-4)!important}.workspace{margin:0 0 var(--space-4)!important}.workspace-actions{margin:0 0 var(--space-2)!important;padding:0}.workspace-layout{gap:12px!important}.workspace-layout>.panel{min-height:290px}.chromosome-heading{padding:8px 0 18px!important}.chromosome-heading h2{margin:0 0 5px}.shane-grid{margin-top:var(--space-3)!important;gap:12px!important}
.modal{padding:7vh 12vw!important;overflow-y:auto;z-index:1000!important}.modal.open{display:block!important}.dialog{height:auto!important;min-height:0;max-height:none!important;max-width:1160px!important;overflow:visible!important;padding:24px 28px!important}.modaltop{position:relative!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;text-align:center!important;width:100%!important;margin:0 auto 16px auto!important;gap:12px!important}.modal-heading{display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;text-align:center!important;gap:8px!important;width:100%!important}.modal-title-row{display:inline-flex!important;align-items:center!important;justify-content:center!important;gap:14px!important;white-space:nowrap!important;margin:0 auto!important}.modal-title-row h2{font-size:24px!important;font-weight:700!important;margin:0!important;white-space:nowrap!important}.modal-cartouche{display:inline-flex!important;align-items:center!important;justify-content:center!important;gap:8px!important;margin:0 auto!important;padding:5px 16px!important;border:1px solid #304b72!important;border-radius:99px!important;background:#0d1933!important;white-space:nowrap!important;font-size:13px!important;color:var(--muted)!important}.modal-cartouche a{color:var(--ink)!important;font-weight:500;text-decoration:none;cursor:pointer;}.modal-illustration{width:100%!important;max-width:920px!important;margin:0 auto!important;display:flex!important;justify-content:center!important}.modal-illustration .structure{width:100%!important;height:120px!important;display:block!important;margin:0 auto!important}.xclose,button.xclose{position:absolute!important;top:0!important;right:0!important;background:transparent!important;border:none!important;outline:none!important;box-shadow:none!important;color:#ffffff!important;font-size:24px!important;line-height:1!important;cursor:pointer!important;padding:2px 8px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;transition:transform .15s!important;z-index:10!important}.xclose:hover,button.xclose:hover{background:transparent!important;border:none!important;box-shadow:none!important;color:#ffffff!important;transform:scale(1.2)!important}.panorama{margin:2px 0 14px!important}.tabs{justify-content:center;margin:12px 0 16px!important}
.methods-modal{z-index:1001!important;overflow-y:auto!important;padding:6vh 8vw!important}.methods-modal .dialog{position:relative;max-width:1040px!important;width:100%!important;height:auto!important;min-height:0!important;max-height:none!important;overflow:visible!important;padding:24px 30px 36px!important;box-sizing:border-box!important;margin:0 auto!important}.methods-modal .modaltop{display:flex!important;justify-content:space-between!important;align-items:center!important;width:100%!important;margin-bottom:18px!important}
.methods-modal .modaltop{display:flex!important;justify-content:space-between!important;align-items:center!important;width:100%!important;margin-bottom:14px!important}
.detail-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:0 0 14px}.flank-tools{display:inline-flex;align-items:center;gap:8px;flex-wrap:wrap}.flank-tools label{display:inline-flex;align-items:center;gap:8px;color:var(--muted);font-size:13px;margin:0}.flank-tools input{width:100px;height:38px!important;min-height:38px!important;padding:0 10px;font-size:13px;box-sizing:border-box;border-radius:8px}.flank-tools button,.copybar .copybtn,.fold-guide-card .copybtn{height:38px!important;min-height:38px!important;padding:0 16px!important;font-size:13px!important;box-sizing:border-box!important;border-radius:8px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;line-height:1!important}.detail-note{color:var(--muted);font-size:11px}.copybar{margin:0!important}.seqbox,.alignbox{overflow-x:auto!important;overflow-y:visible!important;max-height:none!important}.seqbox{padding:20px 18px!important;background:#09142a!important;display:flex!important;flex-direction:column!important;align-items:center!important;overflow-x:auto!important}.base-at{color:#00f0ff!important}.base-gc{color:#ff2df1!important}.context-grid{display:grid;grid-template-columns:26px 104px max-content 104px 26px;column-gap:12px;align-items:baseline;width:max-content;margin:0 auto!important}.context-grid .seqrow{display:contents}.ctx-orient{color:#8396b5!important;text-align:center}.ctx-left{text-align:right}.ctx-right{text-align:left}.ctx-seq{letter-spacing:.03em;line-height:1.95;white-space:pre}.context-grid>*{padding-block:2px}.islands-view-wrapper,.folded-view-wrapper,.branches-view-wrapper{max-width:980px;margin:0 auto;display:flex;flex-direction:column;gap:14px}.island-card-window{background:#091329!important;border:1px solid #233b66!important;border-radius:12px!important;padding:16px 20px!important;box-shadow:0 4px 18px rgba(0,0,0,0.3)!important;text-align:left;height:auto!important;max-height:none!important;overflow:visible!important}.alignbox{display:flex!important;flex-direction:column!important;align-items:center!important;padding:18px!important;background:#030715!important;border:1px solid #1f3354!important;border-radius:12px!important;text-align:center;font-family:Consolas,monospace;height:auto!important;max-height:none!important;overflow-y:visible!important;overflow-x:auto!important}.fold-block{display:block!important;text-align:left;line-height:1.55;margin:0 auto 1.55em!important;width:max-content;clear:both!important;font-family:Consolas,monospace}.fold-block:last-child{margin-bottom:0!important}.fold-line{white-space:pre!important;min-height:1.55em;font-family:Consolas,monospace!important;font-size:13px!important;letter-spacing:0px!important;text-align:left!important;line-height:1.55!important;margin:0!important;padding:0!important}.fold-line.pair{color:#ffffff!important;line-height:1.55!important;margin:0!important;padding:0!important}.island-card-window .alignbox{font-variant-ligatures:none}
.metric .help{width:260px!important;line-height:1.45}.gene-card{text-align:left;align-content:start}.gene-card>div,.gene-card>p{line-height:1.45}
@media(max-width:1100px){.modal{padding:4vh 6vw!important}.dialog{max-width:none!important}}
@media(max-width:720px){.utility-bar{align-items:flex-start}.modal{padding:2vh 3vw!important}.context-grid{grid-template-columns:24px 88px max-content 88px 24px;column-gap:8px}.modal-heading{padding-inline:38px}}
'''

JS = r'''
/* Browser v4.2 publishing finish */
let requestedFlankBp=500;
function installV42(){
  let main=document.querySelector('main'),filters=document.querySelector('.filter-panel');
  if(main&&!document.querySelector('.utility-bar')){
    let bar=document.createElement('div');bar.className='utility-bar';bar.innerHTML=`<div class="utility-left"><button id="homeV42">Home</button><button id="resetV42">Reset</button><button id="bookmarkV42">Bookmark</button></div><div class="utility-right"></div>`;main.insertBefore(bar,filters);homeV42.onclick=()=>{pointFilter=null;activeStat=null;if(selectedGroup)closeChrom();else scrollTo({top:0,behavior:'smooth'});apply()};resetV42.onclick=()=>resetFilters();bookmarkV42.onclick=()=>bookmark();
    [...document.querySelectorAll('.filter-actions button')].forEach(b=>{if(/Reset|Bookmark/.test(b.textContent))b.dataset.moved='1'})
  }
}
const openSHaNEV41=openSHaNE;
openSHaNE=function(s){openSHaNEV41(s);requestedFlankBp=Math.min(500,availableFlank(s).max);enhanceMetricText();if(typeof updateModalNav==='function')updateModalNav(s);}
function availableFlank(s){let seq=s.details?.context_sequence||'',first=seq.search(/[A-Z]/),last=Math.max(-1,...[...seq].map((c,i)=>/[A-Z]/.test(c)?i:-1));if(first<0)return{left:0,right:0,max:0,first:0,last:seq.length-1};return{left:first,right:seq.length-last-1,max:Math.min(10000,first,seq.length-last-1),first,last}}
function enhanceMetricText(){let helps=[...document.querySelectorAll('.metric .help')];let texts=[
'Genomic span from the first nucleotide assigned to the SHaNE through its final nucleotide: End - Start (bp).',
'Full alignment span including dynamically inserted void gap characters (.): Genomic length + Total voids (bp).',
'Maximized Watson-Crick complementarity score calculated as the ratio of canonical base pairs (A-T, G-C) to total duplex length across opposing arms.',
'Secondary structure classification determined by the count, location, and arrangement of internal hairpin stems.',
'Number of complementary island stem pairs reported between the opposed SHaNE arms under canonical detection settings.',
'Number of internal self-complementary stem-loop hairpin branches formed within interisland loops or individual arms.',
'Sum of the reported 5′ island-arm lengths. Each complementary island pair is counted once.',
'Percentage of canonical sequenced nucleotides (Guanine + Cytosine) across the complete SHaNE interval: (G + C) / (A + C + G + T) × 100%, excluding unsequenced/dead Ns.'
];helps.forEach((x,i)=>{if(texts[i])x.textContent=texts[i]})}
contextHTML=function(s,seq){let a=availableFlank(s),flank=Math.max(0,Math.min(10000,requestedFlankBp,a.left,a.right)),from=a.first-flank,to=a.last+flank+1,shown=seq.slice(from,to),genomicStart=s.start-flank,w=60,rows=[];for(let i=0;i<shown.length;i+=w){let part=shown.slice(i,i+w),left=genomicStart+i,right=left+part.length-1,parts=[...part].map((c,j)=>{let original=from+i+j,cl=original>=a.first&&original<=a.last?'shseq':'flank';if(/[Nn]/.test(c))return `<span class="${cl} base-n">${esc(c)}</span>`;return `<span class="${cl}">${esc(c)}</span>`}).join('');rows.push(`<div class="seqrow"><span class="ctx-orient">5′</span><span class="coord ctx-left">${fmt(left)}</span><span class="ctx-seq">${parts}</span><span class="coord ctx-right">${fmt(right)}</span><span class="ctx-orient">3′</span></div>`)}let limit=Math.min(10000,a.left,a.right);return `<div class="detail-toolbar"><div class="flank-tools"><label>Flank per side (bp)<input id="flankBp" type="number" min="0" max="${limit}" step="50" value="${flank}"></label><button onclick="applyFlank()">Apply</button><span class="detail-note">Available in this library: ${fmt(limit)} bp per flank; interface limit: 10,000 bp.</span></div><div class="copybar"><button class="copybtn" onclick="copyCleanSequence()">Copy clean sequence</button></div></div><div class="meta" style="margin-bottom:6px;">Lowercase: flanks • uppercase: SHaNE • 60 bases per row</div><div class="seqbox"><div class="context-grid">${rows.join('')}</div></div>`}
function applyFlank(){let s=L.shanes.find(x=>x.stable_id===modal.dataset.sid),a=availableFlank(s),v=Number(document.getElementById('flankBp')?.value||0);requestedFlankBp=Math.max(0,Math.min(10000,a.left,a.right,v));tabBody.innerHTML=contextHTML(s,s.details.context_sequence)}
copyCleanSequence=function(){let s=L.shanes.find(x=>x.stable_id===modal.dataset.sid),seq=s.details?.context_sequence||'',a=availableFlank(s),f=Math.max(0,Math.min(requestedFlankBp,a.left,a.right)),clean=seq.slice(a.first-f,a.last+f+1).replace(/[^A-Za-z]/g,'');navigator.clipboard.writeText(clean).then(()=>{let b=document.querySelector('.copybtn');if(b){b.textContent='Copied';setTimeout(()=>b.textContent='Copy clean sequence',1200)}})}
function colorChars(line){return [...line].map(c=>{let cl=/[Nn]/.test(c)?'base-n':/[ATat]/.test(c)?'base-at':/[GCgc]/.test(c)?'base-gc':c==='.'?'gap':'';if(c==='|')return '<span style="color:#ffffff;font-weight:700;">|</span>';if(c==='.')return '<span class="gap" style="color:#6b7280;">.</span>';return `<span${cl?` class="${cl}"`:classes(c)}>${esc(c)}</span>`}).join('')}
function classes(c){return ''}
colorAlignment=function(t){if(!t)return '<div class="no-data">No alignment data.</div>';let lines=t.split('\n'),out=[];for(let i=0;i<lines.length;){if(i+2<lines.length&&/5['′]-3['′]/.test(lines[i])&&/3['′]-5['′]/.test(lines[i+2])){let l1=lines[i],l2=lines[i+1],l3=lines[i+2],m=Math.max(l1.length,l2.length,l3.length);let pairContent=l2.includes('|')?colorChars(l2.padEnd(m,' ')):'<span style="visibility:hidden;font-weight:700;">|</span>';out.push(`<div class="fold-block" style="display:block;width:max-content;margin:0 auto 1.55em;clear:both;"><div class="fold-line" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;">${colorChars(l1.padEnd(m,' '))}</div><div class="fold-line pair" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;color:#ffffff;">${pairContent}</div><div class="fold-line" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;">${colorChars(l3.padEnd(m,' '))}</div></div>`);i+=3}else{if(lines[i].trim())out.push(`<div class="fold-line" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;">${colorChars(lines[i])}</div>`);i++}}return out.join('')}
installV42();
'''

def refine(source: str | Path, open_after: bool = False) -> Path:
    p = Path(source).expanduser().resolve()
    root = p if p.is_dir() else p.parent
    v41_page = root / "browser_v4_1" / "index.html"
    if not v41_page.exists():
        raise FileNotFoundError(f"Base Browser v4.1 not found: {v41_page}")

    html = v41_page.read_text(encoding="utf-8")
    html = html.replace("</style>", CSS + "</style>", 1)
    html = html.replace("</script>", JS + "</script>", 1)

    out = root / "browser_v4_2"
    out.mkdir(exist_ok=True)
    page = out / "index.html"
    page.write_text(html, encoding="utf-8")
    if (root / "browser_v4/data").is_dir():
        shutil.copytree(root / "browser_v4/data", out / "data", dirs_exist_ok=True)
    (out / "README.md").write_text("# GReGOrI Finished Browser v4.2\n\nProduction release with polished interface tools, standard font kerning, balanced layout, and non-destructive extensions.\n", encoding="utf-8")
    print(f"Source: {source}\nCreated: {page}")
    if open_after:
        webbrowser.open(page.as_uri())
    return page

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("assembly", nargs="?")
    p.add_argument("--open", action="store_true")
    a = p.parse_args()
    refine(a.assembly or input("Assembly repository: ").strip().strip('"'), a.open)

if __name__ == "__main__":
    main()
