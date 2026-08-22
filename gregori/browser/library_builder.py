from __future__ import annotations
import subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;MODULES=HERE.parent
if str(MODULES) not in sys.path:sys.path.insert(0,str(MODULES))
from bright_browser_theme import apply as apply_browser_theme
from palaces.rich_library import build as build_rich_library
from palaces.browser_quality import apply as apply_browser_quality

def build_library(project,records,sequence_map=None,annotation_audit=None):return build_rich_library(project,records,sequence_map,annotation_audit)
def _run_browser_stage(command,label):
 proc=subprocess.run(command,capture_output=True,text=True)
 if proc.returncode:raise RuntimeError(f'{label} failed: '+(proc.stderr or proc.stdout))
def build_browser(root,library,logo):
 root=Path(root);library=Path(library);repo=library.parent
 stages=[([sys.executable,str(HERE/'GReGOrI_browser_v4_builder.py'),str(library),'--logo',str(logo)],'SHaNE Browser v4 build'),([sys.executable,str(HERE/'GReGOrI_browser_v4.1_refiner.py'),str(repo),'--logo',str(logo)],'SHaNE Browser v4.1 refinement'),([sys.executable,str(HERE/'GReGOrI_browser_v4.2_finisher.py'),str(repo)],'SHaNE Browser v4.2 finish')]
 for command,label in stages:_run_browser_stage(command,label)
 page=repo/'browser_v4_2/index.html'
 if not page.is_file():raise RuntimeError('SHaNE Browser v4.2 completed without index.html')
 apply_browser_theme(page);apply_browser_quality(page);return page
def build_ehab_draft(root,project_path,logo):
 root=Path(root);project_path=Path(project_path);out=project_path/'ehab_browser_draft'
 _run_browser_stage([sys.executable,str(root/'modules/browser/EHaB_browser_draft_builder.py'),str(project_path),'--output',str(out),'--logo',str(logo)],'EHaB draft build')
 page=out/'index.html'
 if not page.is_file():raise RuntimeError('EHaB draft completed without index.html')
 return page
