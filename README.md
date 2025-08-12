# CI-CD-CT-Docker-Kubernetes-DevOps-MLOps

# DevOps Pipeline Visualizer (Free-tier demo)

**Purpose:** Portfolio demo that visualizes CI/CD pipelines, Docker build logs, and a Kubernetes-style cluster map — all using free, open-source tools and designed to run on Streamlit Community Cloud (free tier).

## Highlights
- Live (optional) fetch of GitHub Actions runs for a public repo (owner/repo).
- Simulated streaming build logs for a realistic demo.
- Interactive pipeline timeline and KPIs.
- Kubernetes cluster topology visualization using `networkx` + `plotly`.
- Includes `Dockerfile`, `k8s/deployment.yaml`, and a sample GitHub Actions workflow for recruiter review.

## How to run
1. Create a new public GitHub repo and add files from this project.
2. Push to GitHub.
3. Go to https://share.streamlit.io/ and create a new app pointing to the repo and `app.py`.
4. Open the app — optionally enter a public repo in `owner/repo` form or use the simulator.

## Files in repo
- `app.py` — Streamlit frontend
- `requirements.txt` — dependencies
- `Dockerfile` — example
- `k8s/deployment.yaml` — example
- `.github/workflows/ci.yml` — sample CI workflow (education)

## Notes
- The demo **does not run real Kubernetes or Docker registries** on Streamlit free tier. Instead it **simulates** them and provides the real-world artifacts (Dockerfile, K8s manifest, CI workflow) so interviewers can see your end-to-end knowledge.
