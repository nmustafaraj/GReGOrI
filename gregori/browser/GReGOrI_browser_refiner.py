"""Refines GReGOrI Browser v4 into Browser v4.1 with responsive styles and polished UX."""
from __future__ import annotations
import argparse, json, re, shutil, webbrowser
from pathlib import Path

def must_replace(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Could not patch {label}; Browser v4 layout differs from the expected build.")
    return text.replace(old, new, 1)

def refine(source: str | Path, open_after: bool = False, logo: str | Path | None = None) -> Path:
    p = Path(source).expanduser().resolve()
    root = p if p.is_dir() else p.parent
    v4_page = root / "browser_v4" / "index.html"
    if not v4_page.exists():
        raise FileNotFoundError(f"Base Browser v4 not found: {v4_page}")

    s = v4_page.read_text(encoding="utf-8")
    s = s.replace("<h1>Pipeline</h1>", "<h1>Browser</h1>").replace("<h1>SHaNE Browser</h1>", "<h1>Browser</h1>").replace("<h1>Unified Browser</h1>", "<h1>Browser</h1>")

    css = r'''/* Browser v4.1 refinement */
.workspace-actions{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.chromosome-heading{text-align:center;padding:4px 0 10px}
.chromosome-heading .meta span,.modal-cartouche span{color:#4e6386;padding:0 5px}
.modal{padding:6vh 9vw!important}.dialog{height:auto!important;min-height:0;max-height:none!important;max-width:1320px;margin:auto}
.modaltop{position:relative!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;text-align:center!important;width:100%!important;margin:0 auto 16px auto!important;gap:12px!important}
.modal-heading{display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;text-align:center!important;gap:8px!important;width:100%!important}
.modal-title-row{display:inline-flex!important;align-items:center!important;justify-content:center!important;gap:14px!important;white-space:nowrap!important;margin:0 auto!important}
.modal-title-row h2{font-size:24px!important;font-weight:700!important;margin:0!important;white-space:nowrap!important}
.modal-cartouche{display:inline-flex!important;align-items:center!important;justify-content:center!important;gap:8px!important;margin:0 auto!important;padding:5px 16px!important;border:1px solid #304b72!important;border-radius:99px!important;background:#0d1933!important;white-space:nowrap!important;font-size:13px!important;color:var(--muted)!important}
.modal-illustration{width:100%!important;max-width:920px!important;margin:0 auto!important;display:flex!important;justify-content:center!important}
.modal-illustration .structure{width:100%!important;height:120px!important;display:block!important;margin:0 auto!important}
.methods-modal .modaltop{position:relative!important;display:flex!important;flex-direction:row!important;justify-content:space-between!important;align-items:center!important;width:100%!important;margin-bottom:14px!important}
.xclose,button.xclose{position:absolute!important;top:0!important;right:0!important;background:transparent!important;border:none!important;outline:none!important;box-shadow:none!important;color:#ffffff!important;font-size:24px!important;line-height:1!important;cursor:pointer!important;padding:2px 8px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;transition:transform .15s!important;z-index:10!important}
.xclose:hover,button.xclose:hover{background:transparent!important;border:none!important;box-shadow:none!important;color:#ffffff!important;transform:scale(1.2)!important}
.xclose:before,.xclose:after{display:none!important}
.seqbox,.alignbox{background:#071025!important;padding:18px!important;scrollbar-color:#315c7a #080f21;scrollbar-width:thin}
.base-at{color:#00f0ff!important}.base-gc{color:#ff2df1!important}
.seqrow{line-height:1.75!important}.copybar{display:flex;justify-content:flex-end;margin:8px 0}.copybtn{border-color:#526b91}
.gene-card{padding:14px!important;display:grid;gap:8px;cursor:pointer}.gene-card:hover{border-color:var(--green);box-shadow:0 0 14px #32d39933}
.gene-card h3,.gene-card p{margin:0}
*{scrollbar-color:#315c7a #080f21;scrollbar-width:thin}*::-webkit-scrollbar{width:9px;height:9px}*::-webkit-scrollbar-track{background:#080f21}*::-webkit-scrollbar-thumb{background:linear-gradient(var(--cyan),#315c7a);border-radius:8px}
@media(max-width:650px){.modal{padding:2vh 3vw!important}}
'''
    s = must_replace(s, "</style>", css + "</style>", "v4.1 styles")

    old_modal = '''<div class="modaltop"><div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;"><button id="modalPrev" class="nav-arrow-btn" onclick="navigateSHaNE(-1)" title="Previous SHaNE (Left Arrow)" style="background:transparent;border:1px solid #365079;border-radius:50%;width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center;font-size:16px;cursor:pointer;color:var(--ink);line-height:1;padding:0;">‹</button><h2 id="modalTitle" style="margin:0;"></h2><button id="modalNext" class="nav-arrow-btn" onclick="navigateSHaNE(1)" title="Next SHaNE (Right Arrow)" style="background:transparent;border:1px solid #365079;border-radius:50%;width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center;font-size:16px;cursor:pointer;color:var(--ink);line-height:1;padding:0;">›</button></div><button class="xclose" aria-label="Close" onclick="closeModal()" title="Close (Esc)">✕</button></div><div id="modalSub" class="meta"></div>'''
    new_modal = '''<div class="modaltop"><div class="modal-heading"><div class="modal-title-row" style="display:inline-flex;align-items:center;justify-content:center;gap:12px;white-space:nowrap;"><button id="modalPrev" class="nav-arrow-btn" onclick="navigateSHaNE(-1)" title="Previous SHaNE (Left Arrow)" style="background:transparent;border:1px solid #365079;border-radius:50%;width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center;font-size:16px;cursor:pointer;color:var(--ink);line-height:1;padding:0;">‹</button><h2 id="modalTitle" style="margin:0;font-size:22px;white-space:nowrap;"></h2><button id="modalNext" class="nav-arrow-btn" onclick="navigateSHaNE(1)" title="Next SHaNE (Right Arrow)" style="background:transparent;border:1px solid #365079;border-radius:50%;width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center;font-size:16px;cursor:pointer;color:var(--ink);line-height:1;padding:0;">›</button></div><div id="modalSub" class="modal-cartouche" style="white-space:nowrap;"></div></div><div id="modalIllustration" class="modal-illustration"></div><button class="xclose" aria-label="Close" onclick="closeModal()" title="Close (Esc)">✕</button></div>'''
    if old_modal in s:
        s = s.replace(old_modal, new_modal)

    # Restore linked metadata beside the logo.
    old_meta = "assemblyMeta.innerHTML=`${esc(a.species)} • ${esc(a.name)} • ${esc(srcName)} • ${esc(a.accession)}`"
    new_meta = "assemblyMeta.innerHTML=`<a target=\"_blank\" href=\"https://www.ncbi.nlm.nih.gov/datasets/genome/?taxon=${encodeURIComponent(a.species||'')}\">${esc(a.species)}</a> • <a target=\"_blank\" href=\"https://www.ncbi.nlm.nih.gov/datasets/genome/${encodeURIComponent(a.accession||'')}/\">${esc(a.name)}</a> • ${esc(srcName)} • ${esc(a.accession)}`"
    s = must_replace(s, old_meta, new_meta, "species and assembly links")

    # Organic navigation and chromosome controls
    s = s.replace("workspace.scrollIntoView({behavior:'smooth'});apply()", "apply();requestAnimationFrame(()=>workspace.scrollIntoView({behavior:'smooth',block:'start'}))")
    s = s.replace("function closeChrom(){selectedGroup=null;selectedRecord=null;apply();workspace.scrollIntoView({behavior:'smooth'})}", "function closeChrom(){let y=workspace.getBoundingClientRect().top+scrollY;selectedGroup=null;selectedRecord=null;apply();requestAnimationFrame(()=>scrollTo({top:Math.max(0,y-90),behavior:'smooth'}))}")

    # SHaNE illustration and polished cartouche inside the modal.
    old_sub = "modalSub.innerHTML=`${esc(s.sequence_accession)} <span>│</span> ${fmt(s.start)}–${fmt(s.end)} bp <span>│</span> ${esc(s.chromosome_group)}`"
    new_sub = "modalSub.innerHTML=`${esc(s.sequence_accession)} <span>│</span> ${fmt(s.start)}–${fmt(s.end)} bp <span>│</span> ${esc(s.chromosome_group)}`;modalIllustration.innerHTML='';modalIllustration.append(structure(s,true));modal.scrollTop=0;"
    s = must_replace(s, old_sub, new_sub, "modal illustration and cartouche")

    out = root / "browser_v4_1"
    out.mkdir(exist_ok=True)
    page = out / "index.html"
    page.write_text(s, encoding="utf-8")
    if (root / "browser_v4/data").is_dir():
        shutil.copytree(root / "browser_v4/data", out / "data", dirs_exist_ok=True)
    (out / "README.md").write_text("# GReGOrI Unified Browser v4.1\n\nA non-destructive refinement of Browser v4 polishing navigation, metadata, SHaNE details, gene cards, context display, and alignment spacing.\n", encoding="utf-8")
    print(f"Source: {source}\nCreated: {page}")
    if open_after:
        webbrowser.open(page.as_uri())
    return page

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("assembly", nargs="?")
    p.add_argument("--logo")
    p.add_argument("--open", action="store_true")
    a = p.parse_args()
    refine(a.assembly or input("Assembly repository: ").strip().strip('"'), a.open, a.logo)

if __name__ == "__main__":
    main()
