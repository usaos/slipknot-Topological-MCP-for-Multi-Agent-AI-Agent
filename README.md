Slipknot V4.1 Lite - Lightweight Topological Arbitration MCP Coprocessor
Underlying Mathematical Consensus Protocol for Multi-Agent Clusters | 7-Day Rapid Deployment Edition

🎯 Project Positioning
Slipknot is an AI infrastructure project that combines Topological Data Analysis (TDA) with Multi-Agent Systems. Its core positioning is the "Underlying Mathematical Consensus Protocol for Multi-Agent Clusters" / "Lightweight Topological Arbitration MCP Coprocessor".

Exclusive Differentiation Barriers:
Topological Consensus Court: Uses persistent graph Wasserstein/Bottleneck distances as a mathematically neutral yardstick to resolve decision-making conflicts and deadlocks among multiple Agents.
Reward Evolution Flywheel: Agents feed back business rewards, and Bayesian optimization automatically iterates TDA hyperparameters, making the data increasingly accurate with use.
Prototype of Federated Topological Privacy Computing: Only lightweight topological skeletons are uploaded while raw data remains local, ensuring compliance.
Industry-Adaptive Plugins: The same topological computation results are automatically translated into actionable business instructions for Agents in corresponding industries.

🚀 Quick Start

Option 1: Pure FastAPI Version (Recommended, Zero Dependencies)
bash
Install basic dependencies
pip install -r requirements.txt

One-click start
python dev_start.py

Access services
Health Check: http://127.0.0.1:8000/health
API Docs:     http://127.0.0.1:8000/docs
MCP Endpoint: http://127.0.0.1:8000/mcp
Tools List:   http://127.0.0.1:8000/mcp/tools

Option 2: FastMCP Standard Version (Standard MCP Protocol)
bash
Create virtual environment and install full dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Start FastMCP service
python -m slipknot.gateway

Access services
SSE Endpoint:  http://127.0.0.1:8000/sse
HTTP Endpoint: http://127.0.0.1:8000/mcp

Option 3: Docker Deployment
bash
chmod +x docker-run.sh
./docker-run.sh

🧪 Running Tests
bash
Core functionality tests (no need to start the service)
python scripts/demo_test.py

Gateway API tests (requires service to be started first)
python dev_start.py &
python scripts/gateway_test.py

📦 Project Structure
text
slipknot-lite/
├── slipknot/
│   ├── init.py              # Version declaration
│   ├── core/                    # TDA core computation layer
│   │   ├── accel.py             # Numba JIT acceleration functions
│   │   └── engine.py            # Topological analysis engine
│   ├── consensus/               # Topological Consensus Court
│   │   ├── models.py            # Pydantic data models
│   │   └── court.py             # Consensus arbitration engine
│   ├── storage/                 # Storage backend (Dual-mode)
│   │   └── backend.py           # Memory/Redis automatic fallback
│   ├── task/                    # Task pool
│   │   └── pool.py              # Thread pool task scheduling
│   ├── flywheel/                # Evolution flywheel
│   │   ├── filter.py            # Reward filter
│   │   └── optimizer.py         # Bayesian optimizer
│   ├── plugins/                 # Industry plugins
│   │   ├── energy.py            # Energy storage scheduling
│   │   ├── quant.py             # Quantitative trading
│   │   └── fraud.py             # Risk control & fraud
│   ├── gateway.py               # FastMCP standard gateway
│   └── gateway_simple.py        # Pure FastAPI gateway
├── scripts/
│   ├── demo_test.py             # Core functionality tests
│   └── gateway_test.py          # Gateway API tests
├── tmp/                         # Test data directory
├── dev_start.py                 # Local one-click start script
├── Dockerfile                   # Production container image
├── docker-run.sh                # Container one-click deployment
├── requirements.txt             # Dependency list
├── .env.example                 # Environment variables template
└── README.md                    # Project documentation

🔧 Core Features

TDA Topological Analysis Engine
Adaptive Sampling: Default upper limit of 3000, lower limit of 80, automatically adapts to data scale.
UMAP Dimensionality Reduction: Manifold learning preserves topological structures.
Persistent Homology Computation: Supports H0/H1/H2 three-order hole detection.
Singularity Identification: Automatically identifies anomalous data points.
Numba JIT Acceleration: Just-in-time compilation for core computational loops.

Topological Consensus Court
Dual-Layer Distance Determination: Bottleneck for rapid screening + Wasserstein for precise computation.
Three-Tier Verdicts: CONSENSUS_FAST / CONSENSUS / TOPOLOGICAL_DIVERGENCE.
Weaker Agent Identification: Automatically marks the Agent with lower confidence during divergence.
Mathematically Neutral Arbitration: Pure topological distance, free from subjective bias.

Reward Self-Evolution Flywheel
Reward Cleansing: Extreme value truncation + 3σ anomaly detection.
Bayesian Optimization: Gaussian process surrogate model + gp_minimize.
Industry Parameter Isolation: Independent hyperparameter optimization for each industry.
Automatic Triggering: Triggers optimization for every 50 valid Rewards.

Industry-Adaptive Plugins
Industry   Plugin   Core Capabilities
Energy Storage Scheduling   energy   Load cycle identification, charge/discharge strategies, fault warning

Quantitative Trading   quant   Market cycle detection, position management, hedging strategies

Risk Control & Fraud   fraud   Syndicate identification, transaction loop closure, risk grading

🔌 API Endpoints

Pure FastAPI Version (gateway_simple.py)

Health Check
http
GET /health

Get Tools List
http
GET /mcp/tools
Authorization: Bearer enterprise-agent-key-2026

Call MCP Tool
http
POST /mcp
Authorization: Bearer enterprise-agent-key-2026
X-Agent-Role: energy_storage
Content-Type: application/json

{
  "name": "submit_tda",
  "arguments": {
    "csv_path": "tmp/grid_load.csv",
    "industry": "energy"
  }
}

Available Tools
submit_tda - Submit topological data analysis task
 Parameters: csv_path (file path), industry (industry type)
 Returns: data_id + task status
get_insight - Get topological analysis results and industry instructions
 Parameters: data_id, agent_role (Agent role)
 Returns: Business insights + operational instructions + raw topological data
arbitrate - Multi-Agent topological consensus arbitration
 Parameters: state_a, state_b (topological states of two Agents)
 Returns: Arbitration verdict + distance metrics + weaker Agent identification
send_reward - Feed back business Reward to drive self-evolution
 Parameters: agent_id, industry, reward, params
 Returns: Cleansed Reward value

⚙️ Configuration

Environment Variables
env
Service Configuration
PORT=8000
MAX_WORKERS=4

Storage Configuration
USE_REDIS=0
REDIS_URL=redis://localhost:6379/0

Security Configuration
AGENT_TOKEN=enterprise-agent-key-2026

TDA Default Parameters
N_NEIGHBORS=15
MIN_DIST=0.1
HOLE_THRESHOLD=0.1
TOP_K=5

Default Token
enterprise-agent-key-2026

🎯 Use Cases

Smart Manufacturing
Production line multi-Agent scheduling conflict arbitration
Equipment anomaly topological pattern recognition
Quality fluctuation cycle detection

New Energy
Energy storage cluster load scheduling
Power grid peak-valley topological analysis
Photovoltaic output prediction optimization

Quantitative Finance
Multi-strategy Agent consensus arbitration
Market cycle topological identification
Risk topological early warning

Financial Risk Control
Anti-fraud multi-Agent cross-validation
Syndicate transaction topological detection
Anomalous behavior pattern recognition

📈 Performance Features
Numba JIT Acceleration: 5-10x speedup for core loops.
Dual-Layer Distance Determination: Fast return in 80% of scenarios, 3-5x overall speedup.
Adaptive Sampling: Automatic downsampling for large datasets to ensure response time.
Dual-Mode Storage: Zero-dependency memory mode, scalable Redis mode.
Thread Pool Concurrency: Supports parallel processing of multiple tasks.

🔒 Security Features
File Sandbox: Only allows reading files within whitelisted directories.
Token Authentication: All API calls require a Bearer Token.
Audit Logs: All arbitration operations are written to audit logs.
Parameter Validation: Strict type validation via Pydantic.

🚀 Version Evolution
Version   Positioning   Core Features
V1.0   Standalone Tool   Basic TDA analysis + CSV input

V2.0   Enterprise Middleware   FastAPI gateway + caching + authentication

V3.0   Platformization   SDK + plugin system + visualization

V4.0   Consensus Protocol   A2A communication + Topological Court + Evolution Flywheel

V4.1 Lite   Rapid Deployment   Lightweight architecture + zero dependencies + 7-day delivery

📝 Development Roadmap
[ ] V4.2: Federated Topological Privacy Computing
[ ] V4.5: Distributed Swarm Cluster
[ ] V5.0: Cross-Industry Plugin Marketplace
[ ] V5.5: Visual Topological Graph
[ ] V6.0: ASI-Level Topological Awareness Kernel

🤝 Tech Stack
Core Computation: NumPy, Numba, UMAP, Ripser, GUDHI
Web Framework: FastAPI, Uvicorn
Data Models: Pydantic
Optimization Algorithms: Scikit-Optimize, POT
MCP Protocol: FastMCP (Optional)
Deployment: Docker

📞 Contact
Project Repository: [GitHub]
Technical Documentation: [Wiki]
Issue Tracking: [Issues]

Slipknot V4.1 Lite - Empowering Multi-Agent Clusters with Mathematical-Grade Consensus