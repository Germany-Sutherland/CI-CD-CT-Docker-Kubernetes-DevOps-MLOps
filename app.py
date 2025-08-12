# app.py
# DevOps Pipeline Visualizer (Free-tier version)
# - Uses only free open-source libraries
# - Simulates CI/CD builds, shows GitHub Actions runs if a public repo is provided
# - Visualizes a Kubernetes-style cluster (simulated) using networkx + plotly
# - Designed to run on Streamlit Community Cloud (free tier)

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import json
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone

# --------------------------
# Page config and header
# --------------------------
st.set_page_config(page_title="DevOps Pipeline Visualizer", layout="wide", page_icon="🚀")
st.title("🚀 DevOps Pipeline Visualizer — Resume Demo (Free Tier)")

st.markdown(
    "This demo **visualizes CI/CD, Docker build logs, and a Kubernetes cluster map**.\n\n"
    "You can (A) enter a public GitHub repo (`owner/repo`) to fetch recent GitHub Actions runs (unauthenticated), "
    "or (B) use the simulator which demonstrates the full pipeline. Everything here uses free open-source tools."
)

st.markdown("---")

# --------------------------
# Sidebar controls
# --------------------------
st.sidebar.header("Controls")
st.sidebar.markdown("Enter a public GitHub repository to fetch Actions runs (optional).")
repo_input = st.sidebar.text_input("Public repo (owner/repo)", value="")
use_sim = st.sidebar.checkbox("Force simulator (don't call GitHub API)", value=True)
refresh = st.sidebar.button("Refresh / Fetch")

st.sidebar.markdown("---")
st.sidebar.header("Artifacts & Examples")
st.sidebar.markdown("- `Dockerfile` and `k8s/deployment.yaml` included in repo")
st.sidebar.markdown("- `.github/workflows/ci.yml` sample is included")

# --------------------------
# Helper: fetch GitHub Actions runs (unauthenticated, low rate limit)
# --------------------------
GITHUB_RUNS_API = "https://api.github.com/repos/{owner_repo}/actions/runs?per_page=10"

@st.cache_data(ttl=60)
def fetch_github_actions(owner_repo: str):
    # owner_repo: "owner/repo"
    try:
        url = GITHUB_RUNS_API.format(owner_repo=owner_repo)
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        runs = data.get("workflow_runs", [])
        # normalize
        rows = []
        for run in runs:
            rows.append({
                "id": run.get("id"),
                "name": run.get("name") or run.get("workflow_id"),
                "status": run.get("status"),
                "conclusion": run.get("conclusion"),
                "created_at": run.get("created_at"),
                "updated_at": run.get("updated_at"),
                "run_number": run.get("run_number"),
                "html_url": run.get("html_url")
            })
        df = pd.DataFrame(rows)
        return df
    except Exception as e:
        return pd.DataFrame()  # empty df on error

# --------------------------
# Simulator functions (safe for free tier)
# --------------------------
def simulated_ci_history(n=12):
    rng = np.random.default_rng(42)
    times = pd.date_range(end=pd.Timestamp.now(tz=timezone.utc), periods=n, freq="H")
    status = rng.choice(["completed", "completed", "completed", "in_progress", "queued"], size=n, p=[0.6,0.1,0.1,0.1,0.1])
    conclusion = []
    for s in status:
        if s == "completed":
            conclusion.append(rng.choice(["success","failure","neutral"], p=[0.7,0.2,0.1] if False else [0.75,0.2,0.05]))
        else:
            conclusion.append(None)
    df = pd.DataFrame({
        "time": times,
        "status": status,
        "conclusion": conclusion
    })
    return df

def simulate_build_logs():
    # small, short simulated build log for UI streaming
    steps = [
        "Cloning repository...",
        "Checking out branch main...",
        "Installing dependencies (pip install -r requirements.txt)...",
        "Running unit tests (pytest)...",
        "Building Docker image (python:3.10-slim)...",
        "Pushing image to registry (simulated)...",
        "Deploying to Kubernetes (simulated kubectl apply)...",
        "Verifying deployment...",
        "Pipeline complete."
    ]
    return steps

# --------------------------
# Top row: CI/CD overview
# --------------------------
st.subheader("CI/CD Overview")

col1, col2 = st.columns([2,1])
with col1:
    st.markdown("**Recent Workflow Runs**")
    if repo_input and not use_sim:
        df_runs = fetch_github_actions(repo_input.strip())
        if df_runs.empty:
            st.warning("No runs fetched (API rate-limit or repo not found). Use simulator or try again later.")
            df_runs = simulated_ci_history().rename(columns={"time":"created_at"})
        else:
            # parse datetimes
            if "created_at" in df_runs.columns:
                df_runs["created_at"] = pd.to_datetime(df_runs["created_at"], errors="coerce")
        st.dataframe(df_runs.head(10))
    else:
        st.info("Showing simulated CI history (no GitHub fetch).")
        df_sim = simulated_ci_history(12)
        st.dataframe(df_sim.rename(columns={"time":"created_at"}))

with col2:
    st.markdown("**Pipeline KPIs (simulated)**")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.metric("Avg Build Time", "6m 24s")
    with kpi_col2:
        st.metric("Success Rate", "87%")
    with kpi_col3:
        st.metric("Deploy Frequency", "daily")

# --------------------------
# Build log simulator (animated)
# --------------------------
st.markdown("---")
st.subheader("Build Log (Simulated Streaming)")

log_col1, log_col2 = st.columns([3,1])
with log_col1:
    if st.button("Simulate Build Log"):
        steps = simulate_build_logs()
        log_area = st.empty()
        log_text = ""
        for step in steps:
            log_text += f"> {datetime.now().strftime('%H:%M:%S')} - {step}\n"
            log_area.code(log_text, language="bash")
            time.sleep(0.6)
        st.success("Build simulation complete (logs streamed above).")
    else:
        st.info("Click 'Simulate Build Log' to stream a sample container build log.")

with log_col2:
    st.markdown("**Artifacts**")
    st.write("- docker-image: myorg/sample:latest")
    st.write("- helm-chart: sample-chart v0.1.0")
    st.write("- artifact size: 24 MB")

# --------------------------
# Pipeline timeline chart (simulated)
# --------------------------
st.markdown("---")
st.subheader("Pipeline Timeline (Simulated)")

timeline_df = pd.DataFrame({
    "stage": ["checkout", "install", "test", "build", "push", "deploy", "verify"],
    "duration_min": [1, 2.5, 3.0, 4.2, 1.0, 2.0, 0.6]
})
fig_timeline = px.bar(timeline_df, x="stage", y="duration_min", title="Stage durations (minutes)")
st.plotly_chart(fig_timeline, use_container_width=True)

# --------------------------
# Kubernetes cluster map (simulated)
# --------------------------
st.markdown("---")
st.subheader("Kubernetes Cluster Map (Simulated)")

# build a small graph
G = nx.DiGraph()
G.add_node("cluster", type="cluster")
G.add_node("node-1", type="node")
G.add_node("node-2", type="node")
G.add_node("pod-frontend", type="pod")
G.add_node("pod-backend", type="pod")
G.add_node("pod-db", type="pod")
G.add_node("svc-frontend", type="service")

G.add_edges_from([
    ("cluster", "node-1"),
    ("cluster", "node-2"),
    ("node-1", "pod-frontend"),
    ("node-1", "pod-backend"),
    ("node-2", "pod-db"),
    ("svc-frontend", "pod-frontend")
])

pos = nx.spring_layout(G, seed=42)
node_x = []
node_y = []
node_text = []
node_color = []
for n in G.nodes():
    x, y = pos[n]
    node_x.append(x)
    node_y.append(y)
    typ = G.nodes[n].get("type", "pod")
    node_text.append(f"{n} ({typ})")
    color = {"cluster":"#114B5F", "node":"#028090", "pod":"#00A896", "service":"#02C39A"}.get(typ, "#00A896")
    node_color.append(color)

edge_x = []
edge_y = []
for e in G.edges():
    x0, y0 = pos[e[0]]
    x1, y1 = pos[e[1]]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

fig_graph = go.Figure()
fig_graph.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1, color="#888"), hoverinfo="none"))
fig_graph.add_trace(go.Scatter(
    x=node_x, y=node_y,
    mode="markers+text",
    marker=dict(size=30, color=node_color, line=dict(width=2, color="#222")),
    text=list(G.nodes()),
    textposition="bottom center",
    hovertext=node_text,
    hoverinfo="text"
))
fig_graph.update_layout(title="Simulated K8s cluster topology", showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False), height=450)
st.plotly_chart(fig_graph, use_container_width=True)

# --------------------------
# Quick interactive drills for interview/demo
# --------------------------
st.markdown("---")
st.subheader("Interactive Drills (Interview-ready)")

st.markdown("Click a drill to show sample commands a candidate would run in a real pipeline.")

if st.button("Show Docker build + push commands"):
    st.code("""# Build
docker build -t myorg/sample:latest .
# Tag & push (example)
docker tag myorg/sample:latest registry.example.com/myorg/sample:latest
docker push registry.example.com/myorg/sample:latest
""", language="bash")

if st.button("Show kubectl deploy + rollout"):
    st.code("""kubectl apply -f k8s/deployment.yaml
kubectl rollout status deployment/my-app -n production
kubectl get pods -o wide
""", language="bash")

# --------------------------
# Bottom: repo files & how it works
# --------------------------
st.markdown("---")
st.subheader("Included repo artifacts (for your GitHub)")
st.markdown("""
- `Dockerfile` — Example container image build instructions.
- `k8s/deployment.yaml` — Example Kubernetes deployment manifest.
- `.github/workflows/ci.yml` — Sample GitHub Actions workflow.
""")

st.markdown("### How this demo maps to real-world skills")
st.write(
    "- **CI/CD understanding**: shown via workflow runs, KPIs and build logs.\n"
    "- **Docker practice**: sample build commands & Dockerfile included.\n"
    "- **Kubernetes architecture**: topology visualization mimics node/pod/service relationships.\n"
    "- **Monitoring & telemetry**: timeline & pipeline KPIs demonstrate observability.\n"
    "- **Resume-ready**: Link this app in your CV and explain the repo artifacts to interviewers."
)

st.markdown("---")
st.caption("Demo by Amit — DevOps Pipeline Visualizer. All free & open source. Not a production CI/CD system; a portfolio demo for hiring interviews.")

# -----------------------
# BEAUTIFUL, LIGHTWEIGHT LAYMAN GUIDE (for bottom of page)
# -----------------------
user_guide_html = """
<style>
.user-guide {
    background: linear-gradient(145deg, #fefefe, #f5faff);
    border-radius: 16px;
    padding: 28px;
    box-shadow: 0 6px 24px rgba(0,0,0,0.06);
    font-family: "Segoe UI", Roboto, Arial, sans-serif;
    margin-top: 40px;
    border: 1px solid rgba(200, 220, 255, 0.4);
}

.user-guide h2 {
    text-align: center;
    font-size: 1.6rem;
    margin-bottom: 18px;
    color: #0a3d62;
    background: linear-gradient(90deg, #00b4db, #0083b0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.user-guide ol {
    counter-reset: step;
    padding-left: 0;
}

.user-guide li {
    list-style: none;
    margin: 12px 0;
    padding: 14px 18px;
    border-radius: 12px;
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.05);
    box-shadow: 0 3px 8px rgba(0,0,0,0.03);
    transition: transform 0.15s ease;
}
.user-guide li:hover {
    transform: translateY(-2px);
}

.user-guide li:before {
    counter-increment: step;
    content: "✔";
    background: linear-gradient(135deg,#00b4db,#0083b0);
    color: white;
    font-weight: bold;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    margin-right: 10px;
    border-radius: 50%;
    font-size: 14px;
    box-shadow: 0 3px 6px rgba(0,0,0,0.1);
}

.user-guide .step-title {
    font-weight: 600;
    color: #08323a;
}

.user-guide .step-why {
    display: block;
    font-size: 13px;
    color: #5f6f7e;
    margin-top: 4px;
}
</style>

<div class="user-guide">
    <h2>📘 How to Use This Tool – Step-by-Step (Easy English)</h2>
    <ol>
        <li><span class="step-title">Open the app link in your browser</span>
            <span class="step-why">Like opening a door before entering a shop.</span></li>
        <li><span class="step-title">Read the title & short intro</span>
            <span class="step-why">Tells you what the app does in one glance.</span></li>
        <li><span class="step-title">Look at the sidebar on the left</span>
            <span class="step-why">This is your control panel for the app.</span></li>
        <li><span class="step-title">If you have a GitHub repo, type it in (optional)</span>
            <span class="step-why">Lets the app fetch your real data.</span></li>
        <li><span class="step-title">Turn on “Simulate” to try a demo</span>
            <span class="step-why">Runs a fake safe example so you can see results instantly.</span></li>
        <li><span class="step-title">Click “Fetch” to get data</span>
            <span class="step-why">Like pressing ‘play’ to start the process.</span></li>
        <li><span class="step-title">Check the results table</span>
            <span class="step-why">Shows latest runs or tests for your project.</span></li>
        <li><span class="step-title">Look at the KPIs</span>
            <span class="step-why">Quick health check for speed & success rate.</span></li>
        <li><span class="step-title">Play the build log</span>
            <span class="step-why">See what happens step-by-step inside.</span></li>
        <li><span class="step-title">View the timeline chart</span>
            <span class="step-why">See which steps take longest.</span></li>
        <li><span class="step-title">Check the cluster map</span>
            <span class="step-why">Visual of how everything is connected.</span></li>
        <li><span class="step-title">Open Docker commands</span>
            <span class="step-why">See how the container is built & stored.</span></li>
        <li><span class="step-title">Open Kubernetes commands</span>
            <span class="step-why">See how deployment happens.</span></li>
        <li><span class="step-title">If for an interview, show your README</span>
            <span class="step-why">Explains your work to employers.</span></li>
        <li><span class="step-title">Click slowly & explore</span>
            <span class="step-why">Better understanding for better demos.</span></li>
        <li><span class="step-title">Take screenshots if errors appear</span>
            <span class="step-why">Helps in fixing & explaining issues.</span></li>
        <li><span class="step-title">Always try the sample if unsure</span>
            <span class="step-why">Gives a full working demo instantly.</span></li>
        <li><span class="step-title">Explain with simple examples</span>
            <span class="step-why">Makes it easier for non-technical people.</span></li>
        <li><span class="step-title">You can also run it locally</span>
            <span class="step-why">Faster and works without internet issues.</span></li>
        <li><span class="step-title">Close the tab when done</span>
            <span class="step-why">Keeps your session private & safe.</span></li>
    </ol>
</div>
"""

import streamlit as st
st.markdown(user_guide_html, unsafe_allow_html=True)
