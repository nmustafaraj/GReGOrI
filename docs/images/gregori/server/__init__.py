"""GReGOrI Local Web Application and Server."""
from __future__ import annotations

from .app import main, start_server
from .controller import (
    create_job,
    get_all_projects,
    mutate_project,
    setup_workspace,
)
from .picker import pick_paths
