"""Runtime settings, read once from the environment (twelve-factor style)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    root: Path                 # where the application code and built-in content live
    home: Path                 # YOUR data: own problems, banks, exams, results
    host: str = "127.0.0.1"
    port: int = 8765
    allowed_hosts: frozenset = frozenset({"localhost", "127.0.0.1", "[::1]"})
    allow_fetch: bool = True   # may the server download links for "My bank"?
    ai_provider: str = ""      # "" (off, default) or "anthropic"
    ai_model: str = "claude-haiku-5-5"
    max_code_bytes: int = 50_000
    packs_dir: Path = None     # optional content packs (separate repos, e.g. a private question bank); default <root>/packs

    @classmethod
    def from_env(cls, root: Path, env=os.environ) -> "Settings":
        extra = {h.strip() for h in env.get("ILAB_ALLOWED_HOSTS", "").split(",") if h.strip()}
        return cls(
            root=Path(root).resolve(),
            home=Path(env.get("ILAB_HOME", Path(root) / "workspace")).resolve(),
            host=env.get("ILAB_HOST", "127.0.0.1"),
            port=int(env.get("ILAB_PORT", "8765")),
            allowed_hosts=frozenset({"localhost", "127.0.0.1", "[::1]"} | extra),
            allow_fetch=env.get("ILAB_ALLOW_FETCH", "1") != "0",
            ai_provider=env.get("ILAB_AI_PROVIDER", "").strip().lower(),
            ai_model=env.get("ILAB_AI_MODEL", "claude-haiku-5-5"),
            packs_dir=Path(env.get("ILAB_PACKS_DIR", Path(root) / "packs")).resolve(),
        )
