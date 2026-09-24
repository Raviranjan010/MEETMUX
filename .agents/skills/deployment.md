# Skill: deployment

**Purpose:** Prepare and, where possible, execute cloud deployment.
**When to use:** Phase 24.
**Inputs:** docs/DEPLOYMENT.md runbook.
**Outputs:** Either a live, health-checked URL, or an explicit 'documented but not executed' status.
**Files involved:** docs/DEPLOYMENT.md, deployment platform config files (vercel.json, render.yaml, etc. as applicable)
**Validation requirements:** If deployed, GET {url}/api/health actually returns 200; the response is quoted in the phase report.
**Failure handling:** Deployment platform unavailable in this environment → report as not executed, with the runbook still fully written for the human operator to run.
**Prohibited shortcuts:** Never state a deployment URL or 'live' status without having actually hit it and recorded the response.
