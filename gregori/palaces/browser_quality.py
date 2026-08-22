from __future__ import annotations
from pathlib import Path
CSS=r'''/* Palaces Browser quality maintenance 0.3.1 */
.atlas-safe{overflow:auto}.atlas-safe svg{display:block;max-width:100%;height:auto;margin:0 auto}.seqbox{text-align:center}.seqbox .context-grid{margin-inline:auto}.alignbox{text-align:center}.island-block .alignbox{text-align:left}.structure{display:block;margin-inline:auto;max-width:100%}.workspace-layout>.panel{min-width:0}.gene-card,.metric{text-align:center}.records{isolation:isolate}
'''
JS=r'''/* Palaces Browser quality maintenance 0.3.1 */
(function(){
 const oldAtlas=window.atlasSVG;
 if(typeof oldAtlas==='function')window.atlasSVG=function(arr,title){return oldAtlas(arr,title).replace('<svg ','<svg preserveAspectRatio="xMidYMid meet" ')};
 const oldContext=window.contextHTML;
 if(typeof oldContext==='function')window.contextHTML=function(s,seq){return oldContext(s,seq).replace('class="seqbox"','class="seqbox centrally-aligned"')};
})();
'''
def apply(page):
    p=Path(page);text=p.read_text(encoding='utf-8')
    if 'Palaces Browser quality maintenance 0.3.1' in text:return p
    text=text.replace('</style>',CSS+'</style>',1).replace('</script></body>',JS+'</script></body>',1)
    p.write_text(text,encoding='utf-8');return p
