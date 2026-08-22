"""Standalone single-file HTML5 GReGOrI SHaNE Browser v4 builder."""
from __future__ import annotations
import argparse, base64, json, mimetypes
from pathlib import Path
try:
    from .methods_content import get_methods_html
except (ImportError, ValueError):
    try:
        from methods_content import get_methods_html
    except (ImportError, ValueError):
        from gregori.browser.methods_content import get_methods_html

HTML = r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GReGOrI (Genomic Repeat Grouping & Orientation Identifier) • Browser</title><style>
:root {
  --bg: #060a14;
  --bg-grad: radial-gradient(circle at 85% 0%, #0d2542 0%, #07152b 45%, #040914 100%);
  --panel: #0b162a;
  --panel2: #0f1e38;
  --panel-border: #1d365a;
  --header-bg: #071224eb;
  --header-border: #213d66;
  --btn-bg: #10223e;
  --btn-border: #2b4f80;
  --ink: #eef8ff;
  --muted: #8ba2c2;
  --magenta: #ff2df1;
  --pink: #ff2df1;
  --creme: #ffffff;
  --cyan: #00f0ff;
  --yellow: #ffee33;
  --green: #00ff88;
  --purple: #c44dff;
  --gray: #859bb8;
  --line: #1d3558;
  --accent: #00f0ff;
  --accent-glow: rgba(0,240,255,0.35);
  --modal-bg: #091428;
  --modal-border: #2a4c7c;
  --seq-bg: #040915;
}

*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg-grad) fixed;color:var(--ink);font:14px Segoe UI,system-ui}button,input,select{font:inherit;color:var(--ink);background:var(--btn-bg);border:1px solid var(--btn-border);border-radius:8px;padding:6px 9px;transition:border-color .15s,box-shadow .15s}button{cursor:pointer}button:hover:not(:disabled){border-color:var(--accent);box-shadow:0 0 12px var(--accent-glow)}button:disabled{opacity:.35;cursor:not-allowed;pointer-events:auto}a{color:var(--cyan)}header{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:14px;padding:10px 20px;background:var(--header-bg);border-bottom:1px solid var(--header-border);backdrop-filter:blur(12px)}.brand-block{display:flex;align-items:center}.logo{height:46px;max-width:220px;object-fit:contain}header h1{margin:0;font-size:18px}.meta{color:var(--muted)}.actions{margin-left:auto;display:flex;gap:7px;flex-wrap:wrap}main{max-width:1560px;margin:auto;padding:16px}.panel,.card{background:var(--panel);border:1px solid var(--panel-border);border-radius:14px;padding:14px}
.xclose,button.xclose{position:absolute!important;top:0!important;right:0!important;background:transparent!important;border:none!important;outline:none!important;box-shadow:none!important;color:#ffffff!important;font-size:24px!important;line-height:1!important;cursor:pointer!important;padding:2px 8px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;transition:transform .15s!important;z-index:10!important}.xclose:hover,button.xclose:hover{background:transparent!important;border:none!important;box-shadow:none!important;color:#ffffff!important;transform:scale(1.2)!important}.xclose:before,.xclose:after{display:none!important}
.filter-panel{padding:14px 18px}
.filter-panel-grid{display:grid;grid-template-columns:1fr auto;gap:10px 18px;align-items:end}
.search-box-wrap{grid-column:1;grid-row:1;display:flex;flex-direction:column;gap:5px}
.search-box-wrap input{width:100%;box-sizing:border-box}
.param-filters{grid-column:2;grid-row:1;display:flex;align-items:flex-end;gap:18px}
.filter-divider{grid-column:1/-1;grid-row:2;height:1px;background:var(--line);margin:0}
.filter-actions-col{grid-column:1;grid-row:3;display:flex;align-items:center;justify-content:space-between;gap:8px;width:100%;box-sizing:border-box;margin:0;padding:0}
.filter-actions-col > button{flex:1 1 0;min-width:0;display:inline-flex;align-items:center;justify-content:center;white-space:nowrap;padding:6px 6px;font-size:12.5px;box-sizing:border-box;text-align:center}
.filter-group{display:flex;flex-direction:column;gap:5px;flex:0 0 auto}
.filter-group-title{font-size:11px;font-weight:700;color:#ffffff;text-transform:uppercase;letter-spacing:.08em}
.filter-inputs input{width:74px;padding:6px 18px 6px 4px;text-align:center}
input[type=number]{-webkit-appearance:none!important;-moz-appearance:textfield!important;appearance:none!important;background-color:#091428!important;color:#ffffff!important;border:1px solid #28446e!important;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='8' height='12' viewBox='0 0 8 12' fill='none'%3E%3Cpath d='M4 1L1.5 4.5H6.5L4 1Z' fill='%2325d9f4'/%3E%3Cpath d='M4 11L1.5 7.5H6.5L4 11Z' fill='%2325d9f4'/%3E%3C/svg%3E")!important;background-repeat:no-repeat!important;background-position:right 5px center!important;padding-right:18px!important;box-sizing:border-box!important}
input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button{-webkit-appearance:none!important;margin:0!important}
.range-sep{color:var(--muted);font-size:13px;font-weight:600;user-select:none}
.toggle.active{border-color:var(--accent);box-shadow:0 0 12px var(--accent-glow);background:#132d52}
.sort-btn{display:inline-flex;align-items:center;gap:4px;cursor:pointer;background:var(--btn-bg);border:1px solid var(--btn-border);border-radius:8px;padding:6px 8px;color:var(--ink);font-size:12.5px;transition:border-color .15s,box-shadow .15s}.sort-btn:hover{border-color:var(--accent);box-shadow:0 0 12px var(--accent-glow)}
.summary{margin:10px 2px;color:var(--muted);font-weight:500}
.rings{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:12px 0}
.ring-card{text-align:center;cursor:pointer;transition:border-color .2s,box-shadow .2s,transform .2s;position:relative;padding:14px 10px;user-select:none;background:var(--panel);border:1px solid var(--panel-border);-webkit-tap-highlight-color:transparent}
.ring-card:hover{transform:translateY(-2px)}
.ring-card:active{filter:none;-webkit-filter:none;transform:none;background:var(--panel)}
.ring-card.disabled{opacity:.35!important;cursor:not-allowed!important;pointer-events:none}
.ring{width:100%;height:130px}.arc{transition:stroke-dasharray .65s cubic-bezier(.2,.8,.2,1)}
.ring-label{font-size:13px;font-weight:600;color:var(--ink);margin-top:4px}
.ring-caption{font-size:11px;color:var(--muted);margin-top:2px}
.graph-panel{display:none;margin:16px 0 18px;background:var(--panel);border:1px solid var(--panel-border)}.graph-panel.open{display:block;animation:reveal .3s ease}.graph-head{text-align:center}.graph-wrap{max-width:940px;margin:auto}.chart{width:100%;height:260px;overflow:visible}.gridline{stroke:#1d3860;opacity:.4}.axis{stroke:#254773}.axistext{fill:#8ba2c2;font-size:10px}.point{cursor:pointer;transition:r .15s}.point:hover{r:6}.graph-stats{display:flex;justify-content:center;gap:24px;flex-wrap:wrap;text-align:center}.graph-stats b{display:block;font-size:16px}.tip{position:fixed;display:none;z-index:500;background:#050817ee;border:1px solid #294773;border-radius:7px;padding:6px 9px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(315px,1fr));gap:12px}.chrom{cursor:pointer}.chrom.selected{border-color:var(--accent);box-shadow:0 0 18px var(--accent-glow)}.head{display:flex;justify-content:space-between;align-items:center;gap:8px}.badge,.chip{display:inline-block;border-radius:99px;padding:2px 8px;background:transparent;border:1px solid #f5b942;color:#f5b942;font-weight:500;font-size:11px}
.mini{width:100%;height:70px}.track{stroke:var(--gray);stroke-linecap:round}.hit{stroke:var(--magenta);stroke-width:3}.workspace{display:none;margin:16px 0}.workspace.open{display:block;animation:reveal .35s ease}.workspace-layout{display:grid;grid-template-columns:1fr 300px;gap:12px}.workspace h2{margin:.1em 0}.workspace-btn{height:36px;min-height:36px;padding:0 14px;font-size:13px;display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box;line-height:1}.maintrack{width:100%;height:170px}.records{height:235px;overflow:auto;margin-top:9px;padding-right:4px;scrollbar-color:#315c7a var(--bg);scrollbar-width:thin}.records::-webkit-scrollbar{width:9px}.records::-webkit-scrollbar-track{background:var(--bg);border-radius:8px}.records::-webkit-scrollbar-thumb{background:linear-gradient(var(--cyan),#315c7a);border-radius:8px}.record{display:flex;width:100%;justify-content:space-between;margin:4px 0;text-align:left}.record.sub{margin-left:12px;width:calc(100% - 12px);font-size:12px}.record.active{border-color:var(--cyan)}.shane-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px;margin-top:12px}.shane{cursor:pointer}.structure{width:100%;height:120px}.body{fill:var(--gray)}.arm5{fill:var(--cyan)}.arm3{fill:var(--magenta)}.gene-track{fill:var(--green)}.gene-label{fill:#94f2d2;font-size:9px}.label{fill:var(--muted);font-size:10px}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;color:var(--muted);font-size:11px}.genechips{margin-top:8px;padding-top:7px;border-top:1px solid var(--line)}.genechip{margin:2px;background:#123b38;border:1px solid #26715f;color:#a9f4d9;text-decoration:none;transition:border-color .15s,box-shadow .15s,background .15s}.modal{display:none;position:fixed;inset:0;z-index:1000!important;background:#000c;padding:6vh 8vw;overflow-y:auto}.modal.open{display:block!important}.dialog{height:auto;min-height:0;max-height:none;overflow:visible;background:var(--modal-bg);border:1px solid var(--modal-border);border-radius:16px;padding:24px 28px;box-sizing:border-box}.modaltop{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;width:100%;margin:0 auto 16px auto;gap:12px}.modal-heading{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:8px;width:100%}.modal-title-row{display:inline-flex;align-items:center;justify-content:center;gap:14px;white-space:nowrap;margin:0 auto}.modal-title-row h2{font-size:24px;font-weight:700;margin:0;white-space:nowrap}.nav-arrow-btn{background:transparent!important;border:1px solid #365079!important;border-radius:50%!important;width:28px!important;height:28px!important;min-width:28px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;font-size:16px!important;cursor:pointer!important;color:var(--ink)!important;line-height:1!important;padding:0!important;box-shadow:none!important;transition:border-color .15s,background .15s,transform .15s!important}.nav-arrow-btn:hover:not(:disabled){border-color:var(--cyan)!important;background:#112644!important;transform:scale(1.1)!important}.nav-arrow-btn:disabled{opacity:.3!important;cursor:not-allowed!important}.modal-cartouche{display:inline-flex;align-items:center;justify-content:center;gap:8px;margin:0 auto;padding:5px 16px;border:1px solid #304b72;border-radius:99px;background:#0d1933;white-space:nowrap;font-size:13px;color:var(--muted)}.modal-cartouche a{color:var(--ink)!important;font-weight:500;text-decoration:none}.modal-cartouche span{color:#4e6386;padding:0 4px}.modal-illustration{width:100%;max-width:920px;margin:0 auto;display:flex;justify-content:center}.modal-illustration .structure{width:100%;height:120px;display:block;margin:0 auto}.panorama{display:grid;grid-template-columns:repeat(6,1fr);gap:7px;background:var(--panel2);border:1px solid var(--line);padding:10px;border-radius:12px;margin:10px 0}.metric{position:relative;text-align:center;color:var(--muted)}.metric b{display:block;color:var(--ink);font-size:15px}.metric .help{display:none;position:absolute;z-index:5;bottom:100%;left:50%;transform:translateX(-50%);width:230px;background:#030612ef;border:1px solid #60789b;border-radius:7px;padding:8px;text-align:left}.metric:hover .help{display:block}.tabs{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0;align-items:center}.tab{display:none}.tab.active{display:block}.gene-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}.gene-card{background:var(--panel);border:1px solid #276857;border-radius:11px;padding:11px;cursor:pointer;transition:border-color .15s,box-shadow .15s}.gene-card:hover{border-color:var(--green);box-shadow:0 0 14px #32d39944}.seqbox,.alignbox{background:var(--seq-bg);border-radius:10px;padding:12px;overflow:auto;font:13px Consolas,monospace}.seqrow{white-space:pre;line-height:1.6}.coord{color:#8396b5}.flank{color:#7588a6}.shseq{color:#fff}.base-at{color:#00f0ff!important}.base-gc{color:#ff2df1!important}.base-n{color:#8396b5!important;font-weight:600}.pair{color:#e9fff8}.gap{color:#566987}.ctx-orient{color:#8396b5!important;text-align:center}.island-block{margin:12px 0;border:1px solid #36527a;border-radius:10px;padding:10px}.island-title{color:var(--yellow);font-weight:700}.direct-ncbi{display:inline-flex;align-items:center;justify-content:center;background:var(--btn-bg);border:1px solid var(--btn-border);color:var(--cyan);padding:6px 12px;border-radius:8px;text-decoration:none;font:inherit;line-height:1;transition:border-color .15s,box-shadow .15s}.direct-ncbi:hover{border-color:var(--accent);box-shadow:0 0 12px var(--accent-glow)}.branch-link{transition:filter .15s,text-shadow .15s,color .15s;cursor:pointer}.branch-link.active-branch{filter:brightness(1.5);text-shadow:0 0 10px #f5b942,0 0 20px #f5b942;color:#ffe57f!important}.duplex-center-wrap{display:inline-block;text-align:left;margin:0 auto}.duplex-center-wrap .fold-block{display:block;width:100%!important;margin:0 0 1.55em 0!important;clear:both;text-align:left}.fold-block{display:block;width:max-content;margin:0 auto 1.55em;clear:both}.fold-line{font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;white-space:pre;margin:0;padding:0}.fold-line.pair{font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;white-space:pre;color:#ffffff;margin:0;padding:0}
.inline-branch-drawer{overflow:hidden;transition:opacity .24s cubic-bezier(.2,.8,.2,1),transform .24s cubic-bezier(.2,.8,.2,1),max-height .28s cubic-bezier(.2,.8,.2,1),padding .24s cubic-bezier(.2,.8,.2,1),margin .24s cubic-bezier(.2,.8,.2,1)}
.methods-modal{z-index:1001!important;overflow-y:auto!important;padding:6vh 8vw!important}.methods-modal .dialog{position:relative;max-width:1040px!important;width:100%!important;height:auto!important;min-height:0!important;max-height:none!important;overflow:visible!important;padding:24px 30px 36px!important;box-sizing:border-box!important;margin:0 auto!important}.methods-modal .modaltop{position:relative!important;display:flex!important;flex-direction:row!important;justify-content:space-between!important;align-items:center!important;width:100%!important;margin-bottom:18px!important}
.methods-qmark{display:inline-flex;align-items:center;justify-content:center;width:17px;height:17px;min-width:17px;border-radius:50%;background:#112644;color:#ffffff;border:1px solid #41577e;font-size:11px;font-weight:700;cursor:pointer;text-decoration:none;margin-left:4px;vertical-align:middle;line-height:1;transition:background .15s,transform .15s,box-shadow .15s}.methods-qmark:hover{background:var(--cyan);color:#050a18;transform:scale(1.18);box-shadow:0 0 10px rgba(37,217,244,0.6);border-color:var(--cyan)}
.methods-section{background:#0b152d;border:1px solid #22385c;border-radius:12px;padding:16px 20px;margin-bottom:16px;font-family:Consolas,'Courier New',monospace;width:100%;box-sizing:border-box}.methods-section h3{color:var(--cyan);margin:0 0 8px 0;font-size:14px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-family:Consolas,'Courier New',monospace}.methods-section p{margin:0 0 8px 0;color:var(--ink);line-height:1.65;font-size:12px}.methods-badge{font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;letter-spacing:.04em;text-transform:uppercase}.badge-lit{background:#0d2820;color:#32d399;border:1px solid #25705a}.badge-theory{background:#0c223c;color:#25d9f4;border:1px solid #1f5778}.badge-spec{background:#2e1f0e;color:#f5b942;border:1px solid #755018}.methods-ref{font-size:11px;color:var(--muted);background:#050914;padding:8px 12px;border-radius:6px;border-left:3px solid var(--cyan);margin-top:8px;line-height:1.5}.methods-ref a{color:var(--cyan);word-break:break-all}.legacy-terminal-card{display:flex;align-items:center;justify-content:center;width:100%;box-sizing:border-box;margin-top:20px;padding:16px 20px;background:#000000;border:1px solid #23385d;border-radius:10px;font-family:Consolas,'Courier New',monospace;font-size:15px;font-weight:700;color:#ffffff;text-align:center;letter-spacing:0.5px;cursor:pointer;transition:all .2s ease;user-select:none}.legacy-terminal-card:hover{border-color:#ffffff!important;box-shadow:0 0 16px rgba(255,255,255,0.4)!important;transform:translateY(-1px)}.legacy-terminal-card:active{transform:translateY(0);box-shadow:0 0 8px rgba(255,255,255,0.6)!important}.no-data{text-align:center;padding:30px;color:var(--muted)}@keyframes reveal{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}
@media(max-width:1150px){.filter-panel-grid{grid-template-columns:1fr}.param-filters{grid-column:1;grid-row:2;flex-wrap:wrap}.filter-divider{grid-column:1;grid-row:3}.filter-actions-col{grid-column:1;grid-row:4;flex-wrap:wrap}.filter-actions-col > button{flex:1 1 auto}.rings{grid-template-columns:repeat(3,1fr)}.workspace-layout{grid-template-columns:1fr}}
@media(max-width:650px){.rings{grid-template-columns:repeat(2,1fr)}.panorama{grid-template-columns:repeat(2,1fr)}header .actions{display:none}}
</style></head><body><header><div id="brand" class="brand-block"></div><div><h1>Browser</h1><div id="assemblyMeta" class="meta"></div></div><div class="actions"><button disabled style="opacity:0.6;cursor:default;" title="Active library">Libraries</button><button onclick="openMethodsModal()">Methods</button><input id="assemblyFile" type="file" accept=".json" hidden><button onclick="downloadGenomeGFF()">Genome GFF3</button><button onclick="downloadAtlas()">Atlas SVG</button><button onclick="downloadTSV()">Filtered TSV</button></div></header><main>
<section class="panel filter-panel"><div class="filter-panel-grid"><div class="search-box-wrap"><div class="filter-group-title">Search</div><input id="search" placeholder="A1, gene:KIT, id:Fc_SHaNE..." oninput="apply()"></div><div class="param-filters"><div class="filter-group"><div class="filter-group-title">Size (bp)</div><div class="filter-inputs"><input id="sizeMin" type="number" min="0" step="100" value="10000" placeholder="10000" oninput="onFilterInputChange()" title="Minimum size (bp)"><span class="range-sep">–</span><input id="sizeMax" type="number" min="0" step="100" placeholder="Max" oninput="onFilterInputChange()" title="Maximum size (bp)"></div></div><div class="filter-group"><div class="filter-group-title">Score</div><div class="filter-inputs"><input id="scoreMin" type="number" min="0" max="1" step=".01" value="0.80" placeholder="0.80" oninput="onFilterInputChange()" title="Minimum score (0 to 1)"><span class="range-sep">–</span><input id="scoreMax" type="number" min="0" max="1" step=".01" placeholder="Max" oninput="onFilterInputChange()" title="Maximum score (0 to 1)"></div></div><div class="filter-group"><div class="filter-group-title">Islands</div><div class="filter-inputs"><input id="islandMin" type="number" min="0" step="1" value="2" placeholder="2" oninput="onFilterInputChange()" title="Minimum island count"><span class="range-sep">–</span><input id="islandMax" type="number" min="0" step="1" placeholder="Max" oninput="onFilterInputChange()" title="Maximum island count"></div></div><div id="geneFilterGroup" class="filter-group"><div class="filter-group-title">Gene-crossing</div><div class="filter-inputs"><input id="geneMin" type="number" min="0" step="1" value="1" placeholder="1" oninput="onFilterInputChange()" title="Minimum gene-crossing count (set 0 to 0 for intergenic)"><span class="range-sep">–</span><input id="geneMax" type="number" min="0" step="1" placeholder="Max" oninput="onFilterInputChange()" title="Maximum gene-crossing count"></div></div><div class="filter-group"><div class="filter-group-title">GC content %</div><div class="filter-inputs"><input id="gcMin" type="number" min="0" max="100" step="0.1" value="30" placeholder="30" oninput="onFilterInputChange()" title="Minimum GC percentage"><span class="range-sep">–</span><input id="gcMax" type="number" min="0" max="100" step="0.1" placeholder="Max" oninput="onFilterInputChange()" title="Maximum GC percentage"></div></div></div><div class="filter-divider"></div><div class="filter-actions-col"><button id="globalFilterBtn" class="toggle" onclick="toggleGlobalFilter()" title="Filter the entire page (chromosomes, SHaNEs, and all stats) using all parameter ranges">Filter page</button><button id="viewToggle" class="toggle" onclick="toggleView()" title="Switch between Chromosome-level overview tracks and individual SHaNEs grid">SHaNEs</button><button id="sortBtn" class="sort-btn" onclick="cycleSort()" title="Natural order: Ordered by natural alphanumeric sequence of chromosomes. Click to toggle."><span id="sortVal" style="color:#ffffff;font-weight:600;">Natural</span></button><select id="sorter" onchange="onSorterSelectChange()" style="display:none;"></select><button onclick="resetFilters()">Reset filters</button><button onclick="bookmark()">Bookmark</button></div></div></section><div id="summary" class="summary"></div><section id="rings" class="rings"></section><section id="graph" class="panel graph-panel"></section><section id="workspace" class="workspace"></section><section id="cards" class="grid"></section></main>
<div id="tip" class="tip"></div>
<div id="methodsModal" class="modal methods-modal" onclick="if(event.target===this)closeMethodsModal()"><div class="dialog"><div class="modaltop" style="position:relative;display:flex;flex-direction:row;justify-content:space-between;align-items:center;width:100%;margin-bottom:18px;"><h2 style="margin:0;font-size:16px;">GReGOrI (Genomic Repeat Grouping &amp; Orientation Identifier) Methods &amp; Exploration Guide</h2><button class="xclose" onclick="closeMethodsModal()" title="Close (Esc)">✕</button></div><div id="methodsBody" style="padding:10px 0 24px 0;font-family:Consolas,'Courier New',monospace;width:100%;box-sizing:border-box;">
__METHODS_HTML__
</div></div></div>
<div id="modal" class="modal" onclick="if(event.target===this)closeModal()"><div class="dialog"><div class="modaltop"><div class="modal-heading"><div class="modal-title-row" style="display:inline-flex;align-items:center;justify-content:center;gap:12px;white-space:nowrap;"><button id="modalPrev" class="nav-arrow-btn" onclick="navigateSHaNE(-1)" title="Previous SHaNE (Left Arrow)" style="background:transparent;border:1px solid #365079;border-radius:50%;width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center;font-size:16px;cursor:pointer;color:var(--ink);line-height:1;padding:0;">‹</button><h2 id="modalTitle" style="margin:0;font-size:22px;white-space:nowrap;"></h2><button id="modalNext" class="nav-arrow-btn" onclick="navigateSHaNE(1)" title="Next SHaNE (Right Arrow)" style="background:transparent;border:1px solid #365079;border-radius:50%;width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center;font-size:16px;cursor:pointer;color:var(--ink);line-height:1;padding:0;">›</button></div><div id="modalSub" class="modal-cartouche" style="white-space:nowrap;"></div></div><div id="modalIllustration" class="modal-illustration"></div><button class="xclose" aria-label="Close" onclick="closeModal()" title="Close (Esc)">✕</button></div><div id="panorama" class="panorama"></div><div id="tabs" class="tabs"></div><section id="tabBody"></section></div></div>
<script>let L=__DATA__,LOGO='__LOGO__',view='chromosomes',globalFilterActive=false,activeStat=null,selectedGroup=null,selectedRecord=null,pointFilter=null,ringState={},lastGraph=null,hasGeneAnalysis=false;
const C={all:'#ff70ea',size:'#ffffff',score:'#00f0ff',islands:'#ffee33',genes:'#00ff88',gc:'#8ba2c2'},NS='http://www.w3.org/2000/svg';const $=id=>document.getElementById(id),fmt=n=>Number(n||0).toLocaleString(),short=n=>n>=1e9?(n/1e9).toFixed(2)+' Gb':n>=1e6?(n/1e6).toFixed(2)+' Mb':n>=1e3?(n/1e3).toFixed(1)+' kb':n+' bp',esc=s=>String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;'),E=(n,a={})=>{let e=document.createElementNS(NS,n);Object.entries(a).forEach(([k,v])=>e.setAttribute(k,v));return e};

function getCentralLoopSeq(s){
  let d = s.details || {};
  let seq = d.candidate_sequence || '';
  let islands = s.islands || [];
  if (!seq || !islands.length) return '';
  let i5 = Math.max(...islands.map(x => x.s_end)) - s.start;
  let i3 = Math.min(...islands.map(x => x.h_start)) - s.start;
  if (i3 > i5 && i5 >= 0 && i3 <= seq.length) {
    return seq.slice(i5, i3);
  }
  return '';
}

function calcIslandThermo(l5_seq, l3_seq, na_conc_m = 0.050, strand_conc_m = 2e-7) {
  let s1 = l5_seq.replace(/[\s]/g, '').toUpperCase();
  let s2 = l3_seq.replace(/[\s]/g, '').toUpperCase();
  let n = Math.min(s1.length, s2.length);
  if (n < 2) return { delta_g_37_kcal: 0, tm_celsius: 0 };

  const NN = {
    'AA/TT': [-7.9, -22.2], 'TT/AA': [-7.9, -22.2],
    'AT/TA': [-7.2, -20.4], 'TA/AT': [-7.2, -21.3],
    'CA/GT': [-8.5, -22.7], 'GT/CA': [-8.4, -22.4],
    'CT/GA': [-7.8, -21.0], 'GA/CT': [-8.2, -22.2],
    'CG/GC': [-10.6, -27.2], 'GC/CG': [-9.8, -24.4],
    'GG/CC': [-8.0, -19.9], 'CC/GG': [-8.0, -19.9],
    'AC/TG': [-8.4, -22.4], 'TG/AC': [-8.5, -22.7],
    'TC/AG': [-8.2, -22.2], 'AG/TC': [-7.8, -21.0]
  };

  const isWC = (a, b) => {
    let p = (a + b).toUpperCase();
    return p === 'AT' || p === 'TA' || p === 'GC' || p === 'CG';
  };

  let direct_wc = 0, rev_wc = 0;
  for (let i = 0; i < n; i++) {
    if (isWC(s1[i], s2[i])) direct_wc++;
    if (isWC(s1[i], s2[n - 1 - i])) rev_wc++;
  }
  if (rev_wc > direct_wc) s2 = [...s2].reverse().join('');

  let dh = 0, ds = 0;
  let valid_pairs = [];
  for (let i = 0; i < n; i++) {
    if (s1[i] !== '.' && s2[i] !== '.') valid_pairs.push([s1[i], s2[i]]);
  }
  if (valid_pairs.length) {
    let p1 = valid_pairs[0].join(''), pn = valid_pairs[valid_pairs.length - 1].join('');
    if (p1 === 'GC' || p1 === 'CG') { dh += 0.1; ds += -2.8; }
    else if (p1 === 'AT' || p1 === 'TA') { dh += 2.3; ds += 4.1; }
    if (pn === 'GC' || pn === 'CG') { dh += 0.1; ds += -2.8; }
    else if (pn === 'AT' || pn === 'TA') { dh += 2.3; ds += 4.1; }
  }

  let wc_matches = 0, gc_count = 0;
  for (let i = 0; i < n; i++) {
    if (isWC(s1[i], s2[i])) {
      wc_matches++;
      if (s1[i] === 'G' || s1[i] === 'C') gc_count++;
    }
  }

  for (let i = 0; i < n - 1; i++) {
    let c1_1 = s1[i], c1_2 = s1[i + 1];
    let c2_1 = s2[i], c2_2 = s2[i + 1];
    if (isWC(c1_1, c2_1) && isWC(c1_2, c2_2)) {
      let key = `${c1_1}${c1_2}/${c2_1}${c2_2}`;
      if (NN[key]) {
        dh += NN[key][0]; ds += NN[key][1];
      } else {
        dh += -8.0; ds += -22.0;
      }
    } else {
      dh += 1.0; ds += 2.0;
    }
  }

  let dg_37 = dh - (310.15 * ds) / 1000.0;
  let salt_term = 16.6 * Math.log10(na_conc_m);
  let gc_pct = wc_matches > 0 ? (gc_count / wc_matches) * 100 : 0;
  let mismatch_pct = ((n - wc_matches) / n) * 100;
  let tm_c;

  if (n >= 50) {
    tm_c = 81.5 + salt_term + (0.41 * gc_pct) - (500.0 / n) - (0.61 * mismatch_pct);
  } else {
    let ds_salt = ds + 0.368 * (n - 1) * Math.log(na_conc_m);
    let r_const = 1.9872;
    let denom = ds_salt + r_const * Math.log(strand_conc_m / 4.0);
    if (denom !== 0 && dh < 0) {
      tm_c = (dh * 1000.0) / denom - 273.15;
    } else {
      tm_c = 64.9 + 41.0 * (gc_count - 16.4) / Math.max(1, n);
    }
  }
  return {
    delta_g_37_kcal: Number(dg_37.toFixed(1)),
    tm_celsius: Number(tm_c.toFixed(1))
  };
}

function getIslandStats(s){
  let d = s.details || {};
  let islAlign = d.island_alignment || '';
  let sections = islAlign.split(/(?=Island\s+\d+:)/).filter(x => x.trim() && x.includes('Island'));
  let stats = [];
  s.islands.forEach((isl, i) => {
    let len = Math.max((isl.s_end - isl.s_start) || 0, (isl.h_end - isl.h_start) || 0);
    let sc = null;
    let l5_str = '', l3_str = '';
    if (i < sections.length) {
      let lines = sections[i].trim().split('\n').filter(l => l.trim());
      let l5_line = lines.find(l => /^5['′]/.test(l)) || '';
      let l5 = l5_line.replace(/^5['′]?\s*[-–—]?\s*(?:3['′]?)?\s*:?\s*/i, '').trim();
      let l3_line = lines.find(l => /^3['′]/.test(l)) || '';
      let l3 = l3_line.replace(/^3['′]?\s*[-–—]?\s*(?:5['′]?)?\s*:?\s*/i, '').trim();
      l5_str = l5; l3_str = l3;
      if (l5 && l3) {
        let maxL = Math.max(l5.length, l3.length);
        let l5_pad = l5.padEnd(maxL, ' '), l3_pad = l3.padEnd(maxL, ' ');
        let m = 0;
        for (let j = 0; j < maxL; j++) {
          let p = (l5_pad[j] + l3_pad[j]).toUpperCase();
          if (p === 'AT' || p === 'TA' || p === 'GC' || p === 'CG') m++;
        }
        sc = maxL > 0 ? (m / maxL) : 0;
      }
    }
    if (sc === null) sc = isl.score !== undefined ? Number(isl.score) : Number(s.score || 1.0);
    isl.calculated_score = sc;
    let th = (l5_str && l3_str) ? calcIslandThermo(l5_str, l3_str) : (isl.thermodynamics || {});
    isl.calculated_thermo = th;
    stats.push({ index: i + 1, length: len, score: sc, isl, thermo: th });
  });
  return stats;
}

function init(){brand.innerHTML=LOGO?`<img class="logo" src="${LOGO}">`:'<b>GReGOrI</b>';hydrate();if(typeof assemblyFile!=='undefined'&&assemblyFile)assemblyFile.onchange=loadAssembly;apply()}
function hydrate(){
  let a=L.assemblies?.[0]||{};
  let srcName = (a.source || '').toUpperCase();
  assemblyMeta.innerHTML=`${esc(a.species)} • ${esc(a.name)} • ${esc(srcName)} • ${esc(a.accession)}`;
  hasGeneAnalysis = L.shanes.some(s => s.genes && s.genes.length > 0) || !!a.has_gene_annotations;
  L.shanes.forEach(s=>{
    s.start=s.coordinates.start;s.end=s.coordinates.end;s.gene_count=s.genes.length;s.island_count=s.islands.length;
    let stList = getIslandStats(s);
    s.island_stats = stList;
    
    let loopSeq = getCentralLoopSeq(s);
    let cl = s.central_loop_analysis || (s.details && s.details.central_loop_analysis) || {};
    let hasN = /[Nn]/.test(loopSeq) || !loopSeq || (cl.loop_seq && /[Nn]/.test(cl.loop_seq)) || cl.has_n_bases || cl.contains_null_bases;
    if (hasN) {
      cl.has_central_loop = false;
      cl.has_n_bases = true;
      cl.contains_null_bases = true;
      cl.hypothesis_badge = 'Excluded (Contains N)';
      cl.hypothesis_text = 'Central loop contains undetermined/null (N) bases and was excluded from thermodynamic and self-folding analysis.';
      s.central_loop_analysis = cl;
      if (s.details) s.details.central_loop_analysis = cl;
    }
  });
  
  let gGroup = document.getElementById('geneFilterGroup');
  if (gGroup && !hasGeneAnalysis) {
    gGroup.style.opacity = '0.38';
    gGroup.title = 'Gene annotations not available in this library';
    let gInps = gGroup.querySelectorAll('input');
    gInps.forEach(inp => { inp.disabled = true; inp.style.cursor = 'not-allowed'; });
  }
  setSorter();
}
function setSorter(){
  sorter.innerHTML='<option value="position">Natural</option><option value="count">SHaNE count</option>';
  updateSortBtnLabel();
}
function cycleSort(){
  if(!sorter || !sorter.options.length) return;
  let nextIdx = (sorter.selectedIndex + 1) % sorter.options.length;
  sorter.selectedIndex = nextIdx;
  updateSortBtnLabel();
  apply();
}
function onSorterSelectChange(){
  updateSortBtnLabel();
  apply();
}
function updateSortBtnLabel(){
  let el = document.getElementById('sortVal');
  let btn = document.getElementById('sortBtn');
  if (sorter && sorter.options.length) {
    let curVal = sorter.value;
    let label = curVal === 'count' ? 'SHaNE count' : 'Natural';
    if (el) el.textContent = label;
    if (btn) {
      btn.title = curVal === 'count'
        ? 'SHaNE count: Ordered by number of SHaNEs per chromosome (descending). Click to toggle.'
        : 'Natural: Ordered by natural alphanumeric sequence of chromosomes. Click to toggle.';
    }
  }
}
function scope(){return selectedGroup?L.shanes.filter(s=>s.chromosome_group===selectedGroup):L.shanes}
function textMatch(s,q){if(!q)return true;q=q.toLowerCase().trim();if(q.startsWith('gene:'))return s.genes.some(g=>String(g.symbol||g.locus_tag||'').toLowerCase().includes(q.slice(5)));if(q.startsWith('id:'))return [s.systematic_name,s.stable_id,s.short_id].some(x=>String(x).toLowerCase().includes(q.slice(3)));if(/^[a-z]+\d+(?:_\d+)?$/i.test(q))return s.chromosome_group.toLowerCase()===q||s.sequence_display_name.toLowerCase()===q;return [s.systematic_name,s.stable_id,s.short_id,s.chromosome_group,s.sequence_accession,...s.genes.map(g=>g.symbol)].join(' ').toLowerCase().includes(q)}

function getMinMax(k){
  let sMin = (typeof sizeMin!=='undefined'&&sizeMin&&sizeMin.value!=='') ? +sizeMin.value : 0;
  let sMax = (typeof sizeMax!=='undefined'&&sizeMax&&sizeMax.value!=='') ? +sizeMax.value : Infinity;
  let scMin = (typeof scoreMin!=='undefined'&&scoreMin&&scoreMin.value!=='') ? +scoreMin.value : 0;
  let scMax = (typeof scoreMax!=='undefined'&&scoreMax&&scoreMax.value!=='') ? +scoreMax.value : Infinity;
  let isMin = (typeof islandMin!=='undefined'&&islandMin&&islandMin.value!=='') ? +islandMin.value : 0;
  let isMax = (typeof islandMax!=='undefined'&&islandMax&&islandMax.value!=='') ? +islandMax.value : Infinity;
  let gnMin = (typeof geneMin!=='undefined'&&geneMin&&geneMin.value!=='') ? +geneMin.value : 0;
  let gnMax = (typeof geneMax!=='undefined'&&geneMax&&geneMax.value!=='') ? +geneMax.value : Infinity;
  let gcMinVal = (typeof gcMin!=='undefined'&&gcMin&&gcMin.value!=='') ? +gcMin.value : 0;
  let gcMaxVal = (typeof gcMax!=='undefined'&&gcMax&&gcMax.value!=='') ? +gcMax.value : Infinity;
  if(k==='size') return {min:sMin, max:sMax};
  if(k==='score') return {min:scMin, max:scMax};
  if(k==='islands') return {min:isMin, max:isMax};
  if(k==='genes') return {min:gnMin, max:gnMax};
  if(k==='gc') return {min:gcMinVal, max:gcMaxVal};
  return {min:0, max:Infinity};
}

function matchSingleFilter(k, s){
  let {min, max} = getMinMax(k);
  if(k==='size') return s.length_bp >= min && s.length_bp <= max;
  if(k==='score') return s.score >= min && s.score <= max;
  if(k==='islands') return s.island_count >= min && s.island_count <= max;
  if(k==='genes') return s.gene_count >= min && s.gene_count <= max;
  if(k==='gc') { let v = s.gc_content_percent ?? 0; return v >= min && v <= max; }
  return true;
}

function filtered(ignoreStat=false){
  let arr = scope().filter(s => textMatch(s, search.value));
  if (globalFilterActive) {
    let sMin=sizeMin.value!==''?+sizeMin.value:0, sMax=sizeMax.value!==''?+sizeMax.value:Infinity;
    let scMin=scoreMin.value!==''?+scoreMin.value:0, scMax=scoreMax.value!==''?+scoreMax.value:Infinity;
    let isMin=islandMin.value!==''?+islandMin.value:1, isMax=islandMax.value!==''?+islandMax.value:Infinity;
    let gnMin=geneMin.value!==''?+geneMin.value:0, gnMax=geneMax.value!==''?+geneMax.value:Infinity;
    let gcMinVal=gcMin.value!==''?+gcMin.value:0, gcMaxVal=gcMax.value!==''?+gcMax.value:Infinity;
    arr = arr.filter(s =>
      s.length_bp >= sMin && s.length_bp <= sMax &&
      s.score >= scMin && s.score <= scMax &&
      s.island_count >= isMin && s.island_count <= isMax &&
      (!hasGeneAnalysis || (s.gene_count >= gnMin && s.gene_count <= gnMax)) &&
      (s.gc_content_percent ?? 0) >= gcMinVal && (s.gc_content_percent ?? 0) <= gcMaxVal
    );
  }
  if (!ignoreStat && activeStat) {
    arr = arr.filter(s => matchSingleFilter(activeStat, s));
  }
  if (pointFilter) arr = arr.filter(s => pointFilter.test(s));
  return arr;
}

function toggleGlobalFilter(){
  globalFilterActive = !globalFilterActive;
  let btn = document.getElementById('globalFilterBtn');
  if (btn) btn.classList.toggle('active', globalFilterActive);
  apply();
}

function onFilterInputChange(){
  renderRings();
  if (activeStat) renderGraph();
  if (globalFilterActive) {
    renderWorkspace();
    renderCards();
    updateSummary();
  }
}

function updateSummary(){
  let n = filtered().length;
  let filterNote = globalFilterActive ? ' (page filtered by parameters)' : (activeStat ? ` (filtered by ${activeStat.toUpperCase()})` : '');
  summary.textContent = `${n} matching SHaNEs • denominator ${scope().length} ${selectedGroup ? 'in chromosome ' + selectedGroup : 'in assembly'}${filterNote}`;
}

function apply(){
  renderRings();
  renderGraph();
  renderWorkspace();
  renderCards();
  updateSummary();
}

function renderRings(){
  let base = scope().filter(s => textMatch(s, search.value));
  let den = base.length || scope().length;
  let chosen = globalFilterActive ? filtered(true) : (activeStat ? base.filter(s => matchSingleFilter(activeStat, s)) : base);

  let defs = [
    ['all', 'All SHaNEs', ''],
    ['size', 'Size', getRangeLabel('size')],
    ['score', 'Score', getRangeLabel('score')],
    ['islands', 'Islands', getRangeLabel('islands')],
    ['genes', 'Gene-crossing', getRangeLabel('genes')],
    ['gc', 'GC %', getRangeLabel('gc')]
  ];

  rings.innerHTML = '';
  defs.forEach(([k, title, threshLabel]) => {
    let isGenes = k === 'genes';
    let isDeactivated = isGenes && !hasGeneAnalysis;
    let color = C[k];

    let value;
    if (isDeactivated) {
      value = 0;
    } else if (globalFilterActive || activeStat) {
      value = k === 'all' ? chosen.length : chosen.filter(s => matchSingleFilter(k, s)).length;
    } else {
      value = k === 'all' ? base.length : base.filter(s => matchSingleFilter(k, s)).length;
    }

    let c = document.createElement('article');
    let isActive = activeStat === k;
    c.className = 'panel ring-card' + (isDeactivated ? ' disabled' : '');
    c.title = isDeactivated ? 'No gene annotations available in this library' : `Click to filter view by ${title} ${threshLabel}`;
    
    if (!isDeactivated) {
      c.onmouseenter = () => {
        if (activeStat !== k) {
          c.style.borderColor = color;
          c.style.boxShadow = `0 0 16px ${color}55`;
        }
      };
      c.onmouseleave = () => {
        if (activeStat !== k) {
          c.style.borderColor = '';
          c.style.boxShadow = '';
        }
      };
      c.onclick = () => {
        activeStat = activeStat === k ? null : k;
        pointFilter = null;
        apply();
      };
    }

    if (isActive) {
      c.style.borderColor = color;
      c.style.boxShadow = `0 0 20px ${color}66`;
      c.style.background = '#111f3d';
    } else {
      c.style.borderColor = '';
      c.style.boxShadow = '';
      c.style.background = '';
    }

    let d = 2 * Math.PI * 43, p = den ? value / den : 0, old = ringState[k] || {p: 0, v: 0}, svg = E('svg', {viewBox: '0 0 160 135', class: 'ring'});
    svg.append(E('circle', {cx: 80, cy: 59, r: 43, fill: 'none', stroke: '#1b2a47', 'stroke-width': 14}));
    if ((value || old.v) && !isDeactivated) {
      let a = E('circle', {cx: 80, cy: 59, r: 43, fill: 'none', stroke: color, 'stroke-width': 14, 'stroke-dasharray': `${old.p * d} ${d}`, 'stroke-linecap': 'round', transform: 'rotate(-90 80 59)', class: 'arc'});
      svg.append(a);
      requestAnimationFrame(() => a.setAttribute('stroke-dasharray', `${p * d} ${d}`));
    }
    let t = E('text', {x: 80, y: 66, 'text-anchor': 'middle', fill: isDeactivated ? '#546682' : '#eef8ff', 'font-size': 18, 'font-weight': '700'});
    t.textContent = isDeactivated ? 'N/A' : value;
    svg.append(t);
    c.append(svg);

    let label = document.createElement('div');
    label.className = 'ring-label';
    label.textContent = isDeactivated ? 'Genes (N/A)' : (threshLabel ? `${title} ${threshLabel}` : title);
    c.append(label);

    let cap = document.createElement('div');
    cap.className = 'ring-caption';
    cap.textContent = isDeactivated ? 'No gene data' : `${(p * 100).toFixed(1)}% of scope`;
    c.append(cap);

    if (isActive) {
      let badge = document.createElement('div');
      badge.style.cssText = 'position:absolute;top:8px;right:8px;background:' + color + '22;color:' + color + ';border:1px solid ' + color + ';font-size:10px;font-weight:700;padding:1px 6px;border-radius:99px;';
      badge.textContent = 'Active';
      c.append(badge);
    }
    rings.append(c);
    ringState[k] = {p, v: value};
  });
}

function getRangeLabel(k){
  let {min, max} = getMinMax(k);
  if (k === 'size') {
    if (min === max && max < Infinity) return `= ${short(min)}`;
    if (min > 0 && max < Infinity) return `${short(min)}–${short(max)}`;
    if (min > 0) return `≥ ${short(min)}`;
    if (max < Infinity) return `≤ ${short(max)}`;
    return '≥ 0 bp';
  }
  if (k === 'score') {
    if (min === max && max < Infinity) return `= ${min.toFixed(2)}`;
    if (min > 0 && max < Infinity) return `${min.toFixed(2)}–${max.toFixed(2)}`;
    if (min > 0) return `≥ ${min.toFixed(2)}`;
    if (max < Infinity) return `≤ ${max.toFixed(2)}`;
    return '≥ 0.00';
  }
  if (k === 'islands') {
    if (min === max && max < Infinity) return `= ${min}`;
    if (min > 0 && max < Infinity) return `${min}–${max}`;
    if (min > 0) return `≥ ${min}`;
    if (max < Infinity) return `≤ ${max}`;
    return '≥ 0';
  }
  if (k === 'genes') {
    if (min === 0 && max === 0) return '= 0 (0 genes)';
    if (min === max && max < Infinity) return `= ${min}`;
    if (min > 0 && max < Infinity) return `${min}–${max}`;
    if (min === 0 && max < Infinity) return `0–${max}`;
    if (min > 0) return `≥ ${min}`;
    if (max < Infinity) return `≤ ${max}`;
    return '≥ 0';
  }
  if (k === 'gc') {
    if (min === max && max < Infinity) return `= ${min}%`;
    if (min > 0 && max < Infinity) return `${min}%–${max}%`;
    if (min > 0) return `≥ ${min}%`;
    if (max < Infinity) return `≤ ${max}%`;
    return '≥ 0%';
  }
  return '';
}

function graphMetric(){return activeStat||'all'}
function metric(k,s){
  if(k==='size')return s.length_bp;
  if(k==='score')return s.score;
  if(k==='islands')return s.island_count;
  if(k==='genes')return s.gene_count;
  if(k==='gc')return s.gc_content_percent||0;
  return s.length_bp;
}
function renderGraph(){
  if(!activeStat){graph.classList.remove('open');return}
  graph.classList.add('open');
  let key=graphMetric(),arr=filtered(),vals=arr.map(s=>metric(key,s)),color=C[key];
  let titleStr=key==='score'?'Score':key==='islands'?'Islands per SHaNE':key==='genes'?'Gene-crossing':key==='gc'?'GC content %':'SHaNE length (bp)';
  graph.innerHTML=`<div class="graph-head"><h3>${titleStr} distribution</h3><div class="meta">Click a point to filter the current view</div></div><div class="graph-wrap">${chart(vals,key,color)}</div>${stats(vals)}`;
  bindPoints(key);
}
function formatAxisVal(v, key) {
  if (key === 'score') return Number(v).toFixed(2);
  if (key === 'gc') return Number(v).toFixed(1) + '%';
  if (key === 'size') return short(v);
  return Number.isInteger(v) ? String(v) : Number(v).toFixed(1);
}

function getQuantile(sorted, p) {
  let idx = p * (sorted.length - 1);
  let lo = Math.floor(idx), hi = Math.ceil(idx);
  let w = idx - lo;
  return sorted[lo] * (1 - w) + sorted[hi] * w;
}

function chart(vals, key, color){
  if(!vals.length) return '<div class="no-data">No data</div>';
  let sorted = [...vals].sort((a, b) => a - b);
  let n = sorted.length;
  let mean = vals.reduce((a, b) => a + b, 0) / n;
  let variance = vals.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / n;
  let stdDev = Math.sqrt(variance);

  let discrete = (key === 'islands' || key === 'genes') && (Math.max(...vals) - Math.min(...vals) <= 20);
  let xs = [], counts = [], binsMeta = [];
  
  if (discrete) {
    let min = Math.min(...vals), max = Math.max(...vals);
    for (let x = min; x <= max; x++) {
      xs.push(x);
      let c = vals.filter(v => v === x).length;
      counts.push(c);
      binsMeta.push({ label: String(x), minVal: x, maxVal: x, centerVal: x });
    }
  } else {
    let uniqueVals = Array.from(new Set(sorted));
    let uniqueCount = uniqueVals.length;
    
    let K = n <= 3 ? n : n <= 8 ? Math.min(4, uniqueCount) : n <= 24 ? Math.min(5, uniqueCount) : n <= 60 ? Math.min(8, uniqueCount) : Math.min(10, uniqueCount);
    K = Math.max(2, K);
    
    let bounds = [];
    for (let i = 0; i <= K; i++) {
      bounds.push(getQuantile(sorted, i / K));
    }
    let uniqueBounds = [bounds[0]];
    for (let i = 1; i < bounds.length; i++) {
      if (bounds[i] > uniqueBounds[uniqueBounds.length - 1] + 1e-7) {
        uniqueBounds.push(bounds[i]);
      }
    }
    
    if (uniqueBounds.length <= 1) {
      xs = [sorted[0]];
      counts = [n];
      binsMeta = [{ label: formatAxisVal(sorted[0], key), minVal: sorted[0], maxVal: sorted[0], centerVal: sorted[0] }];
    } else {
      let numBins = uniqueBounds.length - 1;
      for (let i = 0; i < numBins; i++) {
        let bLo = uniqueBounds[i], bHi = uniqueBounds[i + 1];
        let mid = (bLo + bHi) / 2;
        xs.push(mid);
        let c = sorted.filter(v => (i === numBins - 1) ? (v >= bLo && v <= bHi) : (v >= bLo && v < bHi)).length;
        counts.push(c);
        binsMeta.push({
          label: formatAxisVal(mid, key),
          rangeLabel: `${formatAxisVal(bLo, key)}–${formatAxisVal(bHi, key)}`,
          minVal: bLo,
          maxVal: bHi,
          centerVal: mid
        });
      }
    }
  }
  
  let W = 780, H = 220, Lf = 58, R = 28, T = 28, B = 42;
  let M = Math.max(...counts, 1);
  let x = i => Lf + i * (W - Lf - R) / Math.max(1, xs.length - 1);
  let y = v => T + (M - v) * (H - T - B) / M;
  let pts = counts.map((v, i) => [x(i), y(v)]);
  
  // Value-to-X coordinate interpolator
  function valToX(val) {
    if (xs.length <= 1) return (Lf + (W - R)) / 2;
    let vMin = xs[0], vMax = xs[xs.length - 1];
    if (val <= vMin) return x(0);
    if (val >= vMax) return x(xs.length - 1);
    for (let i = 0; i < xs.length - 1; i++) {
      let lo = xs[i], hi = xs[i + 1];
      if (val >= lo && val <= hi) {
        let frac = (hi === lo) ? 0 : (val - lo) / (hi - lo);
        return x(i) + frac * (x(i + 1) - x(i));
      }
    }
    return x(0);
  }
  
  let meanX = valToX(mean);
  let sdLoX = valToX(Math.max(sorted[0], mean - stdDev));
  let sdHiX = valToX(Math.min(sorted[sorted.length - 1], mean + stdDev));
  
  let sdBand = '';
  if (sorted.length > 1 && isFinite(sdLoX) && isFinite(sdHiX) && Math.abs(sdHiX - sdLoX) > 1) {
    let leftX = Math.min(sdLoX, sdHiX), widthX = Math.abs(sdHiX - sdLoX);
    sdBand = `
      <rect x="${leftX.toFixed(1)}" y="${T}" width="${widthX.toFixed(1)}" height="${H - T - B}" fill="${color}" fill-opacity="0.08" stroke="${color}" stroke-opacity="0.35" stroke-width="1" stroke-dasharray="2 3" rx="2" />
      <line x1="${sdLoX.toFixed(1)}" y1="${T}" x2="${sdLoX.toFixed(1)}" y2="${H - B}" stroke="${color}" stroke-opacity="0.45" stroke-width="1" stroke-dasharray="2 3" />
      <line x1="${sdHiX.toFixed(1)}" y1="${T}" x2="${sdHiX.toFixed(1)}" y2="${H - B}" stroke="${color}" stroke-opacity="0.45" stroke-width="1" stroke-dasharray="2 3" />
      <text x="${sdLoX.toFixed(1)}" y="${T - 7}" text-anchor="middle" fill="#8fa5c8" font-size="9" font-family="system-ui,sans-serif" font-weight="600">-1σ</text>
      <text x="${sdHiX.toFixed(1)}" y="${T - 7}" text-anchor="middle" fill="#8fa5c8" font-size="9" font-family="system-ui,sans-serif" font-weight="600">+1σ</text>
    `;
  }
  
  let meanOverlay = '';
  if (isFinite(meanX)) {
    meanOverlay = `
      <line x1="${meanX.toFixed(1)}" y1="${T - 4}" x2="${meanX.toFixed(1)}" y2="${H - B}" stroke="#ffffff" stroke-width="1.8" stroke-dasharray="4 3" style="filter:drop-shadow(0 0 4px rgba(255,255,255,0.7));" />
      <rect x="${(meanX - 28).toFixed(1)}" y="${(T - 18).toFixed(1)}" width="56" height="15" rx="3" fill="#09152b" stroke="#ffffff" stroke-width="1" />
      <text x="${meanX.toFixed(1)}" y="${(T - 7).toFixed(1)}" text-anchor="middle" fill="#ffffff" font-size="9" font-family="system-ui,sans-serif" font-weight="700">μ = ${formatAxisVal(mean, key)}</text>
    `;
  }

  // Sharp digital ECG telemetry path
  let path = pts.map((p, i) => (i === 0 ? 'M' : 'L') + ` ${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
  let area = `${path} L ${pts[pts.length-1][0].toFixed(1)} ${H-B} L ${pts[0][0].toFixed(1)} ${H-B} Z`;
  
  // Digital ECG telemetry oscilloscope grid
  let grid = '';
  for (let i = 0; i <= 4; i++) {
    let yy = T + i * (H - T - B) / 4;
    grid += `<line x1="${Lf}" y1="${yy}" x2="${W-R}" y2="${yy}" class="gridline" stroke="#1d3860" stroke-width="1" stroke-dasharray="3 3"/><text x="${Lf-8}" y="${yy+4}" text-anchor="end" class="axistext">${Math.round(M*(1-i/4))}</text>`;
  }
  for (let i = 0; i < xs.length; i++) {
    let xx = x(i);
    grid += `<line x1="${xx}" y1="${T}" x2="${xx}" y2="${H-B}" stroke="#132744" stroke-width="1" stroke-dasharray="2 4"/>`;
  }
  
  let labels = binsMeta.map((bm, i) => `<text x="${x(i)}" y="${H-15}" text-anchor="middle" class="axistext">${bm.label}</text>`).join('');
  let points = counts.map((v, i) => `<circle class="point" data-idx="${i}" data-min="${binsMeta[i].minVal}" data-max="${binsMeta[i].maxVal}" data-label="${binsMeta[i].rangeLabel || binsMeta[i].label}" data-count="${v}" cx="${x(i)}" cy="${y(v)}" r="4.2" fill="#081426" stroke="${color}" stroke-width="2.4" style="filter:drop-shadow(0 0 5px ${color});cursor:pointer;"/>`).join('');
  
  let gradId = `ecgGrad_${key}`;
  let defs = `<defs><linearGradient id="${gradId}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${color}" stop-opacity="0.32"/><stop offset="80%" stop-color="${color}" stop-opacity="0.04"/><stop offset="100%" stop-color="${color}" stop-opacity="0"/></linearGradient></defs>`;
  
  return `<svg class="chart" viewBox="0 0 ${W} ${H}" style="overflow:visible;">${defs}${grid}${sdBand}<path d="${area}" fill="url(#${gradId})" /><path d="${path}" fill="none" stroke="${color}" stroke-width="2.6" stroke-linejoin="miter" stroke-linecap="square" style="filter:drop-shadow(0 0 6px ${color}99);"/>${meanOverlay}${points}<line x1="${Lf}" y1="${H-B}" x2="${W-R}" y2="${H-B}" class="axis" stroke="#254773" stroke-width="1.5"/>${labels}</svg>`;
}

function stats(v){
  if(!v.length) return '<div class="no-data">No data</div>';
  let a=[...v].sort((x,y)=>x-y), n=v.length;
  let mean=v.reduce((x,y)=>x+y,0)/n;
  let med=n%2?a[(n-1)/2]:(a[n/2-1]+a[n/2])/2;
  let variance=v.reduce((acc,val)=>acc+Math.pow(val-mean,2),0)/n;
  let stdDev=Math.sqrt(variance);
  let minVal=Math.min(...v);
  let maxVal=Math.max(...v);
  let fmtStat=x=>Number.isFinite(x)?Number(x.toFixed(2)):x;
  return `<div class="graph-stats"><span><b>${n}</b>n</span><span><b>${fmtStat(mean)}</b>mean</span><span><b>${fmtStat(stdDev)}</b>std dev (σ)</span><span><b>${fmtStat(med)}</b>median</span><span><b>${fmtStat(minVal)}</b>minimum</span><span><b>${fmtStat(maxVal)}</b>maximum</span></div>`;
}

function bindPoints(key){
  document.querySelectorAll('.point').forEach(p => {
    let lbl = p.dataset.label, count = p.dataset.count, minVal = +p.dataset.min, maxVal = +p.dataset.max;
    p.onmousemove = e => {
      tip.style.display = 'block';
      tip.style.left = e.clientX + 12 + 'px';
      tip.style.top = e.clientY + 12 + 'px';
      tip.textContent = `${lbl}: ${count} SHaNEs`;
    };
    p.onmouseleave = () => tip.style.display = 'none';
    p.onclick = () => {
      pointFilter = {
        test: s => {
          let v = metric(key, s);
          if (minVal === maxVal) return Math.abs(v - minVal) < 1e-6;
          return v >= minVal && v <= maxVal;
        }
      };
      apply();
    };
  });
}
function renderCards(){if(selectedGroup){cards.innerHTML='';return}let arr=filtered();if(view==='chromosomes')renderChromosomes(arr);else renderShanes(cards,arr)}
function renderChromosomes(arr){
  cards.className='grid';cards.innerHTML='';let groups={};L.sequence_records.forEach(r=>(groups[r.chromosome_group]??=[]).push(r));
  let entries=Object.entries(groups),sort=sorter.value;
  if(sort==='count')entries.sort((a,b)=>arr.filter(s=>s.chromosome_group===b[0]).length-arr.filter(s=>s.chromosome_group===a[0]).length);
  else entries.sort((a,b)=>a[0].localeCompare(b[0],undefined,{numeric:true}));
  entries.forEach(([g,rs])=>{
    let hits=arr.filter(s=>s.chromosome_group===g),main=rs.find(r=>r.display_name===g)||rs[0],c=document.createElement('article');
    c.className='card chrom';c.onclick=()=>selectChrom(g);
    c.innerHTML=`<div class="head"><b>${esc(g)}</b><span class="badge">${hits.length} SHaNEs</span></div><div class="meta">${short(main.length_bp)} • ${rs.length} record(s)</div>`;
    let v=E('svg',{viewBox:'0 0 1000 70',class:'mini'});
    v.append(E('line',{x1:50,y1:35,x2:950,y2:35,class:'track','stroke-width':12}));
    let maxL=Math.max(...hits.map(s=>s.length_bp||1),1),minL=Math.min(...hits.map(s=>s.length_bp||1),1);
    hits.filter(s=>s.sequence_accession===main.sequence_accession).forEach(s=>{
      let x=50+s.start/main.length_bp*900;
      let norm=(s.length_bp-minL)/Math.max(1,maxL-minL);
      let halfH=8+norm*16;
      let hitColor=(hasGeneAnalysis && s.gene_count>0)?'#32d399':'#ee3edc';
      let line=E('line',{x1:x,y1:35-halfH,x2:x,y2:35+halfH,class:'hit',style:`cursor:pointer;stroke:${hitColor};stroke-width:2.8px;transition:stroke-width .15s;`});
      line.onmouseenter=e=>{
        e.stopPropagation();tip.style.display='block';tip.style.left=e.clientX+14+'px';tip.style.top=e.clientY+14+'px';
        tip.innerHTML=`<b>${esc(s.systematic_name)}</b> (${esc(s.short_id)})<br>${fmt(s.start)}–${fmt(s.end)} bp (${fmt(s.length_bp)} bp)<br>Score: ${Number(s.score).toFixed(4)} • Islands: ${s.island_count} • GC: ${Number(s.gc_content_percent).toFixed(1)}%<br><span style="color:${hitColor};">${hasGeneAnalysis?(s.gene_count>0?`Gene-crossing: ${s.gene_count}`:'No gene overlap'):'Intergenic SHaNE'}</span>`;
        line.style.strokeWidth='5px';
        line.style.filter=`drop-shadow(0 0 8px ${hitColor})`;
      };
      line.onmouseleave=()=>{tip.style.display='none';line.style.strokeWidth='2.8px';line.style.filter='none';};
      line.onclick=e=>{e.stopPropagation();openSHaNE(s);};
      v.append(line);
    });
    c.append(v);cards.append(c);
  });
}
function selectChrom(g){selectedGroup=g;selectedRecord=null;activeStat=null;pointFilter=null;view='chromosomes';workspace.scrollIntoView({behavior:'smooth'});apply()}
function renderWorkspace(){
  if(!selectedGroup){workspace.classList.remove('open');workspace.innerHTML='';return}
  workspace.classList.add('open');
  let recs=L.sequence_records.filter(r=>r.chromosome_group===selectedGroup),main=recs.find(r=>r.display_name===selectedGroup)||recs[0];
  if(!selectedRecord)selectedRecord=main.sequence_accession;
  let rec=recs.find(r=>r.sequence_accession===selectedRecord)||main,arr=filtered();
  let chromHits=arr.filter(s=>s.sequence_accession===rec.sequence_accession);
  let chromTitle=selectedGroup.startsWith('LG')||selectedGroup.toLowerCase().startsWith('chr')||selectedGroup==='MT'||selectedGroup==='Mitochondrion'?selectedGroup:`Chromosome ${selectedGroup}`;
  
  let legendHTML = hasGeneAnalysis ? `
    <div class="chrom-legend" style="display:inline-flex;align-items:center;gap:12px;font-size:11px;color:var(--muted);background:#091227;padding:4px 12px;border-radius:99px;border:1px solid #1f3558;">
      <span style="display:inline-flex;align-items:center;gap:5px;"><span style="width:9px;height:9px;border-radius:2px;background:#32d399;"></span> Gene-crossing (${chromHits.filter(s=>s.gene_count>0).length})</span>
      <span style="display:inline-flex;align-items:center;gap:5px;"><span style="width:9px;height:9px;border-radius:2px;background:#ee3edc;"></span> Intergenic (${chromHits.filter(s=>s.gene_count===0).length})</span>
    </div>
  ` : `
    <div class="chrom-legend" style="display:inline-flex;align-items:center;gap:8px;font-size:11px;color:var(--muted);background:#091227;padding:4px 12px;border-radius:99px;border:1px solid #1f3558;">
      <span style="width:9px;height:9px;border-radius:2px;background:#ee3edc;"></span> SHaNEs (${chromHits.length})
    </div>
  `;

  workspace.innerHTML=`<div class="workspace-layout"><div class="panel" style="display:flex;flex-direction:column;justify-content:space-between;"><div class="head" style="display:flex;align-items:center;justify-content:space-between;width:100%;"><div style="flex:0 0 auto;"><button class="workspace-btn" onclick="closeChrom()">← Overview</button></div><div style="flex:1 1 auto;text-align:center;padding:0 12px;"><h2 style="margin:0 0 3px 0;font-size:18px;">${esc(chromTitle)}</h2><div class="meta" style="font-size:12px;">${esc(rec.display_name)} • ${esc(rec.sequence_accession)} • ${short(rec.length_bp)} • ${chromHits.length} SHaNEs</div></div><div style="flex:0 0 auto;display:flex;align-items:center;gap:6px;"><button class="workspace-btn" onclick="downloadChromGFF()">Chromosome GFF3</button><button class="workspace-btn" onclick="downloadAtlas(true)">Chromosome atlas</button></div></div><svg id="maintrack" class="maintrack" viewBox="0 0 1100 170"></svg><div style="display:flex;justify-content:flex-end;align-items:center;margin-top:2px;padding-right:6px;">${legendHTML}</div></div><div class="panel"><b>Sequence records</b><div class="records">${recs.map(r=>`<button class="record ${r.sequence_accession===selectedRecord?'active':''} ${r===main?'':'sub'}" onclick="selectRecord('${r.sequence_accession}')"><span>${r===main?'Main: ':''}${esc(r.display_name)}</span><span>${arr.filter(s=>s.sequence_accession===r.sequence_accession).length}</span></button>`).join('')}</div></div></div><div id="chromShanes" class="shane-grid"></div>`;
  drawMain(rec,chromHits);
  renderShanes(chromShanes,chromHits);
}
function drawMain(rec,hits){
  let v=maintrack;v.innerHTML='';v.append(E('line',{x1:65,y1:80,x2:1035,y2:80,class:'track','stroke-width':13}));
  let maxL=Math.max(...hits.map(s=>s.length_bp||1),1),minL=Math.min(...hits.map(s=>s.length_bp||1),1);
  hits.forEach(s=>{
    let x=65+s.start/rec.length_bp*970;
    let norm=(s.length_bp-minL)/Math.max(1,maxL-minL);
    let halfH=14+norm*26;
    let hitColor=(hasGeneAnalysis && s.gene_count>0)?'#32d399':'#ee3edc';
    let line=E('line',{x1:x,y1:80-halfH,x2:x,y2:80+halfH,class:'hit',style:`cursor:pointer;stroke:${hitColor};stroke-width:4px;transition:stroke-width .15s,filter .15s;`});
    line.onmouseenter=e=>{
      tip.style.display='block';tip.style.left=e.clientX+14+'px';tip.style.top=e.clientY+14+'px';
      tip.innerHTML=`<b>${esc(s.systematic_name)}</b> <span class="badge" style="font-size:10px;">${esc(s.short_id)}</span><br>${fmt(s.start)}–${fmt(s.end)} bp (${fmt(s.length_bp)} bp)<br>Score: ${Number(s.score).toFixed(4)} • Islands: ${s.island_count} • GC: ${Number(s.gc_content_percent).toFixed(1)}%<br><span style="color:${hitColor};">${hasGeneAnalysis?(s.gene_count>0?`Gene-crossing: ${s.gene_count}`:'No gene overlap'):'Intergenic SHaNE'}</span>`;
      line.style.strokeWidth='7px';line.style.filter=`drop-shadow(0 0 10px ${hitColor})`;
    };
    line.onmouseleave=()=>{tip.style.display='none';line.style.strokeWidth='4px';line.style.filter='none';};
    line.onclick=()=>openSHaNE(s);
    v.append(line);
  });
  for(let i=0;i<=5;i++){let t=E('text',{x:65+i*194,y:145,'text-anchor':'middle',class:'label'});t.textContent=short(rec.length_bp*i/5);v.append(t)}
}
function closeChrom(){selectedGroup=null;selectedRecord=null;apply();workspace.scrollIntoView({behavior:'smooth'})}
function selectRecord(a){selectedRecord=a;apply()}
function renderShanes(root,arr){
  root.innerHTML='';
  let sort=sorter.value;
  if(sort==='count'){
    arr=[...arr].sort((a,b)=>b.island_count-a.island_count||b.total_island_length_bp-a.total_island_length_bp||b.length_bp-a.length_bp);
  }else{
    arr=[...arr].sort((a,b)=>a.chromosome_group.localeCompare(b.chromosome_group,undefined,{numeric:true})||a.start-b.start);
  }
  arr.forEach(s=>{
    let c=document.createElement('article');c.className='card shane';
    let lenText=s.length_with_voids_bp&&s.length_with_voids_bp!==s.length_bp?`${fmt(s.length_bp)} bp (${fmt(s.length_with_voids_bp)} with voids)`:`${fmt(s.length_bp)} bp`;
    let genesMetric = hasGeneAnalysis ? `<span title="Number of annotated genes overlapping this SHaNE interval">Gene-crossing ${s.gene_count}</span>` : `<span title="Gene annotations not loaded" style="opacity:0.5;">Genes: N/A</span>`;
    let geneChipsHTML = hasGeneAnalysis ? (s.genes.length?s.genes.map(g=>`<a class="chip genechip" href="${g.ncbi_url}" target="_blank" onclick="event.stopPropagation()">${esc(g.symbol||g.locus_tag||g.feature_id)}</a>`).join(' '):'<span class="meta">No crossed gene</span>') : '<span class="meta">No gene annotations loaded</span>';
    c.innerHTML=`<div class="head"><b>${esc(s.systematic_name)}</b><span class="badge">${esc(s.short_id)}</span></div><div class="meta">${fmt(s.start)}–${fmt(s.end)} bp</div>`;
    c.append(structure(s));
    c.insertAdjacentHTML('beforeend',`<div class="metrics"><span title="Genomic Length: End - Start (${fmt(s.length_bp)} bp)${s.length_with_voids_bp ? ' • Alignment with voids: ' + fmt(s.length_with_voids_bp) + ' bp' : ''}">Length ${lenText}</span><span title="Number of complementary island stem pairs detected between opposing arms">Islands ${s.island_count}</span><span title="Sum of all individual 5′ island stem arm lengths in base pairs">Total island length ${fmt(s.total_island_length_bp)} bp</span><span title="Maximized Watson-Crick score: Matches / Total duplex length (${(Number(s.score)*100).toFixed(2)}%)">Score ${Number(s.score).toFixed(4)}</span><span title="GC Content: (G + C) / (A + C + G + T) × 100% of sequenced bases (excluding dead Ns)">GC ${Number(s.gc_content_percent).toFixed(2)}%</span>${genesMetric}</div><div class="genechips">${geneChipsHTML}</div>`);
    c.onclick=()=>openSHaNE(s);
    root.append(c);
  });
}
function structure(s, isModal = false){
  let v=E('svg',{viewBox:'0 0 1000 120',class:'structure'}),lo=s.start,span=Math.max(1,s.end-s.start),x=p=>125+(p-lo)/span*825;
  let stList = s.island_stats || getIslandStats(s);

  s.islands.forEach((a, idx)=>{
    let islIdx = idx + 1;
    let st = stList[idx] || { score: (a.score || s.score || 1.0) };
    let islScore = st.score !== undefined ? st.score : (a.calculated_score || s.score || 1.0);
    let x5_start=x(a.s_start),x5_end=x(a.s_end),w5=Math.max(4,x5_end-x5_start);
    let th = st.thermo || a.calculated_thermo || a.thermodynamics || {};
    let thermoTip = th.delta_g_37_kcal !== undefined ? ` • ΔG°₃₇: ${th.delta_g_37_kcal} kcal/mol • Tm: ${th.tm_celsius}°C (SantaLucia 1998)` : '';
    let pad = Math.max(500, Math.round((a.h_end - a.s_start) * 0.15));
    let islLo = Math.max(1, a.s_start + 1 - pad), islHi = a.h_end + pad;
    let ncbiAcc = encodeURIComponent(s.sequence_accession);
    let scoreInt = Math.round(islScore * 100);
    let marks = `${s.start+1}:${s.end}|${encodeURIComponent(s.systematic_name)}|8592A8,${a.s_start+1}:${a.s_end}|I${islIdx}_5p_sc${scoreInt}|25D9F4,${a.h_start+1}:${a.h_end}|I${islIdx}_3p_sc${scoreInt}|EE3EDC`;
    let islUrl = `https://www.ncbi.nlm.nih.gov/nuccore/${ncbiAcc}?report=graph&v=${islLo}:${islHi}&mk=${encodeURIComponent(marks)}&content=4`;

    let r5=E('rect',{x:x5_start,y:36,width:w5,height:14,rx:0,fill:'#25d9f4',style:'cursor:pointer;transition:filter .15s;'});
    r5.onmouseenter=e=>{
      tip.style.display='block';tip.style.left=e.clientX+14+'px';tip.style.top=e.clientY+14+'px';
      tip.innerHTML=`<b>Island ${islIdx} (5′ Arm)</b><br>${fmt(a.s_start)}–${fmt(a.s_end)} bp (${a.s_end-a.s_start} bp) • Score: ${islScore.toFixed(4)}${thermoTip}<br><span style="color:#25d9f4;font-size:10px;">${isModal ? 'Click to view in NCBI Graph Viewer ↗' : 'Click card to view details'}</span>`;
      r5.style.filter='drop-shadow(0 0 8px #25d9f4)';
    };
    r5.onmouseleave=()=>{tip.style.display='none';r5.style.filter='none';};
    if (isModal) {
      r5.onclick=e=>{e.stopPropagation();window.open(islUrl,'_blank');};
    }
    v.append(r5);
    
    let x3_start=x(a.h_start),x3_end=x(a.h_end),w3=Math.max(4,x3_end-x3_start);
    let r3=E('rect',{x:x3_start,y:36,width:w3,height:14,rx:0,fill:'#ee3edc',style:'cursor:pointer;transition:filter .15s;'});
    r3.onmouseenter=e=>{
      tip.style.display='block';tip.style.left=e.clientX+14+'px';tip.style.top=e.clientY+14+'px';
      tip.innerHTML=`<b>Island ${islIdx} (3′ Arm)</b><br>${fmt(a.h_start)}–${fmt(a.h_end)} bp (${a.h_end-a.h_start} bp) • Score: ${islScore.toFixed(4)}${thermoTip}<br><span style="color:#ee3edc;font-size:10px;">${isModal ? 'Click to view in NCBI Graph Viewer ↗' : 'Click card to view details'}</span>`;
      r3.style.filter='drop-shadow(0 0 8px #ee3edc)';
    };
    r3.onmouseleave=()=>{tip.style.display='none';r3.style.filter='none';};
    if (isModal) {
      r3.onclick=e=>{e.stopPropagation();window.open(islUrl,'_blank');};
    }
    v.append(r3);
  });

  v.append(E('rect',{x:125,y:56,width:825,height:14,rx:0,fill:'#0e172e',stroke:'#233654','stroke-width':1}));

  if (hasGeneAnalysis) {
    s.genes.forEach(g=>{
      let g_start=g.genomic_start!==undefined?g.genomic_start:g.start;
      let g_end=g.genomic_end!==undefined?g.genomic_end:g.end;
      let gs=Math.max(lo,g_start),ge=Math.min(s.end,g_end);
      if(ge<=gs)return;
      let gx1=x(gs),gx2=x(ge),plus=g.strand!=='-',gy=plus?76:94,gw=Math.max(4,gx2-gx1);
      let head=Math.min(8,gw*0.4);
      let polyPoints=plus?`${gx1},${gy} ${gx2-head},${gy} ${gx2},${gy+7} ${gx2-head},${gy+14} ${gx1},${gy+14}`:`${gx1+head},${gy} ${gx2},${gy} ${gx2},${gy+14} ${gx1+head},${gy+14} ${gx1},${gy+7}`;
      let gPoly=E('polygon',{points:polyPoints,fill:'#32d399',opacity:'0.85',class:'gene-track','data-gene':g.symbol||g.feature_id||'gene',style:'cursor:pointer;transition:opacity .15s,filter .15s,stroke .15s;'});
      gPoly.onmouseenter=e=>{
        tip.style.display='block';tip.style.left=e.clientX+14+'px';tip.style.top=e.clientY+14+'px';
        tip.innerHTML=`<b>${esc(g.symbol||g.feature_id)}</b> (${esc(g.biotype||'gene')})<br>Strand: ${esc(g.strand)} • ${fmt(gs)}–${fmt(ge)} bp<br>Overlap: ${fmt(g.overlap_bp||(ge-gs))} bp<br><span style="color:#32d399;font-size:10px;">${isModal ? 'Click to view in NCBI Gene ↗' : 'Click card to view details'}</span>`;
        gPoly.style.opacity='1';
        gPoly.style.filter='drop-shadow(0 0 8px #32d399)';
        gPoly.style.stroke='#32d399';
        gPoly.style.strokeWidth='1px';
        highlightGene(g.symbol||g.feature_id,true);
      };
      gPoly.onmouseleave=()=>{
        tip.style.display='none';
        gPoly.style.opacity='0.85';
        gPoly.style.filter='none';
        gPoly.style.stroke='none';
        highlightGene(g.symbol||g.feature_id,false);
      };
      if (isModal) {
        gPoly.onclick=e=>{e.stopPropagation();if(g.ncbi_url)window.open(g.ncbi_url,'_blank');};
      }
      v.append(gPoly);
    });
  }

  let lblIsland=E('text',{x:115,y:47,'text-anchor':'end',fill:'#25d9f4','font-size':10,'font-weight':'600'});
  lblIsland.textContent='Islands (5′/3′)';
  v.append(lblIsland);

  let lblSeq=E('text',{x:115,y:67,'text-anchor':'end',fill:'#8fa5c8','font-size':10,'font-weight':'600'});
  lblSeq.textContent='SHaNE';
  v.append(lblSeq);

  let lblGene=E('text',{x:115,y:87,'text-anchor':'end',fill:hasGeneAnalysis?'#32d399':'#4a5c78','font-size':10,'font-weight':'600'});
  lblGene.textContent=hasGeneAnalysis?'Genes (+/-)':'Genes (N/A)';
  v.append(lblGene);

  return v;
}
function highlightGene(id,on){
  document.querySelectorAll(`.genechip`).forEach(el=>{
    if(el.textContent.trim()===id){
      el.style.borderColor = on ? 'var(--green)' : '#26715f';
      el.style.background = on ? '#1b4d48' : '#123b38';
      el.style.boxShadow = on ? '0 0 10px #32d39988' : 'none';
    }
  });
  document.querySelectorAll(`polygon[data-gene="${id}"], rect[data-gene="${id}"], path[data-gene="${id}"]`).forEach(el=>{
    el.style.opacity = on ? '1' : '0.85';
    el.style.filter = on ? 'drop-shadow(0 0 8px #32d399)' : 'none';
    el.style.stroke = on ? '#32d399' : 'none';
    el.style.strokeWidth = on ? '1px' : '0';
  });
}
function toggleView(){
  view=view==='chromosomes'?'shanes':'chromosomes';
  let isShanes=view==='shanes';
  viewToggle.textContent=isShanes?'Chromosomes':'SHaNEs';
  viewToggle.title=isShanes?'Switch to Chromosome-level overview tracks':'Switch to individual SHaNE cards view';
  viewToggle.classList.toggle('active',isShanes);
  setSorter();
  apply();
}

function openMethodsModal(sec){
  methodsModal.classList.add('open');
  if(sec){
    let target = document.getElementById('method-' + sec);
    if(target){
      setTimeout(()=>{ target.scrollIntoView({behavior:'smooth', block:'start'}); }, 50);
    }
  } else {
    methodsModal.scrollTop = 0;
  }
}
function closeMethodsModal(){methodsModal.classList.remove('open')}

function launchLegacyTerminal(){
  let targetUrl = (window.location.origin && window.location.origin.startsWith('http'))
    ? '/legacy.html'
    : 'http://127.0.0.1:8765/legacy.html';
  window.open(targetUrl, '_blank');
}

function updateModalNav(s){
  let curList=filtered();
  let curIdx=curList.findIndex(x=>x.stable_id===(s?.stable_id||modal.dataset.sid));
  let prevBtn=document.getElementById('modalPrev');
  let nextBtn=document.getElementById('modalNext');
  if(prevBtn)prevBtn.disabled=curIdx<=0;
  if(nextBtn)nextBtn.disabled=curIdx<0||curIdx>=curList.length-1;
}

function navigateSHaNE(dir){
  let curList=filtered();
  let curIdx=curList.findIndex(x=>x.stable_id===modal.dataset.sid);
  if(curIdx<0)curIdx=0;
  let nextIdx=curIdx+dir;
  if(nextIdx>=0&&nextIdx<curList.length){
    openSHaNE(curList[nextIdx]);
  }
}

window.addEventListener('keydown',e=>{
  if(typeof methodsModal!=='undefined'&&methodsModal&&methodsModal.classList.contains('open')){
    if(e.key==='Escape'){closeMethodsModal();}
  } else if(typeof modal!=='undefined'&&modal&&modal.classList.contains('open')){
    if(e.key==='ArrowLeft'){e.preventDefault();navigateSHaNE(-1);}
    else if(e.key==='ArrowRight'){e.preventDefault();navigateSHaNE(1);}
    else if(e.key==='Escape'){closeModal();}
  }
});

function openSHaNE(s){
  if(typeof methodsModal!=='undefined'&&methodsModal)closeMethodsModal();
  modal.classList.add('open');
  modal.scrollTop=0;
  modalTitle.textContent=s.systematic_name;
  modalSub.innerHTML=`${esc(s.sequence_accession)} <span>│</span> ${fmt(s.start)}–${fmt(s.end)} bp <span>│</span> ${esc(s.chromosome_group)}`;
  updateModalNav(s);

  let topName=(s.branching_topology||(s.details&&s.details.branching_topology)||'unbranched').replaceAll('_',' ');
  let bCount=(s.branches||(s.details&&s.details.branches)||[]).length||s.branch_count||0;
  let defs=[
    ['Genomic Length',fmt(s.length_bp)+' bp','Genomic span from start to end coordinate: End - Start (' + fmt(s.length_bp) + ' bp).'],
    ['With Voids',fmt(s.length_with_voids_bp||s.length_bp)+' bp','Alignment span including dynamic void gaps (.): Genomic length + Total voids (' + fmt(s.length_with_voids_bp||s.length_bp) + ' bp).'],
    ['Score',Number(s.score).toFixed(4),'Maximized Watson-Crick score: Matches / Total duplex length (' + (Number(s.score)*100).toFixed(2) + '%). Click Methods for details.'],
    ['Topology',topName,'Secondary structural branching topology classification based on detected internal hairpin stems.'],
    ['Islands',s.island_count,'Number of discrete complementary island stem pairs detected between opposing 5′ and 3′ arms.'],
    ['Branches',bCount,'Number of internal self-complementary stem-loop hairpin branches formed within interisland loops or arms.'],
    ['Total island length',fmt(s.total_island_length_bp)+' bp','Sum of all individual 5′ island stem arm lengths in base pairs.'],
    ['GC',Number(s.gc_content_percent).toFixed(2)+'%','GC percentage: (G + C) / (A + C + G + T) × 100% of sequenced bases, excluding dead N bases.']
  ];
  panorama.innerHTML=defs.map(d=>`<div class="metric"><b>${d[1]}</b>${d[0]}<span class="help">${d[2]}</span></div>`).join('');
  let d=s.details||{},bList=s.branches||d.branches||[];
  let loopSeq = getCentralLoopSeq(s);
  let clData=(d&&d.central_loop_analysis)||(s&&s.central_loop_analysis);
  let containsN = /[Nn]/.test(loopSeq) || (clData && (clData.has_n_bases || clData.contains_null_bases || (clData.loop_seq && /[Nn]/.test(clData.loop_seq))));
  let tooShort = !loopSeq || loopSeq.length < 6;
  let hasCL = !!(clData && clData.has_central_loop && !containsN && !tooShort);

  let loopDisabledReason = '';
  if (!hasCL) {
    if (containsN) {
      loopDisabledReason = 'Central loop analysis is deactivated: central loop contains undetermined/null (N) bases.';
    } else if (tooShort) {
      loopDisabledReason = 'Central loop analysis is deactivated: loop sequence is too short (< 6 bp) or islands directly abut.';
    } else {
      loopDisabledReason = 'Central loop analysis is deactivated: no central loop detected for this structure.';
    }
  }

  let tabsDef=[
    ['genes','Genes',hasGeneAnalysis,hasGeneAnalysis?'':'Gene annotations are not available in this library.'],
    ['context','Context sequence',!!d.context_sequence,d.context_sequence?'':'Context sequence is not available.'],
    ['folded','Folded structure',!!d.folded_alignment,d.folded_alignment?'':'Folded alignment data is not available.'],
    ['islands','Islands',true,''],
    ['branches',`Branches (${bList.length})`,true,''],
    ['loop','Central loop',hasCL,loopDisabledReason]
  ];
  tabs.innerHTML=tabsDef.map(([k,n,on,disTitle])=>`<button ${on?'':'disabled'} ${(!on&&disTitle)?`title="${esc(disTitle)}"`:''} onclick="showTab('${k}')" data-tab="${k}">${n}</button>`).join(' ')+` <a class="direct-ncbi" target="_blank" href="${s.ncbi_region_url}">NCBI ↗</a>`;
  modal.dataset.sid=s.stable_id;
  showTab(hasGeneAnalysis?'genes':'islands');
}

function centralLoopCardHTML(s, d){
  let loopSeq = getCentralLoopSeq(s);
  let loopData = (d && d.central_loop_analysis) || (s && s.central_loop_analysis);
  let hasN = /[Nn]/.test(loopSeq) || !loopSeq || (loopData && (loopData.has_n_bases || loopData.contains_null_bases || (loopData.loop_seq && /[Nn]/.test(loopData.loop_seq))));
  if (!loopData || !loopData.has_central_loop || hasN) return '';

  let isUnfolded = loopData.evolved_to_remain_unfolded;
  let badgeColor = isUnfolded ? '#32d399' : '#f5b942';
  let badgeBg = isUnfolded ? '#0b241e' : '#1b2238';
  let badgeBorder = isUnfolded ? '#236553' : '#374c72';
  return `
    <div class="central-loop-card" style="background:#091329;border:1px solid #233b66;border-radius:12px;padding:14px 18px;margin-top:14px;box-shadow:0 4px 18px rgba(0,0,0,0.3);text-align:left;clear:both;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
        <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
          <b style="font-size:13px;color:var(--ink);font-family:system-ui,sans-serif;">Central Loop Analysis (${fmt(loopData.loop_length_bp)} bp)</b>
          <span style="background:${badgeBg};color:${badgeColor};border:1px solid ${badgeBorder};padding:3px 10px;border-radius:99px;font-size:11px;font-weight:700;font-family:system-ui,sans-serif;">${isUnfolded ? '🧬 ' : ''}${esc(loopData.hypothesis_badge)}</span>
          <a class="methods-qmark" href="javascript:void(0)" onclick="openMethodsModal('loop')" title="Central Loop mathematical model: Expected random pairing vs optimized foldover. Click for scientific Methods.">?</a>
        </div>
        <div style="display:flex;gap:6px;font-size:11px;font-family:system-ui,sans-serif;">
          <span style="background:#132347;color:var(--ink);padding:2px 8px;border-radius:99px;border:1px solid #3b578c;" title="Loop GC percentage">GC: ${loopData.gc_content_percent}%</span>
          <span style="background:#132347;color:var(--ink);padding:2px 8px;border-radius:99px;border:1px solid #3b578c;" title="Spatial distribution across subwindows">Spread: ${esc(loopData.gc_spatial_uniformity)}</span>
        </div>
      </div>
      <div style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin-bottom:10px;font-size:12px;display:grid;">
        <div style="background:#050a18;padding:8px 12px;border-radius:8px;border:1px solid #182842;">
          <span style="color:var(--muted);display:block;font-size:11px;">Expected Random Pairing</span>
          <b style="color:#25d9f4;font-size:14px;">${loopData.expected_random_score_pct}%</b>
          <span style="color:#6b82a8;font-size:10px;display:block;">2 · (fA·fT + fG·fC) for ${loopData.gc_content_percent}% GC</span>
        </div>
        <div style="background:#050a18;padding:8px 12px;border-radius:8px;border:1px solid #182842;">
          <span style="color:var(--muted);display:block;font-size:11px;">Actual Direct Binding</span>
          <b style="color:${loopData.actual_direct_score_pct < loopData.expected_random_score_pct ? '#32d399' : '#ffffff'};font-size:14px;">${loopData.actual_direct_score_pct}%</b>
          <span style="color:#6b82a8;font-size:10px;display:block;">Direct un-gapped fold-over</span>
        </div>
        <div style="background:#050a18;padding:8px 12px;border-radius:8px;border:1px solid #182842;">
          <span style="color:var(--muted);display:block;font-size:11px;">Actual Optimized Binding</span>
          <b style="color:${loopData.actual_optimized_score_pct < loopData.expected_random_score_pct ? '#32d399' : '#f5b942'};font-size:14px;">${loopData.actual_optimized_score_pct}%</b>
          <span style="color:#6b82a8;font-size:10px;display:block;">DP-aligned with dynamic voids</span>
        </div>
      </div>
      <div style="font-size:11px;color:var(--muted);line-height:1.6;background:#050914;padding:8px 12px;border-radius:6px;border-left:3px solid ${badgeColor};">
        <b>Evolutionary Hypothesis:</b> ${esc(loopData.hypothesis_text)}
      </div>
    </div>
  `;
}

function showTab(k){
  let s=L.shanes.find(x=>x.stable_id===modal.dataset.sid)||L.shanes[0],d=s.details||{};
  document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('active',b.dataset.tab===k));
  if(k==='genes')tabBody.innerHTML=hasGeneAnalysis?(s.genes.length?`<div class="gene-cards">${s.genes.map(g=>`<article class="gene-card" data-gene="${esc(g.symbol||g.feature_id)}" onclick="window.open('${g.ncbi_url}','_blank')" onmouseenter="highlightGene('${esc(g.symbol||g.feature_id)}',true)" onmouseleave="highlightGene('${esc(g.symbol||g.feature_id)}',false)" title="Click to view in NCBI Gene ↗"><h3>${esc(g.symbol||g.feature_id)}</h3><div>${esc(g.biotype||'gene')} • strand ${esc(g.strand)}</div><div class="meta">${fmt(g.genomic_start)}–${fmt(g.genomic_end)}</div><p>${esc((g.relationship||'overlap').replaceAll('_',' '))}<br>Overlap: ${fmt(g.overlap_bp)} bp</p></article>`).join('')}</div>`:'<div class="no-data">No crossed gene.</div>'):'<div class="no-data">No gene annotations loaded in this library.</div>';
  if(k==='context')tabBody.innerHTML=contextHTML(s,d.context_sequence);
  if(k==='folded')tabBody.innerHTML=`
    <div class="folded-view-wrapper" style="max-width:980px;margin:0 auto;display:flex;flex-direction:column;gap:14px;">
      <div class="fold-guide-card" style="background:#091329;border:1px solid #233b66;border-radius:12px;padding:14px 18px;box-shadow:0 4px 18px rgba(0,0,0,0.3);text-align:left;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:gap:8px;">
          <div style="display:flex;align-items:center;gap:6px;">
            <b style="font-size:14px;color:var(--ink);">2D Watson-Crick Folded Alignment</b>
            <a class="methods-qmark" href="javascript:void(0)" onclick="openMethodsModal('duplex')" title="Dynamic void duplex scoring and alignment methodology. Click for Methods.">?</a>
          </div>
          <span style="background:#132347;color:var(--ink);padding:2px 10px;border-radius:99px;font-size:11px;border:1px solid #3b578c;">Score: ${(Number(s.score)*100).toFixed(1)}%</span>
        </div>
        <div style="font-size:12px;color:var(--muted);line-height:1.6;">
          <p style="margin:0 0 6px 0;">
            This 2D representation pairs the 5′ forward arm against the opposing reverse-complementary 3′ arm. Uppercase characters denote core island stems; lowercase characters represent interisland loop sequences. Vertical bars indicate Watson-Crick pairings (A-T, G-C).
          </p>
          <p style="margin:0;">
            <b>Dynamic Voids:</b> Phase-shift gaps inserted dynamically to account for loop length differences between opposing arms, maximizing total duplex complementarity across interisland intervals without crossing over.
          </p>
        </div>
      </div>
      <div class="alignbox" style="margin:0 auto;width:100%;text-align:center;box-shadow:0 6px 24px rgba(0,0,0,0.4);border-radius:12px;border:1px solid #1f3354;background:#030715;padding:18px;">
        ${colorAlignment(d.folded_alignment)}
      </div>
    </div>
  `;
  if(k==='islands')tabBody.innerHTML=islandsHTML(s,d);
  if(k==='branches')tabBody.innerHTML=branchesHTML(s,d);
  if(k==='loop')tabBody.innerHTML=`<div class="loop-view-wrapper" style="max-width:980px;margin:0 auto;">${centralLoopCardHTML(s, d)}</div>`;
}
function wrapFasta(seq,w=60){if(!seq)return '';let rows=[];for(let i=0;i<seq.length;i+=w)rows.push(seq.slice(i,i+w));return rows.join('\n')}
function colorLineBases(line){
  return [...line].map(c=>{
    if(/[ATat]/.test(c))return `<span class="base-at">${c}</span>`;
    if(/[GCgc]/.test(c))return `<span class="base-gc">${c}</span>`;
    if(/[Nn]/.test(c))return `<span class="base-n">${c}</span>`;
    if(c==='.')return `<span class="gap" style="color:#6b7280;">.</span>`;
    if(c==='|')return `<span style="color:#ffffff;font-weight:700;">|</span>`;
    return esc(c);
  }).join('');
}

function colorAlignment(t){
  if(!t)return '<div class="no-data">No alignment data available.</div>';
  let lines=t.split('\n'),out=[];
  for(let i=0;i<lines.length;){
    if(i+2<lines.length && /5['′]-3['′]/.test(lines[i]) && /3['′]-5['′]/.test(lines[i+2])){
      let l1=lines[i],l2=lines[i+1],l3=lines[i+2];
      let maxLen=Math.max(l1.length,l2.length,l3.length);
      l1=l1.padEnd(maxLen,' ');
      l2=l2.padEnd(maxLen,' ');
      l3=l3.padEnd(maxLen,' ');
      let pairContent = l2.includes('|') ? colorLineBases(l2) : '<span style="visibility:hidden;font-weight:700;">|</span>';
      out.push(`<div class="fold-block" style="display:block;width:max-content;margin:0 auto 1.55em;clear:both;"><div class="fold-line" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;">${colorLineBases(l1)}</div><div class="fold-line pair" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;color:#ffffff;">${pairContent}</div><div class="fold-line" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;">${colorLineBases(l3)}</div></div>`);
      i+=3;
    }else{
      if(lines[i].trim()){
        out.push(`<div class="fold-line" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;">${colorLineBases(lines[i])}</div>`);
      }
      i++;
    }
  }
  return out.join('');
}

function colorAllWhite(line){
  return [...line].map(c=>{
    if(/[Nn]/.test(c)) return `<span class="base-n" style="color:#8396b5;font-weight:600;">${c}</span>`;
    if(c==='.') return `<span class="gap" style="color:#6b7280;">.</span>`;
    if(c==='|') return `<span style="color:#ffffff;font-weight:700;">|</span>`;
    if(/[A-Za-z]/.test(c)) return `<span style="color:#ffffff;">${c}</span>`;
    return esc(c);
  }).join('');
}

function colorBranchLine(line, isTop, bList){
  let m = line.match(/^(\s*(?:5|3)['′]-?(?:3|5)['′]?\s{1,6})(.*?)(\s{2,}\d+[\d,]*\s*)$/);
  if (!m) {
    return colorAllWhite(line);
  }
  let prefix = m[1], seqPart = m[2], suffix = m[3];
  let anchorCoord = parseInt(suffix.replace(/[^\d]/g, ''), 10);
  let nonGapLen = seqPart.replace(/[\.\s]/g, '').length;
  let startCoord = isTop ? (anchorCoord - nonGapLen) : anchorCoord;
  let curCoord = startCoord;
  let outSeq = '';

  for (let i = 0; i < seqPart.length; i++) {
    let c = seqPart[i];
    if (c === '.') {
      outSeq += `<span class="gap" style="color:#6b7280;">.</span>`;
    } else if (/[Nn]/.test(c)) {
      if (isTop) curCoord++; else curCoord--;
      outSeq += `<span class="base-n" style="color:#8396b5;font-weight:600;">${c}</span>`;
    } else if (/[A-Za-z]/.test(c)) {
      let pos = isTop ? (curCoord + 1) : curCoord;
      if (isTop) curCoord++;
      else curCoord--;

      let bIndex = -1;
      let hitBranch = bList.find((b, idx) => {
        let gs = b.genomic_arm5_start !== undefined ? b.genomic_arm5_start : (b.genomic_start !== undefined ? b.genomic_start : (b.s1 !== undefined ? b.s1 : -1));
        let ge = b.genomic_arm3_end !== undefined ? b.genomic_arm3_end : (b.genomic_end !== undefined ? b.genomic_end : (b.e2 !== undefined ? b.e2 : -1));
        if (gs >= 0 && ge >= 0 && pos >= gs && pos <= ge) {
          bIndex = idx + 1;
          return true;
        }
        return false;
      });

      if (hitBranch && bIndex > 0) {
        let s1_s = hitBranch.genomic_arm5_start !== undefined ? hitBranch.genomic_arm5_start : hitBranch.s1;
        let s1_e = hitBranch.genomic_arm5_end !== undefined ? hitBranch.genomic_arm5_end : hitBranch.e1;
        let s2_s = hitBranch.genomic_arm3_start !== undefined ? hitBranch.genomic_arm3_start : hitBranch.s2;
        let s2_e = hitBranch.genomic_arm3_end !== undefined ? hitBranch.genomic_arm3_end : hitBranch.e2;
        let isStem = (pos >= s1_s && pos <= s1_e) || (pos >= s2_s && pos <= s2_e);
        if (isStem) {
          let charOut = c.toUpperCase();
          outSeq += `<span class="branch-tag-${bIndex} branch-link" onmouseenter="highlightBranch(${bIndex},true)" onmouseleave="highlightBranch(${bIndex},false)" onclick="toggleInlineBranch(${bIndex},this)" title="Click to open Branch ${bIndex} entry here [${esc(hitBranch.location||'Loop')}]" style="color:#f5b942;font-weight:700;">${charOut}</span>`;
        } else {
          let charOut = c.toLowerCase();
          outSeq += `<span class="branch-tag-${bIndex} branch-link" onmouseenter="highlightBranch(${bIndex},true)" onmouseleave="highlightBranch(${bIndex},false)" onclick="toggleInlineBranch(${bIndex},this)" title="Click to open Branch ${bIndex} entry here [${esc(hitBranch.location||'Loop')}]" style="color:#f5b942;font-weight:400;">${charOut}</span>`;
        }
      } else {
        outSeq += `<span style="color:#ffffff;">${c}</span>`;
      }
    } else {
      outSeq += esc(c);
    }
  }

  return `<span class="coord" style="color:#8fa5c8;">${esc(prefix)}</span>${outSeq}<span class="coord" style="color:#8fa5c8;">${esc(suffix)}</span>`;
}

function renderFoldedWithYellowBranches(t, s){
  if(!t)return '<div class="no-data">No alignment data available.</div>';
  let bList = (s && s.branches) || (s && s.details && s.details.branches) || [];
  let lines = t.split('\n'), out = [];
  for(let i=0; i<lines.length; ){
    if(i+2<lines.length && /5['′]-3['′]/.test(lines[i]) && /3['′]-5['′]/.test(lines[i+2])){
      let l1 = lines[i], l2 = lines[i+1], l3 = lines[i+2];
      let maxLen = Math.max(l1.length, l2.length, l3.length);
      l1 = l1.padEnd(maxLen,' '); l2 = l2.padEnd(maxLen,' '); l3 = l3.padEnd(maxLen,' ');
      let pairContent = l2.includes('|') ? colorAllWhite(l2) : '<span style="visibility:hidden;font-weight:700;">|</span>';
      out.push(`<div class="fold-block" style="display:block;width:max-content;margin:0 auto 1.55em;clear:both;"><div class="fold-line" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;">${colorBranchLine(l1, true, bList)}</div><div class="fold-line pair" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;color:#ffffff;">${pairContent}</div><div class="fold-line" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;">${colorBranchLine(l3, false, bList)}</div></div>`);
      i += 3;
    } else {
      if(lines[i].trim()){ out.push(`<div class="fold-line" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;">${colorAllWhite(lines[i])}</div>`); }
      i++;
    }
  }
  return out.join('');
}

function highlightBranch(idx, active){
  document.querySelectorAll('.branch-tag-' + idx).forEach(el => {
    if (active) {
      el.classList.add('active-branch');
    } else {
      el.classList.remove('active-branch');
    }
  });
}

function closeInlineBranch(onDone){
  let drawers = document.querySelectorAll('.inline-branch-drawer:not(.closing)');
  if(!drawers.length){
    if(typeof onDone === 'function') onDone();
    return;
  }
  let remaining = drawers.length;
  drawers.forEach(el => {
    el.classList.add('closing');
    el.style.maxHeight = el.scrollHeight + 'px';
    requestAnimationFrame(() => {
      el.style.maxHeight = '0px';
      el.style.opacity = '0';
      el.style.paddingTop = '0px';
      el.style.paddingBottom = '0px';
      el.style.marginTop = '0px';
      el.style.marginBottom = '0px';
      el.style.transform = 'translateY(-8px) scale(0.98)';
    });
    setTimeout(() => {
      el.remove();
      remaining--;
      if(remaining === 0 && typeof onDone === 'function') onDone();
    }, 260);
  });
}

function formatBranchSeqWrapped(arm5, loop, arm3, w = 60) {
  let full = arm5 + loop + arm3;
  let len5 = arm5.length, lenL = loop.length;
  let rows = [];
  for (let i = 0; i < full.length; i += w) {
    let chunk = full.slice(i, i + w);
    let chunkHtml = '';
    for (let j = 0; j < chunk.length; j++) {
      let idx = i + j;
      let c = chunk[j];
      let isLoop = idx >= len5 && idx < (len5 + lenL);
      if (isLoop) {
        chunkHtml += `<span style="color:#f5b942;font-weight:400;">${c.toLowerCase()}</span>`;
      } else {
        chunkHtml += `<b style="color:#f5b942;font-weight:700;">${c.toUpperCase()}</b>`;
      }
    }
    rows.push(chunkHtml);
  }
  return rows.join('\n');
}

function buildBranchDuplex(arm5, arm3_rev, loop, g_s1, g_e1, g_s2, g_e2, w = 60) {
  let L = loop ? loop.length : 0;
  let mid = Math.ceil(L / 2);
  let topLoop = L > 0 ? loop.slice(0, mid).toLowerCase() : '';
  let botLoop = L > 0 ? loop.slice(mid).toLowerCase() : '';
  let botLoopRev = [...botLoop].reverse().join('');
  
  let topSeq = arm5 + topLoop;
  let botSeq = arm3_rev + botLoopRev;
  
  let maxL = Math.max(topSeq.length, botSeq.length);
  topSeq = topSeq.padEnd(maxL, ' ');
  botSeq = botSeq.padEnd(maxL, ' ');
  
  let bondsFull = '';
  for (let j = 0; j < maxL; j++) {
    let c1 = topSeq[j], c2 = botSeq[j];
    let p = (c1 + c2).toUpperCase();
    bondsFull += (p === 'AT' || p === 'TA' || p === 'GC' || p === 'CG') ? '|' : ' ';
  }
  
  let maxCoordLen = Math.max(fmt(g_s1).length, fmt(g_e2).length);
  let prefixPad = 4 + maxCoordLen + 2;
  
  let rows = [];
  let curTop = g_s1, curBot = g_e2;
  for (let offset = 0; offset < maxL; offset += w) {
    let t_sub = topSeq.slice(offset, offset + w);
    let m_sub = bondsFull.slice(offset, offset + w);
    let b_sub = botSeq.slice(offset, offset + w);
    let nonGapTop = t_sub.replace(/[\.\s]/g, '').length;
    let nonGapBot = b_sub.replace(/[\.\s]/g, '').length;
    let blockWidth = maxL > w ? w : maxL;
    t_sub = t_sub.padEnd(blockWidth, ' ');
    m_sub = m_sub.padEnd(blockWidth, ' ');
    b_sub = b_sub.padEnd(blockWidth, ' ');
    
    let topPref = `5'  ${fmt(curTop).padStart(maxCoordLen, ' ')}  `;
    let midPref = ''.padStart(prefixPad, ' ');
    let botPref = `3'  ${fmt(curBot).padStart(maxCoordLen, ' ')}  `;
    
    rows.push(`${topPref}${t_sub}\n${midPref}${m_sub}\n${botPref}${b_sub}`);
    curTop += nonGapTop;
    curBot -= nonGapBot;
  }
  return rows.join('\n\n');
}

function colorBranchDuplexLine(line){
  let m = line.match(/^(\s*(?:5|3)['′]\s{2}[\d,\s]+\s{2})(.*)$/);
  if (!m) {
    let mMid = line.match(/^(\s{6,})(.*)$/);
    if (mMid) {
      let pref = mMid[1], bonds = mMid[2];
      return `<span class="coord" style="color:#8fa5c8;">${esc(pref)}</span>${colorAllWhite(bonds)}`;
    }
    return colorAllWhite(line);
  }
  let prefix = m[1], seqPart = m[2];
  let seqHtml = [...seqPart].map(c => {
    if(/[Nn]/.test(c)) return `<span class="base-n" style="color:#8396b5;font-weight:600;">${c}</span>`;
    if(c==='.') return `<span class="gap" style="color:#6b7280;">.</span>`;
    if(c==='|') return `<span style="color:#ffffff;font-weight:700;">|</span>`;
    if(/[A-Za-z]/.test(c)) return `<span style="color:#ffffff;">${c}</span>`;
    return esc(c);
  }).join('');
  return `<span class="coord" style="color:#8fa5c8;">${esc(prefix)}</span>${seqHtml}`;
}

function renderBranchAlignmentWhite(t){
  if(!t) return '<div class="no-data">No alignment data.</div>';
  let lines = t.split('\n'), out = [];
  for(let i = 0; i < lines.length; ){
    if(i + 2 < lines.length && /5['′]/.test(lines[i]) && /3['′]/.test(lines[i+2])){
      let l1 = lines[i], l2 = lines[i+1], l3 = lines[i+2];
      let maxL = Math.max(l1.length, l2.length, l3.length);
      l1 = l1.padEnd(maxL, ' '); l2 = l2.padEnd(maxL, ' '); l3 = l3.padEnd(maxL, ' ');
      let pairContent = l2.includes('|') ? colorBranchDuplexLine(l2) : '<span style="visibility:hidden;font-weight:700;">|</span>';
      out.push(`<div class="fold-block" style="display:block;margin:0 0 1.55em 0;clear:both;text-align:left;"><div class="fold-line" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;">${colorBranchDuplexLine(l1)}</div><div class="fold-line pair" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;color:#ffffff;">${pairContent}</div><div class="fold-line" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;">${colorBranchDuplexLine(l3)}</div></div>`);
      i += 3;
    } else {
      if(lines[i].trim()){
        out.push(`<div class="fold-line" style="font:13px Consolas,monospace;line-height:1.45;min-height:1.45em;margin:0;padding:0;white-space:pre;">${colorBranchDuplexLine(lines[i])}</div>`);
      }
      i++;
    }
  }
  return `<div class="duplex-center-wrap" style="display:inline-block;text-align:left;margin:0 auto;">${out.join('')}</div>`;
}

function toggleInlineBranch(idx, el){
  let foldBlock = el.closest('.fold-block') || el.closest('.alignbox') || el;
  let existing = document.querySelector(`.inline-branch-drawer[data-branch-idx="${idx}"]`);
  if (existing) {
    closeInlineBranch();
    highlightBranch(idx, false);
    return;
  }

  closeInlineBranch(() => {
    let s = L.shanes.find(x => x.stable_id === modal.dataset.sid) || L.shanes[0];
    let bList = (s && s.branches) || (s && s.details && s.details.branches) || [];
    let b = bList[idx - 1];
    if (!b) return;

    let g_s1 = b.genomic_arm5_start !== undefined ? b.genomic_arm5_start : (b.genomic_start || b.s1);
    let g_e1 = b.genomic_arm5_end !== undefined ? b.genomic_arm5_end : b.e1;
    let g_s2 = b.genomic_arm3_start !== undefined ? b.genomic_arm3_start : b.s2;
    let g_e2 = b.genomic_arm3_end !== undefined ? b.genomic_arm3_end : (b.genomic_end || b.e2);
    let arm5 = (b.arm5 || '').toUpperCase(), arm3 = (b.arm3 || '').toUpperCase(), arm3_rev = [...arm3].reverse().join('');
    let loop = (b.loop_seq || '').toLowerCase();
    let total_len = b.total_branch_length_bp || (g_e2 - g_s1) || (arm5.length + loop.length + arm3.length);
    let slen = b.stem_length || arm5.length, llen = b.loop_length || loop.length, score = b.score !== undefined ? Number(b.score).toFixed(2) : '1.00';

    let drawer = document.createElement('div');
    drawer.className = 'inline-branch-drawer';
    drawer.dataset.branchIdx = String(idx);
    drawer.style.cssText = 'display:block;margin:12px auto 22px;max-width:880px;background:#09142b;border:1.5px solid #f5b942;border-radius:12px;padding:16px 20px;box-shadow:0 8px 32px rgba(0,0,0,0.6), 0 0 20px rgba(245,185,66,0.28);text-align:left;clear:both;overflow:hidden;opacity:0;transform:translateY(-8px) scale(0.98);max-height:0;transition:opacity .24s cubic-bezier(.2,.8,.2,1),transform .24s cubic-bezier(.2,.8,.2,1),max-height .28s cubic-bezier(.2,.8,.2,1),padding .24s cubic-bezier(.2,.8,.2,1),margin .24s cubic-bezier(.2,.8,.2,1);';

    drawer.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid #1c2e4a;flex-wrap:wrap;gap:8px;">
        <b style="color:#f5b942;font-size:13px;font-family:system-ui,sans-serif;">Branch ${idx} [${esc(b.location||'Loop')}]: ${fmt(g_s1)}–${fmt(g_e2)} (${total_len} bp)</b>
        <div style="display:flex;align-items:center;gap:6px;font-family:system-ui,sans-serif;font-size:11px;">
          <span style="background:#132347;color:#f5b942;border:1px solid #f5b94288;padding:2px 8px;border-radius:99px;">Stem: ${slen} bp</span>
          <span style="background:#132347;color:#f5b942;border:1px solid #f5b94288;padding:2px 8px;border-radius:99px;">Intersequence: ${llen} bp</span>
          <span style="background:#132347;color:#ffffff;border:1px solid #3b578c;padding:2px 8px;border-radius:99px;">Score: ${score}</span>
          <button onclick="closeInlineBranch()" style="background:#142346;border:1px solid #41577e;color:#fff;border-radius:6px;padding:3px 9px;cursor:pointer;font-size:12px;margin-left:6px;line-height:1;transition:border-color .15s,background .15s;" title="Close branch window">✕</button>
        </div>
      </div>
      <div style="margin:8px 0;font-family:Consolas,monospace;font-size:12px;background:#040714;padding:10px 14px;border-radius:6px;border:1px solid #152238;line-height:1.55;text-align:left;">
        <div style="color:var(--muted);margin-bottom:6px;font-family:system-ui,sans-serif;font-size:11px;text-align:left;">Sequence (1st to 2nd stem, 60 bases per row):</div>
        <div style="font-family:Consolas,monospace;white-space:pre;font-size:12px;line-height:1.55;text-align:center;">${formatBranchSeqWrapped(arm5, loop, arm3, 60)}</div>
      </div>
      <div style="margin:12px auto 4px;width:100%;text-align:center;">
        ${renderBranchAlignmentWhite(buildBranchDuplex(arm5, arm3_rev, loop, g_s1, g_e1, g_s2, g_e2, 60))}
      </div>
    `;

    foldBlock.insertAdjacentElement('afterend', drawer);
    requestAnimationFrame(() => {
      drawer.style.maxHeight = '650px';
      drawer.style.opacity = '1';
      drawer.style.transform = 'translateY(0) scale(1)';
    });
    highlightBranch(idx, true);
  });
}

function scrollToBranch(idx){
  let el = document.getElementById('branch-card-' + idx);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    el.style.transition = 'box-shadow 0.3s, background 0.3s';
    let oldBg = el.style.background || '';
    el.style.background = '#152b4d';
    el.style.boxShadow = '0 0 24px rgba(245, 185, 66, 0.45)';
    setTimeout(() => {
      el.style.background = oldBg;
      el.style.boxShadow = 'none';
    }, 1400);
  }
}

function islandsHTML(arg1, arg2){
  let sid = modal.dataset.sid;
  let s = L.shanes.find(x => x.stable_id === sid) || (typeof arg1 === 'object' && arg1 ? arg1 : L.shanes[0]);
  if (!s) return '<div class="no-data">No SHaNE selected.</div>';
  let d = (s && s.details) || (typeof arg2 === 'object' && arg2 ? arg2 : {});
  let islList = (s && s.islands) || [];
  let stList = s.island_stats || getIslandStats(s);
  let islandSections = [];

  if (d && d.island_alignment) {
    let sections = d.island_alignment.split(/(?=Island\s+\d+:)/).filter(x => x.trim() && x.includes('Island'));
    sections.forEach((sec, idx) => {
      let lines = sec.trim().split('\n').filter(l => l.trim());
      let m = lines[0].match(/Island\s+(\d+):\s*(\d+):(\d+)\s+vs\s+(\d+):(\d+)/);
      let islIdx = m ? m[1] : (idx + 1);
      let s5_start = m ? Number(m[2]) : (islList[idx]?.s_start || 0);
      let s5_end = m ? Number(m[3]) : (islList[idx]?.s_end || 0);
      let s3_start = m ? Number(m[4]) : (islList[idx]?.h_start || 0);
      let s3_end = m ? Number(m[5]) : (islList[idx]?.h_end || 0);
      let len5 = s5_end - s5_start, len3 = s3_end - s3_start;
      let isl_len = Math.max(len5, len3);

      let l5_line = lines.find(l => /^5['′]/.test(l)) || '';
      let l5 = l5_line.replace(/^5['′]?\s*[-–—]?\s*(?:3['′]?)?\s*:?\s*/i, '').trim();
      let l3_line = lines.find(l => /^3['′]/.test(l)) || '';
      let l3 = l3_line.replace(/^3['′]?\s*[-–—]?\s*(?:5['′]?)?\s*:?\s*/i, '').trim();

      let maxL = Math.max(l5.length, l3.length);
      let topFull = l5.padEnd(maxL, ' '), botFull = l3.padEnd(maxL, ' ');
      let bondsFull = '';
      for (let j = 0; j < maxL; j++) {
        let p = (topFull[j] + botFull[j]).toUpperCase();
        bondsFull += (p === 'AT' || p === 'TA' || p === 'GC' || p === 'CG') ? '|' : ' ';
      }

      let w = 60;
      let rows = [];
      let curTop = s5_start, curBot = s3_end;
      for (let offset = 0; offset < maxL; offset += w) {
        let t_sub = topFull.slice(offset, offset + w);
        let m_sub = bondsFull.slice(offset, offset + w);
        let b_sub = botFull.slice(offset, offset + w);
        let nonGapTop = t_sub.replace(/[\.\s]/g, '').length;
        let nonGapBot = b_sub.replace(/[\.\s]/g, '').length;
        let endTop = curTop + nonGapTop;
        let endBot = curBot - nonGapBot;
        rows.push(`5'-3'  ${t_sub}  ${fmt(endTop)}\n       ${m_sub}\n3'-5'  ${b_sub}  ${fmt(curBot)}`);
        curTop = endTop;
        curBot = endBot;
      }
      let body = rows.join('\n\n');

      let st = stList[idx] || { score: (islList[idx]?.score || s.score || 1.0) };
      let islScore = st.score !== undefined ? st.score : (islList[idx]?.calculated_score || s.score || 1.0);
      let th = calcIslandThermo(l5, l3);
      let thermoBadges = `
        <span style="color:#32d399;font-size:11px;font-weight:600;background:#0b241e;padding:3px 10px;border-radius:99px;border:1px solid #236553;font-family:system-ui,sans-serif;" title="Nearest-Neighbor Duplex Binding Free Energy at 37°C (50 mM Na+): ΔG° = ΔH° - TΔS° (SantaLucia 1998)">ΔG°₃₇: ${th.delta_g_37_kcal} kcal/mol</span>
        <span style="color:#25d9f4;font-size:11px;font-weight:600;background:#0d2338;padding:3px 10px;border-radius:99px;border:1px solid #215473;font-family:system-ui,sans-serif;" title="Predicted Duplex Melting Temperature (Tm) at 50 mM [Na+] (SantaLucia 1998 / Owczarzy 2004)">Tm: ${th.tm_celsius}°C</span>
        <a class="methods-qmark" href="javascript:void(0)" onclick="openMethodsModal('thermo')" title="Thermodynamic calculations based on SantaLucia (1998) unified nearest-neighbor DNA parameters with salt correction. Click for Methods.">?</a>
      `;
      islandSections.push(`
        <div class="island-section" style="width:100%;max-width:980px;margin:0 auto 28px;text-align:left;">
          <div style="text-align:left;font-size:14px;font-weight:700;color:var(--ink);margin-bottom:6px;font-family:system-ui,sans-serif;">
            Island ${islIdx}: 5′ (${fmt(s5_start)}–${fmt(s5_end)}) vs 3′ (${fmt(s3_start)}–${fmt(s3_end)})
          </div>
          <div style="display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap;margin:10px 0 16px;text-align:center;">
            <span style="color:#25d9f4;font-size:11px;font-weight:600;background:#0d2338;padding:3px 10px;border-radius:99px;border:1px solid #215473;font-family:system-ui,sans-serif;" title="Watson-Crick pairing score for this island stem">Score: ${islScore.toFixed(4)} (${(islScore*100).toFixed(1)}%)</span>
            ${thermoBadges}
            <span style="color:#ffffff;font-size:12px;font-weight:600;background:#132347;padding:3px 12px;border-radius:99px;border:1px solid #3b578c;font-family:system-ui,sans-serif;">Length: ${isl_len} bp</span>
          </div>
          <div class="alignbox" style="margin:0 auto;width:100%;text-align:center;box-shadow:0 6px 24px rgba(0,0,0,0.4);border-radius:12px;border:1px solid #1f3354;background:#030715;padding:18px;">
            ${colorAlignment(body)}
          </div>
        </div>
      `);
    });
  }

  return `
    <div class="islands-view-wrapper" style="max-width:980px;margin:0 auto;">
      ${islandSections.join('\n') || '<div class="no-data">No island data available.</div>'}
    </div>
  `;
}

function downloadBranchesTXT(sid){
  let s = L.shanes.find(x => x.stable_id === sid) || L.shanes[0];
  let d = s.details || {};
  let bList = s.branches || d.branches || [];
  let lines = [
    `# ==============================================================================`,
    `# GReGOrI SHaNE Branching Hairpin Architecture Report`,
    `# SHaNE: ${s.systematic_name} (${s.short_id}) [${s.qualification || 'SHaNE'}]`,
    `# Coordinates: ${s.sequence_accession}:${s.start}..${s.end} (${s.chromosome_group})`,
    `# Branching Topology: ${(s.branching_topology||'unbranched').replaceAll('_',' ')}`,
    `# Total Internal Branches: ${bList.length}`,
    `# ==============================================================================\n`
  ];
  if (!bList.length) {
    lines.push('No internal branching hairpin stems detected for this SHaNE.\n');
  } else {
    bList.forEach((b, i) => {
      let g_s1 = b.genomic_arm5_start !== undefined ? b.genomic_arm5_start : (b.genomic_start || b.s1);
      let g_e1 = b.genomic_arm5_end !== undefined ? b.genomic_arm5_end : b.e1;
      let g_s2 = b.genomic_arm3_start !== undefined ? b.genomic_arm3_start : b.s2;
      let g_e2 = b.genomic_arm3_end !== undefined ? b.genomic_arm3_end : (b.genomic_end || b.e2);
      let arm5 = (b.arm5 || '').toUpperCase(), arm3 = (b.arm3 || '').toUpperCase(), arm3_rev = [...arm3].reverse().join('');
      let loop = (b.loop_seq || '').toLowerCase();
      let full_branch_seq = b.branch_record_seq || b.full_hairpin_seq || (arm5 + loop + arm3);
      let total_len = b.total_branch_length_bp || (g_e2 - g_s1) || full_branch_seq.length;
      let slen = b.stem_length || arm5.length, llen = b.loop_length || loop.length, score = b.score !== undefined ? Number(b.score).toFixed(4) : '1.0000';
      
      lines.push(`>Branch_${i+1} [${b.location||'Loop'}] | Interval: ${g_s1}..${g_e2} (${total_len} bp) | 5' Stem: ${g_s1}..${g_e1} (${slen} bp) | 3' Stem: ${g_s2}..${g_e2} (${slen} bp) | Intersequence Loop: ${llen} bp | Score: ${score}`);
      lines.push(`Sequence (from first letter of 1st stem to last letter of 2nd stem, 60 bp per row):`);
      lines.push(wrapFasta(full_branch_seq, 60));
      lines.push(`3-Line Duplex Alignment (60 bp per block):`);
      lines.push(buildBranchDuplex(arm5, arm3_rev, loop, g_s1, g_e1, g_s2, g_e2, 60));
      lines.push('');
    });
  }
  save(lines.join('\n'),`${s.systematic_name}_branches.txt`,'text/plain');
}

function branchesHTML(arg1, arg2){
  let sid = modal.dataset.sid;
  let s = L.shanes.find(x => x.stable_id === sid) || (typeof arg1 === 'object' && arg1 ? arg1 : L.shanes[0]);
  if (!s) return '<div class="no-data">No SHaNE selected.</div>';
  let d = (s && s.details) || (typeof arg2 === 'object' && arg2 ? arg2 : {});
  let bList = (s && s.branches) || (d && d.branches) || [];

  let header = `
    <div class="fold-guide-card" style="background:#091329;border:1px solid #233b66;border-radius:12px;padding:14px 18px;margin-bottom:14px;box-shadow:0 4px 18px rgba(0,0,0,0.3);text-align:left;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:gap:8px;">
        <b style="font-size:14px;color:var(--ink);">Internal Branching Secondary Structure (${bList.length})</b>
        <div style="display:flex;gap:8px;">
          <button class="copybtn" onclick="downloadBranchesTXT('${s.stable_id}')">Download Branches (.txt)</button>
        </div>
      </div>
      <div style="font-size:12px;color:var(--muted);line-height:1.6;">
        <p style="margin:0 0 6px 0;">
          Below is the whole-SHaNE 2D folded duplex with internal branching hairpins highlighted in <b style="color:#f5b942;font-weight:700;">yellow</b>.
        </p>
        <p style="margin:0;">
          For each branch, the entire continuous sequence from the first letter of the 1st stem to the last letter of the 2nd stem is preserved and wrapped in 60 bases per row.
        </p>
      </div>
    </div>
  `;

  let foldedSection = d.folded_alignment ? `
    <div style="margin-bottom:18px;">
      <div style="font-size:13px;font-weight:600;color:var(--ink);margin-bottom:6px;text-align:left;">Whole-SHaNE Folded Duplex (Yellow Branch Annotations)</div>
      <div class="alignbox" style="margin:0 auto;width:100%;text-align:center;box-shadow:0 4px 18px rgba(0,0,0,0.4);border-radius:12px;border:1px solid #1f3354;">
        ${renderFoldedWithYellowBranches(d.folded_alignment, s)}
      </div>
    </div>
  ` : '';

  let branchSections = bList.map((b, idx) => {
    let g_s1 = b.genomic_arm5_start !== undefined ? b.genomic_arm5_start : (b.genomic_start || b.s1);
    let g_e1 = b.genomic_arm5_end !== undefined ? b.genomic_arm5_end : b.e1;
    let g_s2 = b.genomic_arm3_start !== undefined ? b.genomic_arm3_start : b.s2;
    let g_e2 = b.genomic_arm3_end !== undefined ? b.genomic_arm3_end : (b.genomic_end || b.e2);
    let arm5 = (b.arm5 || '').toUpperCase(), arm3 = (b.arm3 || '').toUpperCase(), arm3_rev = [...arm3].reverse().join('');
    let loop = (b.loop_seq || '').toLowerCase();
    let total_len = b.total_branch_length_bp || (g_e2 - g_s1) || (arm5.length + loop.length + arm3.length);
    let slen = b.stem_length || arm5.length, llen = b.loop_length || loop.length, score = b.score !== undefined ? Number(b.score).toFixed(2) : '1.00';

    return `
      <div id="branch-card-${idx+1}" class="branch-section" style="width:100%;border-radius:8px;padding:6px 0;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;padding:0 4px;flex-wrap:wrap;gap:8px;">
          <b style="color:var(--ink);font-size:13px;font-family:system-ui,sans-serif;">Branch ${idx+1} [${esc(b.location||'Loop')}]: ${fmt(g_s1)}–${fmt(g_e2)} (${total_len} bp)</b>
          <div style="display:flex;gap:6px;font-size:11px;font-family:system-ui,sans-serif;">
            <span style="background:#132347;color:#f5b942;border:1px solid #f5b94288;padding:2px 8px;border-radius:99px;">Stem: ${slen} bp</span>
            <span style="background:#132347;color:#f5b942;border:1px solid #f5b94288;padding:2px 8px;border-radius:99px;">Intersequence: ${llen} bp</span>
            <span style="background:#132347;color:#ffffff;border:1px solid #3b578c;padding:2px 8px;border-radius:99px;">Score: ${score}</span>
          </div>
        </div>
        <div style="margin:8px 0;font-family:Consolas,monospace;font-size:12px;background:#040714;padding:10px 14px;border-radius:6px;border:1px solid #152238;line-height:1.55;text-align:left;">
          <div style="color:var(--muted);margin-bottom:6px;font-family:system-ui,sans-serif;font-size:11px;text-align:left;">Sequence (1st to 2nd stem, 60 bases per row):</div>
          <div style="font-family:Consolas,monospace;white-space:pre;font-size:12px;line-height:1.55;text-align:center;">${formatBranchSeqWrapped(arm5, loop, arm3, 60)}</div>
        </div>
        <div style="margin:12px auto 0;width:100%;text-align:center;">
          ${renderBranchAlignmentWhite(buildBranchDuplex(arm5, arm3_rev, loop, g_s1, g_e1, g_s2, g_e2, 60))}
        </div>
      </div>
    `;
  });

  let branchDivider = '<div style="height:1px;background:#17263c;margin:24px auto;width:96%;"></div>';

  return `
    ${header}
    ${foldedSection}
    <div style="margin-top:18px;">
      <div style="font-size:13px;font-weight:600;color:var(--ink);margin-bottom:8px;text-align:left;">Branch Hairpin Details (${bList.length})</div>
      <div class="alignbox unified-branches-box" style="background:#040714!important;border:1px solid #1a2d4d;padding:22px!important;margin:0 auto;width:100%;text-align:center;box-shadow:0 6px 24px rgba(0,0,0,0.4);border-radius:14px;height:auto!important;max-height:none!important;overflow-y:visible!important;">
        ${branchSections.join(branchDivider) || '<div class="no-data">No internal branching hairpins detected.</div>'}
      </div>
    </div>
  `;
}

function contextHTML(s,seq){
  let sh=seq.search(/[A-Z]/),last=Math.max(...[...seq].map((c,i)=>/[A-Z]/.test(c)?i:-1)),w=60,rows=[];
  for(let i=0;i<seq.length;i+=w){
    let part=seq.slice(i,i+w),start=s.start-(sh>=0?sh:0)+i,end=start+part.length-1;
    let sp=[...part].map((c,j)=>{
      let p=i+j,cl=p>=sh&&p<=last?'shseq':'flank';
      if(/[Nn]/.test(c)) return `<span class="${cl} base-n">${esc(c)}</span>`;
      return `<span class="${cl}">${esc(c)}</span>`;
    }).join('');
    rows.push(`<div class="seqrow"><span class="ctx-orient">5′</span><span class="coord ctx-left">${fmt(start)}</span><span class="ctx-seq">${sp}</span><span class="coord ctx-right">${fmt(end)}</span><span class="ctx-orient">3′</span></div>`);
  }
  return `<div class="meta" style="margin-bottom:8px;">Lowercase: flanks • uppercase: SHaNE • 60 bases per row</div><div class="seqbox"><div class="context-grid">${rows.join('')}</div></div>`;
}
function closeModal(){modal.classList.remove('open')}
function gff(arr){let a=['##gff-version 3'];arr.forEach(s=>{let id=s.short_id;a.push(`${s.sequence_accession}\tGReGOrI\tbiological_region\t${s.start+1}\t${s.end}\t${s.score}\t.\t.\tID=${id};Name=${s.systematic_name};Island_Count=${s.island_count};Gene_Count=${s.gene_count}`);s.islands.forEach((x,i)=>{a.push(`${s.sequence_accession}\tGReGOrI\tinverted_repeat\t${x.s_start+1}\t${x.s_end}\t.\t+\t.\tID=${id}.I${i+1}.5p;Parent=${id};Arm=5prime`);a.push(`${s.sequence_accession}\tGReGOrI\tinverted_repeat\t${x.h_start+1}\t${x.h_end}\t.\t-\t.\tID=${id}.I${i+1}.3p;Parent=${id};Arm=3prime`)})});return a.join('\n')+'\n'}function save(t,n,type){let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type}));a.download=n;a.click()}function downloadGenomeGFF(){save(gff(L.shanes),'GReGOrI_genome_SHaNEs.gff3','text/plain')}function downloadChromGFF(){save(gff(L.shanes.filter(s=>s.chromosome_group===selectedGroup)),`GReGOrI_${selectedGroup}_SHaNEs.gff3`,'text/plain')}

function downloadTSV(){
  let cols=[
    'Short_ID','Systematic_Name','Chromosome_Group','Sequence_Accession',
    'Start','End','Genomic_Length_bp','Length_with_voids_bp','Voids_count',
    'Score','GC_percent','Branching_Topology','Branch_count',
    'Island_count','Total_island_length_bp','Island_Details',
    'Central_Loop_Length_bp','Central_Loop_GC_pct','Central_Loop_Uniformity',
    'Central_Loop_Expected_Random_WC_Prob','Central_Loop_Actual_Direct_Score',
    'Central_Loop_Actual_Optimized_Score','Central_Loop_Evolved_Unfolded',
    'Gene_count','Crossed_Genes'
  ];
  let rows=[cols.join('\t')];
  filtered().forEach(s=>{
    let d=s.details||{};
    let islStr=(s.islands||[]).map((isl,i)=>{
      let th=isl.calculated_thermo||isl.thermodynamics||{};
      let dg=th.delta_g_37_kcal!==undefined?th.delta_g_37_kcal:'NA';
      let tm=th.tm_celsius!==undefined?th.tm_celsius:'NA';
      let sc=isl.calculated_score!==undefined?isl.calculated_score:(isl.score||s.score||1.0);
      return `I${i+1}:[${isl.s_start}..${isl.s_end}_vs_${isl.h_start}..${isl.h_end}|score=${Number(sc).toFixed(4)}|dG=${dg}|Tm=${tm}]`;
    }).join(';');
    let cl=(d.central_loop_analysis)||(s.central_loop_analysis)||{};
    let geneStr=hasGeneAnalysis ? (s.genes||[]).map(g=>g.symbol||g.feature_id||'gene').join(';') : 'NA';
    rows.push([
      s.short_id||'',
      s.systematic_name||'',
      s.chromosome_group||'',
      s.sequence_accession||'',
      s.start,
      s.end,
      s.length_bp,
      s.length_with_voids_bp||s.length_bp,
      s.voids_count||0,
      s.score,
      s.gc_content_percent,
      s.branching_topology||'unbranched',
      s.branch_count||0,
      s.island_count,
      s.total_island_length_bp,
      islStr,
      cl.loop_length_bp||0,
      cl.gc_content_percent||0,
      cl.gc_spatial_uniformity||'NA',
      cl.expected_random_wc_prob||0,
      cl.actual_direct_score||0,
      cl.actual_optimized_score||0,
      cl.evolved_to_remain_unfolded?1:0,
      s.gene_count,
      geneStr
    ].join('\t'));
  });
  save(rows.join('\n'),'GReGOrI_filtered_SHaNEs.tsv','text/tab-separated-values');
}

function atlasSVG(arr,title,chromOnly=false){
  if(chromOnly && selectedGroup){
    let rec=L.sequence_records.find(r=>r.chromosome_group===selectedGroup&&r.display_name===selectedGroup)||L.sequence_records.find(r=>r.chromosome_group===selectedGroup);
    let hits=arr.filter(s=>s.chromosome_group===selectedGroup&&(rec?s.sequence_accession===rec.sequence_accession:true));
    let chromLen=rec?rec.length_bp:Math.max(...hits.map(s=>s.end),1);
    let maxL=Math.max(...hits.map(s=>s.length_bp||1),1),minL=Math.min(...hits.map(s=>s.length_bp||1),1);
    let W=1200, H=280;
    let hitLines=hits.map(s=>{
      let x=100+s.start/chromLen*1000;
      let norm=(s.length_bp-minL)/Math.max(1,maxL-minL);
      let halfH=14+norm*26;
      let color=(hasGeneAnalysis && s.gene_count>0)?'#32d399':'#ee3edc';
      return `<line x1="${x}" y1="${130-halfH}" x2="${x}" y2="${130+halfH}" stroke="${color}" stroke-width="4"/>`;
    }).join('');
    let ticks='';
    for(let i=0;i<=5;i++){
      let tx=100+i*200;
      ticks+=`<line x1="${tx}" y1="137" x2="${tx}" y2="147" stroke="#8592a8" stroke-width="1.5"/><text x="${tx}" y="165" text-anchor="middle" font-size="11" fill="#52627d">${short(chromLen*i/5)}</text>`;
    }
    let atlasLegend = hasGeneAnalysis ? `
      <g transform="translate(820,32)">
        <rect x="0" y="0" width="12" height="12" rx="2" fill="#32d399"/>
        <text x="18" y="10" font-size="11" fill="#52627d">Gene-crossing (${hits.filter(s=>s.gene_count>0).length})</text>
        <rect x="160" y="0" width="12" height="12" rx="2" fill="#ee3edc"/>
        <text x="178" y="10" font-size="11" fill="#52627d">Intergenic (${hits.filter(s=>s.gene_count===0).length})</text>
      </g>
    ` : `
      <g transform="translate(940,32)">
        <rect x="0" y="0" width="12" height="12" rx="2" fill="#ee3edc"/>
        <text x="18" y="10" font-size="11" fill="#52627d">SHaNEs (${hits.length})</text>
      </g>
    `;
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" style="background:#f7f9fd;font-family:Segoe UI,sans-serif;">
      <text x="40" y="38" font-size="22" font-weight="700" fill="#172139">${esc(title)}</text>
      <text x="40" y="62" font-size="12" fill="#52627d">GReGOrI Chromosome Atlas • ${hits.length} SHaNEs • ${rec?esc(rec.sequence_accession):''} (${short(chromLen)})</text>
      ${atlasLegend}
      <line x1="100" y1="130" x2="1100" y2="130" stroke="#8592a8" stroke-width="13" stroke-linecap="round"/>
      ${hitLines}
      ${ticks}
    </svg>`;
  }

  let groups=[...new Set(arr.map(s=>s.chromosome_group))];
  let recs=groups.map(g=>L.sequence_records.find(r=>r.chromosome_group===g&&r.display_name===g)||L.sequence_records.find(r=>r.chromosome_group===g)).filter(Boolean);
  let M=Math.max(...recs.map(r=>r.length_bp),1),H=130+recs.length*46;
  let rows=recs.map((r,i)=>{
    let y=100+i*46,w=r.length_bp/M*940,h=arr.filter(s=>s.chromosome_group===r.chromosome_group&&s.sequence_accession===r.sequence_accession);
    let maxL=Math.max(...h.map(s=>s.length_bp||1),1),minL=Math.min(...h.map(s=>s.length_bp||1),1);
    return `<text x="125" y="${y+5}" text-anchor="end" font-size="12" font-weight="600" fill="#30425f">${esc(r.chromosome_group)}</text>
      <line x1="150" y1="${y}" x2="${150+w}" y2="${y}" stroke="#8592a8" stroke-width="11" stroke-linecap="round"/>
      ${h.map(s=>{
        let norm=(s.length_bp-minL)/Math.max(1,maxL-minL);
        let halfH=6+norm*10;
        let color=(hasGeneAnalysis && s.gene_count>0)?'#32d399':'#ee3edc';
        return `<line x1="${150+s.start/r.length_bp*w}" y1="${y-halfH}" x2="${150+s.start/r.length_bp*w}" y2="${y+halfH}" stroke="${color}" stroke-width="3"/>`;
      }).join('')}
      <text x="1180" y="${y+5}" text-anchor="end" font-size="11" fill="#52627d">${short(r.length_bp)} • ${h.length}</text>`;
  }).join('');
  let genomeLegend = hasGeneAnalysis ? `
    <g transform="translate(820,32)">
      <rect x="0" y="0" width="12" height="12" rx="2" fill="#32d399"/>
      <text x="18" y="10" font-size="11" fill="#52627d">Gene-crossing</text>
      <rect x="130" y="0" width="12" height="12" rx="2" fill="#ee3edc"/>
      <text x="148" y="10" font-size="11" fill="#52627d">Intergenic</text>
    </g>
  ` : `
    <g transform="translate(940,32)">
      <rect x="0" y="0" width="12" height="12" rx="2" fill="#ee3edc"/>
      <text x="18" y="10" font-size="11" fill="#52627d">SHaNEs (${arr.length})</text>
    </g>
  `;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 ${H}" style="background:#f7f9fd;font-family:Segoe UI,sans-serif;">
    <text x="40" y="38" font-size="24" font-weight="700" fill="#172139">${esc(title)}</text>
    <text x="40" y="62" font-size="12" fill="#52627d">GReGOrI SHaNE Genome Atlas • ${arr.length} SHaNEs across ${recs.length} chromosomes</text>
    ${genomeLegend}
    ${rows}
  </svg>`;
}

function downloadAtlas(chrom=false){
  let arr=chrom?L.shanes.filter(s=>s.chromosome_group===selectedGroup):filtered();
  let title=chrom?`Chromosome ${selectedGroup} SHaNE atlas`:`${L.assemblies[0].species} SHaNE atlas`;
  save(atlasSVG(arr,title,chrom),`${title.replaceAll(' ','_')}.svg`,'image/svg+xml');
}

function resetFilters(){
  search.value='';
  if(document.getElementById('sizeMin')) sizeMin.value='10000';
  if(document.getElementById('sizeMax')) sizeMax.value='';
  scoreMin.value='0.80'; scoreMax.value='';
  islandMin.value='2'; islandMax.value='';
  geneMin.value='1'; geneMax.value='';
  gcMin.value='30'; gcMax.value='';
  globalFilterActive=false;
  if(sorter) sorter.selectedIndex=0;
  updateSortBtnLabel();
  let btn=document.getElementById('globalFilterBtn');
  if(btn) btn.classList.remove('active');
  activeStat=null; pointFilter=null; apply();
}
function bookmark(){location.hash=new URLSearchParams({q:search.value,smin:scoreMin.value,smax:scoreMax.value,imin:islandMin.value,imax:islandMax.value,gmin:geneMin.value,gmax:geneMax.value,gcmin:gcMin.value,gcmax:gcMax.value,group:selectedGroup||'',sort:sorter.value}).toString()}
function pickAssembly(){if(typeof assemblyFile!=='undefined'&&assemblyFile)assemblyFile.click()}
function loadAssembly(e){let f=e.target.files[0];if(!f)return;let r=new FileReader();r.onload=()=>{try{let n=JSON.parse(r.result);if(n.library_format!=='GReGOrI-SHaNE-Library')throw Error('Not a GReGOrI library');L=n;selectedGroup=null;selectedRecord=null;activeStat=null;pointFilter=null;hydrate();apply()}catch(x){alert(x.message)}};r.readAsText(f)}
function stepNumberInput(input, dir) {
  let step = parseFloat(input.step);
  if (isNaN(step) || step <= 0) {
    let id = (input.id || '').toLowerCase();
    if (id.includes('score') || id.includes('threshold') || id.includes('gc')) step = 0.01;
    else if (id.includes('lookahead') || id.includes('size')) step = 1000;
    else if (id.includes('step')) step = 100;
    else step = 1;
  }
  let val = parseFloat(input.value);
  if (isNaN(val)) {
    val = parseFloat(input.placeholder) || 0;
  }
  let decimals = (step.toString().split('.')[1] || '').length;
  let newVal = dir > 0 ? val + step : val - step;
  if (input.min !== '' && !isNaN(parseFloat(input.min))) newVal = Math.max(parseFloat(input.min), newVal);
  if (input.max !== '' && !isNaN(parseFloat(input.max))) newVal = Math.min(parseFloat(input.max), newVal);
  input.value = decimals > 0 ? newVal.toFixed(decimals) : String(Math.round(newVal));
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
}

document.addEventListener('pointerdown', function(e) {
  if (e.target.matches && e.target.matches('input[type="number"]') && !e.target.disabled) {
    const rect = e.target.getBoundingClientRect();
    const x = e.clientX - rect.left;
    if (x > rect.width - 20) {
      e.preventDefault();
      const y = e.clientY - rect.top;
      const dir = y < rect.height / 2 ? 1 : -1;
      stepNumberInput(e.target, dir);
    }
  }
});

document.addEventListener('mousemove', function(e) {
  if (e.target.matches && e.target.matches('input[type="number"]') && !e.target.disabled) {
    const rect = e.target.getBoundingClientRect();
    const x = e.clientX - rect.left;
    if (x > rect.width - 20) {
      e.target.style.cursor = 'pointer';
    } else {
      e.target.style.cursor = 'text';
    }
  }
});

init();</script></body></html>'''

def data_uri(p: Path) -> str:
    m, _ = mimetypes.guess_type(str(p))
    return f"data:{m or 'image/png'};base64,{base64.b64encode(p.read_bytes()).decode()}"

def build(source: str | Path, logo: str | Path | None = None, open_browser: bool = False) -> Path:
    p = Path(source).expanduser().resolve()
    lib_file = p if p.is_file() else p / "GReGOrI_SHaNE_library.json"
    if not lib_file.exists():
        raise FileNotFoundError(f"Library not found: {lib_file}")
    data = json.loads(lib_file.read_text(encoding="utf-8"))
    out = lib_file.parent / "browser_v4" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    
    logo_val = ""
    if logo and Path(logo).is_file():
        logo_val = data_uri(Path(logo))
    else:
        repo_root = Path(__file__).resolve().parents[2]
        assets_logo = repo_root / "frontend" / "assets" / "GReGOrI.png"
        if assets_logo.is_file():
            logo_val = data_uri(assets_logo)
            
    html = HTML.replace("__DATA__", json.dumps(data)).replace("__LOGO__", logo_val).replace("__METHODS_HTML__", get_methods_html())
    out.write_text(html, encoding="utf-8")
    print(f"Created: {out}")
    if open_browser:
        import webbrowser; webbrowser.open(out.as_uri())
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('library_or_repository',nargs='?');p.add_argument('--logo');p.add_argument('--open',action='store_true');a=p.parse_args();source=a.library_or_repository or input('Library or assembly repository: ').strip().strip('"');build(source,a.logo,a.open)
if __name__=='__main__':main()
