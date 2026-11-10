# Interview Lab - runs the server AND compiles/executes the code you type inside the container.
# Build:  docker build -t interview-lab .
# Run:    see docker-compose.yml (recommended) or the README.
FROM eclipse-temurin:21-jdk-jammy

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --create-home --uid 10001 --shell /usr/sbin/nologin ilab

WORKDIR /app
COPY --chown=root:root server.py ./
COPY --chown=root:root interview_lab ./interview_lab
COPY --chown=root:root grader ./grader
COPY --chown=root:root web ./web
COPY --chown=root:root problems ./problems
COPY --chown=root:root tools ./tools
COPY --chown=root:root bank ./bank

# Optional AI question generator (off unless ILAB_AI_PROVIDER=anthropic and the user provides ANTHROPIC_API_KEY):
#   docker build --build-arg INSTALL_AI=1 -t interview-lab .
ARG INSTALL_AI=0
RUN if [ "$INSTALL_AI" = "1" ]; then apt-get update && apt-get install -y --no-install-recommends python3-pip \
    && pip3 install --no-cache-dir anthropic && rm -rf /var/lib/apt/lists/*; fi

# Your data (your own problems + your results) lives in a volume mounted at /data
ENV ILAB_HOME=/data ILAB_HOST=0.0.0.0 ILAB_PORT=8765 PYTHONDONTWRITEBYTECODE=1
RUN mkdir /data && chown ilab:ilab /data
VOLUME /data

USER ilab
EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=3s CMD python3 -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8765/api/problems', timeout=2)" || exit 1
CMD ["python3", "server.py"]
