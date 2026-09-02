# Antidote Tox Poisoning Agent

> **Domain:** Clinical Pharmacology & Precision Pharmacotherapy  
> **Reference Guidelines & Standards:** `CPIC Guidelines & FDA Table of Pharmacogenomic Biomarkers`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Antidote Tox Poisoning Agent** is an advanced analytical and computational platform implementing Emergency Toxidrome Classifier & Weight-Based Antidote Doser.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`ToxidromeType`** — dedicated module for toxidrome type evaluation and state verification.
- **`RumackResult`** — dedicated module for rumack result evaluation and state verification.
- **`NACProtocolPlan`** — dedicated module for n a c protocol plan evaluation and state verification.
- **`NaloxonePlan`** — dedicated module for naloxone plan evaluation and state verification.
- **`OrganophosphatePlan`** — dedicated module for organophosphate plan evaluation and state verification.
- **`ToxicAlcoholPlan`** — dedicated module for toxic alcohol plan evaluation and state verification.

---

## 📐 Mathematical Formulation & Logic

```text
  calculated_osmolarity: float
  Calculate Rumack-Matthew nomogram risk line for acute acetaminophen ingestion.
  Calculate exact weight-based N-Acetylcysteine (NAC) dosing.
  Calculate Atropine doubling protocol and Pralidoxime (2-PAM) dosing.
  Calculate Osmolal Gap, Anion Gap, and Fomepizole / Hemodialysis indications.
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --- <value> --hours <value> --level <value> --high-risk <value>
```

### Parameter Reference
- `---`: Specifies input measurement or parameter value.
- `--hours`: Specifies input measurement or parameter value.
- `--level`: Specifies input measurement or parameter value.
- `--high-risk`: Specifies input measurement or parameter value.
- `--json`: Specifies input measurement or parameter value.
- `--weight`: Specifies input measurement or parameter value.
- `--regimen`: Specifies input measurement or parameter value.
- `--rr`: Specifies input measurement or parameter value.
- `--synthetic`: Specifies input measurement or parameter value.
- `--apnea`: Specifies input measurement or parameter value.

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t antidote-tox-poisoning-agent .
docker run -p 8000:8000 antidote-tox-poisoning-agent
```
