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
# USER GUIDE (Layman-friendly, colorful) - paste at the absolute bottom of app.py
# -----------------------
usage_html = """
<style>
/* container */
.howto { 
  background: linear-gradient(135deg,#fff7ed,#e8f7ff); 
  padding: 22px; 
  border-radius: 12px; 
  box-shadow: 0 8px 30px rgba(20,30,50,0.08);
  font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
  margin-top: 28px;
}

/* title */
.howto h2 { 
  text-align:center; 
  color: #113c55; 
  margin-bottom: 10px;
  font-size: 22px;
}

/* ordered list */
.howto ol { counter-reset: step; padding-left: 0; margin-left: 0; }

/* each step card */
.howto li {
  list-style: none;
  background: linear-gradient(90deg,#ffffff,#f6fbff);
  margin: 10px 0;
  padding: 14px 16px;
  border-radius: 10px;
  display: block;
  border-left: 6px solid rgba(17,60,85,0.12);
  box-shadow: 0 3px 12px rgba(12,24,40,0.04);
}

/* step number badge */
.howto li:before{
  counter-increment: step;
  content: counter(step);
  background: linear-gradient(135deg,#2b9eb3,#1f6f8b);
  color: white;
  font-weight: 700;
  display: inline-block;
  width: 30px;
  height: 30px;
  line-height: 30px;
  text-align: center;
  border-radius: 50%;
  margin-right: 12px;
  margin-left: 2px;
  box-shadow: 0 4px 10px rgba(31,70,90,0.15);
}

/* step title */
.howto .title { font-weight: 700; color: #08323a; display:inline; font-size:16px; }

/* reason text (smaller) */
.howto .why { display:block; color:#475569; margin-top:6px; font-size:14px; }

@media(max-width:600px) {
  .howto li { padding: 12px; }
  .howto h2 { font-size:18px; }
}
</style>

<div class="howto">
  <h2>How to use this DevOps Pipeline Visualizer — easy step-by-step</h2>
  <ol>
    <li><span class="title">Open the app link in your browser.</span>
        <span class="why">Why: This opens the tool so you can use it (like opening a door to a room).</span></li>

    <li><span class="title">Read the top title and short description.</span>
        <span class="why">Why: It tells you what the tool does so you know if it helps you.</span></li>

    <li><span class="title">Look at the left side (sidebar).</span>
        <span class="why">Why: The sidebar has the controls you will use, like switches and boxes.</span></li>

    <li><span class="title">If you have a public GitHub repo, type owner/repo in the box (optional).</span>
        <span class="why">Why: This lets the app try to show real CI/CD runs from that repo (optional step).</span></li>

    <li><span class="title">Toggle 'Force simulator' if you want a demo run.</span>
        <span class="why">Why: Simulator runs a safe demo so the app always shows something even without a repo.</span></li>

    <li><span class="title">Click 'Refresh / Fetch' to load data.</span>
        <span class="why">Why: This asks the app to fetch recent workflow activity or prepare the demo history.</span></li>

    <li><span class="title">Check 'Recent Workflow Runs' table.</span>
        <span class="why">Why: It shows recent build or test runs — useful to see if things pass or fail.</span></li>

    <li><span class="title">Look at the KPIs (Avg build time, Success rate).</span>
        <span class="why">Why: These numbers quickly tell you if pipelines are healthy or slow.</span></li>

    <li><span class="title">Click 'Simulate Build Log' to stream a build log.</span>
        <span class="why">Why: It shows step-by-step messages (like watching a bread recipe being followed).</span></li>

    <li><span class="title">Watch the log appear line by line.</span>
        <span class="why">Why: This helps you understand what happens during each pipeline step.</span></li>

    <li><span class="title">Check 'Artifacts' on the right for image names or sizes.</span>
        <span class="why">Why: Artifacts are the packaged results — like a finished product in a box.</span></li>

    <li><span class="title">See the 'Pipeline Timeline' chart.</span>
        <span class="why">Why: This shows how long each stage (install, test, build) takes so you know where delays are.</span></li>

    <li><span class="title">Explore the 'Kubernetes Cluster Map' graphic.</span>
        <span class="why">Why: It shows components (nodes, pods, services) and how they connect — like rooms in a house map.</span></li>

    <li><span class="title">Use 'Show Docker build + push commands' button to view commands.</span>
        <span class="why">Why: These are the actual commands used to build and push a container image (like a recipe).</span></li>

    <li><span class="title">Use 'Show kubectl deploy + rollout' to see deploy commands.</span>
        <span class="why">Why: These commands show how the app would be started in a cluster (for advanced users or interviews).</span></li>

    <li><span class="title">If you are showing this to a hiring manager, highlight the README files in the repo.</span>
        <span class="why">Why: README explains your work and is what recruiters will read next.</span></li>

    <li><span class="title">Click around slowly — read each message and chart.</span>
        <span class="why">Why: The app is a demo; understanding the messages helps you explain it to others.</span></li>

    <li><span class="title">If something looks like 'failure', take a screenshot.</span>
        <span class="why">Why: Screenshots show problems and help you discuss fixes in interviews.</span></li>

    <li><span class="title">Use the simulated sample if you do not have a repo.</span>
        <span class="why">Why: The sample always shows a complete demo so recruiters can click and see results.</span></li>

    <li><span class="title">Tell the interviewer what you did to create this app.</span>
        <span class="why">Why: Employers want to know your steps — mention GitHub, Streamlit, Dockerfile, and K8s manifest.</span></li>

    <li><span class="title">If showing to non-technical people, explain with simple analogies (e.g., 'pipeline = factory').</span>
        <span class="why">Why: It helps people understand without technical words.</span></li>

    <li><span class="title">If you want to demo locally, run the git repo and start Streamlit on your laptop.</span>
        <span class="why">Why: Local run is faster for hands-on demos and you control the environment.</span></li>

    <li><span class="title">If you are stuck, ask for help — use README or the contact line in the repo.</span>
        <span class="why">Why: The repo includes instructions and contact info for questions.</span></li>

    <li><span class="title">When finished, close the browser tab for privacy.</span>
        <span class="why">Why: This prevents others from seeing your session and makes sure your data is private.</span></li>
  </ol>
</div>
"""

import streamlit as st
st.markdown(usage_html, unsafe_allow_html=True)
