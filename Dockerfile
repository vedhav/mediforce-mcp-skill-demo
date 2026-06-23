# =============================================================================
# Word Explorer agent image (MCP + skill demo)
#
# Extends mediforce-golden-image with:
#   - an English wordlist (wamerican -> /usr/share/dict/words) for the MCP
#   - the custom `wordtools-mcp` MCP server (console command on PATH)
#   - the step-2 deterministic script
#
# NOTE: skills are deliberately NOT baked into the image — they live in the repo
# under plugins/ and are read at run time via the step's `skillsDir` + repo+commit
# clone. Only MCP servers (console commands the agent spawns) must be in the image.
#
# Build by hand for local testing (needs mediforce-golden-image present):
#   docker build -t mediforce-agent:mcp-skill-demo .
# =============================================================================

FROM mediforce-golden-image

RUN apt-get update \
 && apt-get install -y --no-install-recommends wamerican \
 && rm -rf /var/lib/apt/lists/*

# Custom MCP: puts the `wordtools-mcp` console command on PATH.
COPY mcp /app/mcp
RUN pip3 install --no-cache-dir --break-system-packages /app/mcp/wordtools

# Step-2 deterministic script.
COPY container/run.py /app/container/run.py

WORKDIR /workspace
