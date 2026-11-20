import os
import re
from pathlib import Path
from app.config import settings

def test_t11_check_secret_exposure_in_repo():
    """T11: Check secret exposure in frontend bundle/repository -> no private API keys or credentials are exposed."""
    root_dir = settings.BASE_DIR
    forbidden_patterns = [
        re.compile(r"AI_PROVIDER_API_KEY\s*=\s*['\"][A-Za-z0-9_\-]{20,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{32,}"),
        re.compile(r"AIza[0-9A-Za-z-_]{35}"),
        re.compile(r"postgres://.*:.*@"),
        re.compile(r"mysql://.*:.*@"),
    ]

    # Search through app/static and app/api
    check_paths = [
        root_dir / "app" / "static",
        root_dir / "app" / "api",
        root_dir / "app" / "ai",
        root_dir / "app" / "analysis",
        root_dir / "app" / "database",
    ]

    for p in check_paths:
        if not p.exists():
            continue
        for file_path in p.rglob("*"):
            if file_path.is_file() and file_path.suffix in (".py", ".js", ".html", ".css", ".json"):
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                for pattern in forbidden_patterns:
                    match = pattern.search(content)
                    assert match is None, f"Potential secret exposure found in {file_path}: {match.group(0)}"
