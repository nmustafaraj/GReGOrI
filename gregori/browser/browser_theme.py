from __future__ import annotations
from pathlib import Path
CSS=r'''/* GReGOrI modular theme 0.9.3 */
:root{--ring-all:#ff70ea;--ring-size:#ffffff;--ring-score:#00f0ff;--ring-islands:#ffee33;--ring-genes:#00ff88;--ring-gc:#8ba2c2}.ring-card{background:#0c152b!important}.ring-card.active{border-color:#25d9f4!important;box-shadow:0 0 14px #25d9f433!important}.arc{filter:saturate(.85) brightness(.92)}.ring-caption{color:#8193b1!important}.records{height:auto!important;max-height:300px}.record.sub{border-left:2px solid #304664;margin-left:14px!important;padding-left:12px}.record-main{font-weight:650}.record-count{color:#8fa5c8}.record-group-label{color:#28d4ed;font-size:11px;text-transform:uppercase;letter-spacing:.07em;margin:10px 4px 4px}
'''
JS=r'''/* GReGOrI modular browser behavior 0.9.3 */
Object.assign(C,{all:'#ff70ea',size:'#ffffff',score:'#00f0ff',islands:'#ffee33',genes:'#00ff88',gc:'#8ba2c2'});
'''
def apply(page):
 p=Path(page);text=p.read_text(encoding='utf-8')
 if 'GReGOrI modular theme 0.9.3' in text:return p
 text=text.replace('</style>',CSS+'</style>',1).replace('</script></body>',JS+'</script></body>',1)
 p.write_text(text,encoding='utf-8');return p
