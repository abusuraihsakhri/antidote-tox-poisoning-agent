# Medical Toxicology Antidote Dosing & Poisoning Emergency Engine

A pure Python clinical toxicology, emergency medicine, and critical care poison center decision support system implementing:
- **Rumack-Matthew Nomogram for Acetaminophen (APAP) Toxicity:**
  - Evaluates acute ingestions between 4 and 24 hours:
    - Standard US 150-treatment line: $[\text{APAP}] = 150 \times 2^{-(t - 4) / 4}\text{ }\mu\text{g/mL}$
    - High-risk 100-treatment line (chronic alcohol, malnutrition, CYP2E1 inducers): $[\text{APAP}] = 100 \times 2^{-(t - 4) / 4}\text{ }\mu\text{g/mL}$
- **N-Acetylcysteine (NAC) Weight-Based Dosing Protocols:**
  - Standard IV 3-Bag 21-hour regimen (150 mg/kg over 1h, 50 mg/kg over 4h, 100 mg/kg over 16h; capped at 100 kg).
  - Modern IV 2-Bag 20-hour simplified regimen (200 mg/kg over 4h, 100 mg/kg over 16h).
  - Oral 72-hour regimen (140 mg/kg loading, then 70 mg/kg every 4 hours for 17 maintenance doses).
- **Opioid Reversal & Naloxone Titration Engine:**
  - Titrates naloxone boluses to reverse respiratory depression ($\text{RR} \ge 10 - 12\text{ bpm}$) rather than complete mental status awakening to prevent acute precipitated withdrawal.
  - High-dose titration logic for high-potency synthetic opioids (fentanyl, carfentanil).
- **Cholinergic Toxicity (Organophosphates & Carbamates):**
  - Doubling-dose Atropine protocol titrated until bronchial clearance ("dry lungs", heart rate $> 80\text{ bpm}$, $\text{SBP} > 80\text{ mmHg}$).
  - Pralidoxime (2-PAM) dosing: $2\text{ g}$ IV loading dose over 30 min followed by $8 - 10\text{ mg/kg/h}$ infusion.
- **Toxic Alcohol Ingestion (Methanol, Ethylene Glycol, Isopropanol):**
  - Osmolal gap calculation and Fomepizole ($15\text{ mg/kg}$ loading, $10\text{ mg/kg}$ q12h) / emergent hemodialysis indication triggers.
- **Toxidrome Pattern Classifier:**
  - Classifies anticholinergic, cholinergic, sympathomimetic, opioid, sedative-hypnotic, and serotonergic syndromes based on vital signs, pupils, diaphoresis, and bowel activity.
- **High-Throughput Batch Toxicology CSV Processing:** Ingests poison center exposure logs and emergency triage records.

Requires Python standard library only (zero external runtime dependencies).

---

## Toxicology Antidote Reference Matrix

| Toxic Exposure | Primary Antidote | Dosing Protocol | Clinical Endpoint |
|:---------------|:-----------------|:----------------|:------------------|
| **Acetaminophen** | N-Acetylcysteine (NAC) | $300\text{ mg/kg}$ IV over 21h or $300\text{ mg/kg}$ IV over 20h | APAP $< 10\text{ }\mu\text{g/mL}$, normal ALT/AST, INR $\le 1.2$ |
| **Opioids** | Naloxone | $0.04 - 0.4\text{ mg}$ IV initial ($2\text{ mg}$ if apneic) | Adequate ventilation ($\text{RR} \ge 12\text{ bpm}$) |
| **Organophosphates** | Atropine + Pralidoxime | Atropine $2 - 5\text{ mg}$ IV (doubling q3-5min); 2-PAM $2\text{ g}$ IV | Tracheobronchial clearance, $\text{HR} > 80\text{ bpm}$ |
| **Methanol / Ethylene Glycol** | Fomepizole | $15\text{ mg/kg}$ IV loading, then $10\text{ mg/kg}$ q12h $\times 4$ doses | Toxic alcohol $< 20\text{ mg/dL}$, normal acid-base |
| **Cyanide** | Hydroxocobalamin | $5\text{ g}$ IV over 15 min (may repeat once) | Reversal of lactic acidosis & hemodynamic stability |

---

## Features

- **Guidelines-Aligned Poison Control:** Built according to ACMT, AACT, and EAPCCT international recommendations.
- **Nomogram Dynamic Mathematical Solver:** Logarithmic half-life interpolation across all sampling intervals (4 to 24 hours).
- **Batch CSV Processing:** High-throughput batch triage for poison center case surveillance.

---

## Installation & Requirements

- Python 3.10+ (tested on 3.10, 3.11, 3.12)
- Zero external runtime dependencies. `pytest` is optional for running tests.

```bash
git clone https://github.com/abusuraihsakhri/antidote-tox-poisoning-agent.git
cd antidote-tox-poisoning-agent
```

---

## CLI Usage

### 1. Acetaminophen Rumack-Matthew Nomogram
```bash
python cli.py apap --hours 6.0 --level 180.0 --json
```

### 2. N-Acetylcysteine Weight-Based Protocol
```bash
python cli.py nac --weight 75.0 --regimen iv_3bag --json
```

### 3. Toxic Alcohol & Osmolal Gap Analysis
```bash
python cli.py toxic-alcohol --toxicant ethylene_glycol --weight 70.0 --measured-osm 330 --na 140 --glucose 100 --bun 15 --ph 7.20 --json
```

### 4. Batch CSV Processing
```bash
python cli.py batch --input sample.csv --output results.csv
```

---

## Python API Quickstart

```python
import antidote_tox_poisoning as atp

# Acetaminophen nomogram
res = atp.evaluate_rumack_matthew(hours_post_ingestion=6.0, apap_ug_ml=180.0)
print(f"Treatment Line (150): {res.treatment_threshold_150} ug/mL")
print(f"Treat with NAC: {res.treat_with_nac}")
print(f"Risk Tier: {res.risk_tier}")

# NAC dosing
plan = atp.calculate_nac_protocol(weight_kg=75.0, regimen="iv_3bag")
print(f"Total Dose: {plan.total_dose_mg} mg over {plan.total_duration_hours} hours")
```

---

## Running Tests

Run the test suite using standard `unittest` or `pytest`:

```bash
pytest -v
```

