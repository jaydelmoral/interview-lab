# Installation / Instalación

> **EN** — Two supported ways: Docker (recommended) or directly on your machine. About 5 minutes.
> **ES** — Dos formas: Docker (recomendada) o directamente en tu equipo. Unos 5 minutos.

## Requirements / Requisitos

| | Docker way | Direct way |
|---|---|---|
| Operating system | Linux, macOS, Windows 10/11 (Docker Desktop or WSL2) | Linux, macOS, Windows (WSL2 recommended) |
| Software | Docker with Compose v2 | **JDK 21** (`javac` and `java` on PATH) and **Python 3.9+** |
| Disk / RAM | ~600 MB image / 1 GB | ~200 MB / 512 MB |

## Option A — Docker (recommended)

```bash
git clone https://github.com/jaydelmoral/interview-lab.git
cd interview-lab
docker compose up --build
```

Open <http://localhost:8765>.

- **Linux file permissions:** if `workspace/` shows permission errors, run  
  `ILAB_UID=$(id -u) ILAB_GID=$(id -g) docker compose up --build`.
- **Stop:** `Ctrl+C`, or `docker compose down`. Your data stays in `./workspace`.
- **Why Docker:** the container runs non-root with a read-only filesystem, no extra Linux capabilities, and CPU/memory/process limits. The port is published on `127.0.0.1` only. See [SECURITY-MODEL.md](SECURITY-MODEL.md).

## Option B — Direct

1. Install JDK 21: Debian/Ubuntu `sudo apt-get install -y openjdk-21-jdk-headless`; macOS `brew install openjdk@21`; Windows: use WSL2 and the Ubuntu command, or install Temurin 21.
2. Check: `javac -version` (must print 21.x) and `python3 --version` (3.9+).
3. Run:
   ```bash
   git clone https://github.com/jaydelmoral/interview-lab.git
   cd interview-lab
   python3 server.py
   ```
4. Open <http://localhost:8765>.

⚠️ Outside Docker, the code you type runs **as your user**. Only grade code you wrote.

## Configuration / Configuración

All settings are environment variables (none are required).

| Variable | Default | Meaning |
|---|---|---|
| `ILAB_HOST` | `127.0.0.1` | Bind address. Docker sets `0.0.0.0` *inside* the container; the port mapping keeps it on loopback. |
| `ILAB_PORT` | `8765` | Port. |
| `ILAB_HOME` | `./workspace` | Your data folder (own problems, banks, exams, results). |
| `ILAB_ALLOWED_HOSTS` | *(empty)* | Extra `Host` names to accept (comma-separated). Changing this is your responsibility. |
| `ILAB_ALLOW_FETCH` | `1` | `0` disables downloading links for "My bank". |
| `ILAB_AI_PROVIDER` | *(off)* | `ollama` (local daemon, nothing leaves your machine) or `anthropic` (cloud, your own key) enables the optional AI question generator (see below). |
| `ILAB_AI_MODEL` | *(auto for `ollama`: first installed model)* / `claude-haiku-5-5` for `anthropic` | Model used by the AI generator. |
| `ILAB_OLLAMA_URL` | `http://127.0.0.1:11434` | Local Ollama daemon. Non-loopback hosts are refused unless `ILAB_OLLAMA_ALLOW_REMOTE=1`. |
| `ILAB_PACKS_DIR` | `./packs` | Folder with optional content packs (separate repositories, for example a private question bank). |

### Optional: local AI with Ollama (nothing leaves your machine)
```bash
ollama pull qwen3.5:9b                # or any model you prefer; larger models write better questions
export ILAB_AI_PROVIDER=ollama
# export ILAB_AI_MODEL=qwen3.5:9b     # optional: otherwise the first installed model is used
python3 server.py
```
The adapter talks to `http://127.0.0.1:11434/api/chat` with the standard library only. It refuses non-loopback hosts unless you set `ILAB_OLLAMA_ALLOW_REMOTE=1`. Small local models make mistakes: everything the model writes is validated structurally and stays in *your* bank as a draft for you to check. On CPU-only machines a 9B model can need minutes per request.

### Optional: AI question generator with **your own** key
Off by default. When on, the text you add to "My bank" is **sent to the provider** and **billed to your account**.

```bash
pip install anthropic                 # optional dependency
export ANTHROPIC_API_KEY=...          # your key, never commit it
export ILAB_AI_PROVIDER=anthropic
python3 server.py
```
The landing page shows which generator is active. If the AI call fails, the offline generator is used and a warning is shown. In Docker, pass the variables in `docker-compose.yml` (`environment:`) and build with the SDK installed.

## Verify the installation / Verificar

```bash
python3 -m unittest discover -s tests -t .     # 45 tests; JVM tests are skipped without a JDK
python3 tools/validate.py                      # validates every exercise (reference must score 100%)
```

## Upgrade, backup, uninstall / Actualizar, respaldar, desinstalar

- **Upgrade:** `git pull`, then restart (`docker compose up --build`).
- **Backup:** copy the `workspace/` folder. It is plain JSON/Markdown/Java files.
- **Uninstall:** `docker compose down --rmi local`, then delete the folder.

## Troubleshooting / Problemas frecuentes

| Symptom | Cause and fix |
|---|---|
| `JDK not found` | Install JDK 21 and make sure `javac` is on PATH (direct way), or use Docker. |
| Permission denied on `workspace/` (Linux Docker) | Start with `ILAB_UID=$(id -u) ILAB_GID=$(id -g) docker compose up`. |
| "origin not allowed" (403) | You opened the app with a different host name. Use `http://localhost:8765` (or set `ILAB_ALLOWED_HOSTS`). |
| Port already in use | Set `ILAB_PORT=8766` (and change the compose port mapping). |
| A link cannot be added | Only public HTTP(S) pages (no logins, JavaScript-only pages or PDFs). Paste the text as notes instead. |
| Remote server through SSH | `ssh -N -L 8765:127.0.0.1:8765 your-server`, then open `http://localhost:8765` on your computer. |
