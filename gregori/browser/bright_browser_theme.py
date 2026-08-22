from __future__ import annotations
from pathlib import Path

CSS = r"""/* GReGOrI Standard Dark Theme Palette */
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
  --magenta: #25d9f4;
  --pink: #25d9f4;
  --creme: #fff4d4;
  --cyan: #25d9f4;
  --yellow: #f5b942;
  --green: #32d399;
  --purple: #5db8ff;
  --gray: #859bb8;
  --line: #1d3558;
  --accent: #25d9f4;
  --accent-glow: rgba(37,217,244,0.35);
  --modal-bg: #091428;
  --modal-border: #2a4c7c;
  --seq-bg: #040915;
}
body {
  background: var(--bg-grad) fixed !important;
  color: var(--ink) !important;
}
header {
  background: var(--header-bg) !important;
  border-bottom: 1px solid var(--header-border) !important;
}
.panel, .card {
  background: var(--panel) !important;
  border: 1px solid var(--panel-border) !important;
}
.ring-card {
  background: var(--panel) !important;
  border: 1px solid var(--panel-border) !important;
}
.ring-card.active {
  border-color: var(--accent) !important;
  box-shadow: 0 0 16px var(--accent-glow) !important;
}
.graph-panel {
  background: var(--panel) !important;
  border: 1px solid var(--panel-border) !important;
}
button, input, select {
  background: var(--btn-bg) !important;
  border: 1px solid var(--btn-border) !important;
  color: var(--ink) !important;
}
button:hover:not(:disabled):not(.xclose) {
  border-color: var(--accent) !important;
  box-shadow: 0 0 12px var(--accent-glow) !important;
}
.xclose, button.xclose {
  position: absolute !important;
  top: 0 !important;
  right: 0 !important;
  background: transparent !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  color: #ffffff !important;
  font-size: 24px !important;
  line-height: 1 !important;
  cursor: pointer !important;
  padding: 2px 8px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: transform .15s !important;
  z-index: 10 !important;
}
.xclose:hover, button.xclose:hover {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: #ffffff !important;
  transform: scale(1.2) !important;
}
.xclose:before, .xclose:after {
  display: none !important;
}
.sort-btn {
  background: var(--btn-bg) !important;
  border: 1px solid var(--btn-border) !important;
  color: var(--ink) !important;
}
.sort-btn:hover {
  border-color: var(--accent) !important;
  box-shadow: 0 0 12px var(--accent-glow) !important;
}
.records {
  scrollbar-color: var(--accent) var(--bg) !important;
}
.records::-webkit-scrollbar-track {
  background: var(--bg) !important;
}
.records::-webkit-scrollbar-thumb {
  background: linear-gradient(var(--accent), var(--line)) !important;
}
.record.sub {
  border-left: 2px solid var(--accent) !important;
}
.record.active {
  border-color: var(--accent) !important;
}
.chrom.selected {
  border-color: var(--magenta) !important;
  box-shadow: 0 0 18px var(--accent-glow) !important;
}
.badge, .chip {
  background: var(--btn-bg) !important;
  color: var(--ink) !important;
  border: 1px solid var(--btn-border) !important;
}
.genechip {
  background: #09261a !important;
  color: #c4f9e3 !important;
  border: 1px solid #1a6e4d !important;
  cursor: pointer !important;
}
.genechip:hover {
  border-color: var(--green) !important;
  box-shadow: 0 0 10px rgba(50, 211, 153, 0.4) !important;
}
.gene-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  margin-top: 10px;
}
.gene-card {
  background: var(--panel) !important;
  border: 1px solid var(--panel-border) !important;
  border-radius: 11px;
  padding: 14px;
  cursor: pointer !important;
  transition: .2s !important;
}
.gene-card:hover {
  border-color: var(--green) !important;
  box-shadow: 0 0 16px rgba(50, 211, 153, 0.35) !important;
  transform: translateY(-2px) !important;
}
.gene-card h3 {
  margin: 0 0 4px 0;
  color: var(--green);
}
.gene-link {
  display: inline-block;
  margin-top: 8px;
  color: var(--green) !important;
  font-weight: 600;
  text-decoration: none;
}
.gene-link:hover {
  text-decoration: underline;
}
.arm5 {
  fill: var(--cyan) !important;
}
.arm3 {
  fill: var(--magenta) !important;
}
.gene-track {
  fill: var(--green) !important;
  transition: .15s ease;
}
.dialog {
  background: var(--modal-bg) !important;
  border: 1px solid var(--modal-border) !important;
}
.panorama {
  background: var(--panel2) !important;
  border: 1px solid var(--line) !important;
}
.seqbox, .alignbox {
  background: var(--seq-bg) !important;
  border: 1px solid var(--line) !important;
}
.point {
  filter: drop-shadow(0 0 4px var(--accent-glow)) !important;
}
"""

JS = r"""/* GReGOrI Standard Theme */
Object.assign(C, {all: '#ff70ea', size: '#ffffff', score: '#00f0ff', islands: '#ffee33', genes: '#00ff88', gc: '#8ba2c2'});
"""

def apply(page: str | Path) -> Path:
    p = Path(page)
    text = p.read_text(encoding="utf-8")
    if "GReGOrI Standard Dark Theme Palette" in text:
        return p
    text = text.replace("</style>", CSS + "</style>", 1).replace("</script></body>", JS + "</script></body>", 1)
    p.write_text(text, encoding="utf-8")
    return p
