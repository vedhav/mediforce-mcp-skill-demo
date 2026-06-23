# mediforce-mcp-skill-demo — "Word Explorer"

A deliberately small 4-step mediforce workflow that teaches the two extension
points: **linking a custom MCP** and **linking a custom skill**.

| # | Step | executor / plugin | Teaches |
|---|------|-------------------|---------|
| 1 | Provide Word | `human` | human input via `params` |
| 2 | Analyze Word | `script` / `script-container` | a deterministic script step |
| 3 | Find Anagrams | `agent` / `claude-code-agent` | **custom MCP** (`wordtools.anagrams`) |
| 4 | Write Poem | `agent` / `claude-code-agent` | **custom skill** (`word-poem`) |

A word flows through: human types it → script computes stats → an agent calls a
custom MCP tool for its anagrams → an agent uses a custom skill to write a poem.

## The two mechanisms

**MCP lives in the image.** `mcp/wordtools` is a stdio MCP server. The Dockerfile
`pip install`s it so `wordtools-mcp` is a command on `PATH`. The agent step
declares it inline and Claude Code spawns it:

```json
"mcpServers": [
  { "name": "wordtools", "command": "wordtools-mcp",
    "description": "anagrams(word) — words formable from a word's letters" }
]
```

**Skill lives in the repo, not the image.** `plugins/mcp-skill-demo/skills/word-poem/SKILL.md`
is read at run time from the cloned `repo@commit` via the step's `skillsDir`:

```json
"skill": "word-poem",
"skillsDir": "plugins/mcp-skill-demo/skills"
```

So a skill change is just push + re-pin (no image rebuild); an MCP change needs
an image rebuild.

**Both run only on `agent` (claude-code-agent) steps**, which use an LLM — so
steps 3 & 4 require `OPENROUTER_API_KEY`. A `script` step can't use an MCP or skill.

## Data flow

All container steps share `/workspace`. Step 2 writes `/workspace/state.json`;
step 3 reads it and writes `/workspace/anagrams.json`; step 4 reads both and
writes `/workspace/poem.md`. (Each step also sees the previous step's output at
`/output/input.json`.)

## Secrets (on the target instance, namespace `vedha`)

| Secret | Used by | Why |
| ------ | ------- | --- |
| `GITHUB_TOKEN` | all 3 container steps (`repoAuth`) | clone this repo over HTTPS for the image build (avoids the staging SSH-deploy-key bug) |
| `OPENROUTER_API_KEY` | steps 3 & 4 | the LLM behind the two agent steps |

## Runbook

Run the CLI from a mediforce checkout **on `main`** (older branches strip the
`script`/agent container fields).

### 1. Push (public repo — clone still uses the token via repoAuth)

```bash
cd /Users/vedha/Repo/mediforce-mcp-skill-demo
git init && git add -A && git commit -m "Word Explorer: MCP + skill demo workflow"
gh repo create mediforce-mcp-skill-demo --public --source=. --push
```

### 2. Pin the commit

```bash
git rev-parse HEAD
```

Set that SHA into `src/mcp-skill-demo.wd.json` (replace the four `0000…` `commit`
values — one per container step). The Dockerfile/MCP at that SHA is what the
image builds from.

### 3. Set the two secrets (example: staging)

```bash
BASE=https://staging.mediforce.ai/      # or the cdisc instance
MEDIFORCE_API_KEY=$(cat ~/.config/mediforce/staging-key) \
pnpm exec mediforce secret set --namespace=vedha --key=GITHUB_TOKEN --stdin --base-url=$BASE
MEDIFORCE_API_KEY=$(cat ~/.config/mediforce/staging-key) \
pnpm exec mediforce secret set --namespace=vedha --key=OPENROUTER_API_KEY --stdin --base-url=$BASE
```

### 4. Register, run, then complete the human step in the UI

```bash
MEDIFORCE_API_KEY=$(cat ~/.config/mediforce/staging-key) \
pnpm exec mediforce workflow register \
  --file=/Users/vedha/Repo/mediforce-mcp-skill-demo/src/mcp-skill-demo.wd.json \
  --namespace=vedha --base-url=$BASE

MEDIFORCE_API_KEY=$(cat ~/.config/mediforce/staging-key) \
pnpm exec mediforce run start --workflow=mcp-skill-demo --namespace=vedha --base-url=$BASE
```

Then in the UI: complete **Provide Word** (e.g. `listen`). Steps 2–4 run
automatically; the poem lands on the **Write Poem** step (and `/workspace/poem.md`).

## Local test (optional)

```bash
docker build -t mediforce-agent:mcp-skill-demo .   # needs mediforce-golden-image
# MCP tool:
docker run --rm mediforce-agent:mcp-skill-demo python3 -c \
  "from wordtools_mcp.server import anagrams; print(anagrams('listen'))"
# step-2 script:
mkdir -p /tmp/out && echo '{"word":"listen"}' > /tmp/out/input.json
docker run --rm -v /tmp/out:/output -v /tmp/ws:/workspace \
  mediforce-agent:mcp-skill-demo python3 /app/container/run.py
```
