# Arkansas Civic Intelligence System Patch

This patch adds **new files only** so you can strategically place them into the repo without overwriting stable work.

## What this patch adds

### New engines
- `engine/user_identity_engine.py`
- `engine/civic_mentor_engine.py`
- `engine/civic_intelligence_system.py`

### New build script
- `scripts/build_civic_intelligence_system.py`

### New dashboard files
- `apps/editor-dashboard/civic-intelligence-dashboard.html`
- `apps/editor-dashboard/civic-intelligence-dashboard.css`
- `apps/editor-dashboard/civic-intelligence-dashboard.js`

## What the new engines do

### User Identity Engine
Adds learner identity, profile metadata, badge awards, role signals, readiness scoring, and identity snapshots.

### Civic Mentor Engine
Turns analytics + identity + tracks + graph state into learner guidance and platform-level priorities.

### Civic Intelligence System
Builds one unified cross-engine snapshot for the whole platform.

## Install order

1. Copy the three files in `engine/`
2. Copy the file in `scripts/`
3. Copy the three files in `apps/editor-dashboard/`
4. Keep your existing working `engine/learning_analytics_engine.py` exactly as-is unless you intentionally want to replace it later

## Run order

After placing the files into your repo root, run:

```powershell
python scripts/build_civic_intelligence_system.py
```

## Expected outputs

This build will generate or refresh:

- `exports/civic_intelligence/civic_intelligence_dashboard.json`
- `exports/civic_intelligence/civic_intelligence_system.md`
- `exports/civic_intelligence/civic_intelligence_manifest.json`
- `exports/identity/identity_index.json`
- `exports/mentor/platform_mentor_brief.json`

It will also refresh supporting exports if needed:

- civic intelligence map
- knowledge graph
- track definitions
- learning analytics

## Dashboard viewer

Open:

```text
apps/editor-dashboard/civic-intelligence-dashboard.html
```

That page reads:

```text
exports/civic_intelligence/civic_intelligence_dashboard.json
```

and shows:

- system health
- tracks
- analytics summary
- mentor priorities
- learner previews
- graph and map summaries

## Notes

- This patch is **filesystem-first** and does not require a database.
- It is designed to sit on top of your existing kernel, course engine, track engine, map, graph, and analytics layers.
- If you later want tighter integration, the next phase should be adding direct links from `apps/editor-dashboard/index.html` into the new dashboard page and wiring lesson runtime events into real learner IDs.
