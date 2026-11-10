#!/usr/bin/env python3
"""Install the optional Monaco code editor (the editor of VS Code, MIT licence) into web/vendor/monaco, at setup time.

    python3 tools/fetch_monaco.py            # explain, ask for confirmation, download, verify, extract
    python3 tools/fetch_monaco.py --check    # report whether it is installed
    python3 tools/fetch_monaco.py --yes      # skip the question

Safety (ADR-0020): the version and its SHA-512 are pinned in this file, so a different or tampered archive is rejected
before anything is extracted; only files under package/min/vs plus the licence files are extracted, with path checks.
The folder web/vendor is git-ignored: nothing downloaded here ever enters the repository. Without Monaco the app
keeps using its plain text editor.
"""
import base64
import hashlib
import io
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path

VERSION = "0.57.0"
URL = f"https://registry.npmjs.org/monaco-editor/-/monaco-editor-{VERSION}.tgz"
INTEGRITY = "sha512-5BkI9KGoqrNvBGUe15/QlZq3OooZ8WLg1AxTpaqHRCP3HNpzPPZKE2EDz8M7c+VRmCeUw1Brp4cx/PWm3kI/5A=="
MAX_DOWNLOAD = 40_000_000
ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "web" / "vendor" / "monaco"
WANTED_PREFIX = "package/min/vs/"
WANTED_FILES = {"package/LICENSE": "LICENSE", "package/ThirdPartyNotices.txt": "ThirdPartyNotices.txt", "package/package.json": "package.json"}


def installed() -> bool:
    return (DEST / "vs" / "loader.js").is_file() and (DEST / "vs" / "editor" / "editor.main.js").is_file()


def verify(data: bytes, expected: str = INTEGRITY) -> bool:
    return "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode() == expected


def extract(data: bytes, dest: Path = DEST) -> int:
    """Extract only the wanted members, refusing anything that could escape `dest`."""
    count = 0
    dest = Path(dest)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for m in tar.getmembers():
            if not m.isfile():
                continue
            name = m.name
            if name in WANTED_FILES:
                rel = Path(WANTED_FILES[name])
            elif name.startswith(WANTED_PREFIX):
                rel = Path("vs") / name[len(WANTED_PREFIX):]
            else:
                continue
            target = (dest / rel).resolve()
            if dest.resolve() not in target.parents:
                raise SystemExit(f"refusing unsafe path in archive: {name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            f = tar.extractfile(m)
            target.write_bytes(f.read())
            count += 1
    return count


def download() -> bytes:
    with urllib.request.urlopen(URL, timeout=120) as r:                      # fixed https URL, size-capped
        data = r.read(MAX_DOWNLOAD + 1)
    if len(data) > MAX_DOWNLOAD:
        raise SystemExit("download is larger than expected; aborting")
    return data


def main(argv):
    if "--check" in argv:
        print(f"Monaco {VERSION}: {'installed' if installed() else 'not installed'} ({DEST})")
        return 0 if installed() else 1
    print(f"Monaco editor {VERSION} (MIT) will be downloaded from:\n  {URL}\n"
          f"  expected SHA-512: {INTEGRITY[:30]}…\n  size: about 18 MB (25 MB extracted) into {DEST.relative_to(ROOT)} (git-ignored).")
    if "--yes" not in argv and input("Type 'yes' to download and install it: ").strip().lower() != "yes":
        print("Cancelled. Nothing was downloaded.")
        return 1
    data = download()
    if not verify(data):
        print("INTEGRITY CHECK FAILED: the archive does not match the pinned hash. Nothing was extracted.")
        return 2
    if DEST.exists():
        shutil.rmtree(DEST)
    n = extract(data)
    print(f"Installed {n} files. Restart the server (or just reload the page); Monaco is used automatically.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
