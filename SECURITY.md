# Security / Seguridad

## EN
**What this tool does:** it compiles and runs the Java code you type, on the machine where it runs. That is its job, and it is the main risk.

Protections included:
- Binds to `127.0.0.1` by default; `Host` and `Origin` are verified and `application/json` is required, so other web pages cannot send code to it.
- The code under test runs in a fresh temporary directory, with time and memory limits, no stdin, and **without your environment variables**.
- Docker setup: non-root user, read-only filesystem, all Linux capabilities dropped, `no-new-privileges`, CPU/memory/PID limits, port published on loopback only.

Not protected (by design): it is **not a sandbox for hostile code**. Submitted code can read what the process user can read (outside Docker: your files!) and, in Docker, use the container's network.
- Use Docker whenever the code is not yours. Never grade code from strangers. Never publish the port (`0.0.0.0`) or put it behind a public URL.
- If you change `ILAB_HOST` or `ILAB_ALLOWED_HOSTS` you take responsibility for the exposure.

**Reporting a vulnerability:** please open a *private* security advisory in the GitHub repository (Security → Report a vulnerability) rather than a public issue.

## ES
**Qué hace esta herramienta:** compila y ejecuta el código Java que escribes, en la máquina donde corre. Ese es su trabajo y también su principal riesgo.

Protecciones incluidas:
- Escucha solo en `127.0.0.1`; verifica `Host` y `Origin` y exige `application/json`, así otras páginas web no pueden mandarle código.
- El código bajo prueba corre en una carpeta temporal nueva, con límites de tiempo y memoria, sin entrada estándar y **sin tus variables de entorno**.
- Con Docker: usuario sin privilegios, sistema de archivos de solo lectura, sin capacidades de Linux, `no-new-privileges`, límites de CPU/memoria/procesos y puerto publicado solo en loopback.

Lo que NO protege (a propósito): **no es un sandbox para código hostil**. El código enviado puede leer lo que el usuario del proceso pueda leer (¡sin Docker, tus archivos!) y, con Docker, usar la red del contenedor.
- Usa Docker siempre que el código no sea tuyo. Nunca califiques código de desconocidos. Nunca publiques el puerto (`0.0.0.0`) ni lo pongas detrás de una URL pública.
- Si cambias `ILAB_HOST` o `ILAB_ALLOWED_HOSTS`, la exposición es tu responsabilidad.

**Reportar una vulnerabilidad:** abre un *aviso de seguridad privado* en el repositorio de GitHub (Security → Report a vulnerability), no un issue público.
