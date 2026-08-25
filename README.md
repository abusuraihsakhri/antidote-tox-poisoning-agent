# Medical Toxicology Antidote Dosing & Poisoning Management Engine

A clinical decision support system for emergency medical toxicology, acute poisoning risk stratification, antidote pharmacokinetics, and toxidrome classification.

---

## Clinical Domain Overview & Guidelines

Acute intoxications require rapid identification of toxic syndromes (toxidromes) and time-critical administration of specific antidotes.

This system provides a verified, pure-standard-library implementation of established medical toxicology protocols:
- **Rumack-Matthew Nomogram** for acute Acetaminophen (APAP) hepatotoxicity assessment (150-line and 100-line).
- **N-Acetylcysteine (NAC)** IV 21-Hour (3-Bag), IV 20-Hour (2-Bag), and Oral 72-Hour protocols with weight capping.
- **Naloxone** low-dose titration and continuous infusion strategies for potent synthetic opioids (Fentanyl, Nitazenes).
- **Organophosphate & Carbamate Protocol**: Atropine doubling to pulmonary drying endpoints and Pralidoxime (2-PAM) dosing.
- **Toxic Alcohol Management**: Exact Osmolal Gap calculation, Anion Gap acidosis assessment, Fomepizole (4-MP) loading/maintenance, and hemodialysis trigger evaluation.
- **Toxidrome Diagnostic Classifier**: Systematic pattern recognition of vital signs, pupillary responses, diaphoresis, and bowel activity.

---

## Clinical Algorithms & Protocols

### 1. Acetaminophen (APAP) Nomogram
$$C_{\text{treat}}(t) = 150 \times 2^{-\frac{t - 4}{4}} \quad (\mu\text{g/mL for } 4 \le t \le 24\text{ hours})$$
- Evaluates risk of severe centrilobular hepatic necrosis.
- High-risk patients (chronic alcohol abuse, malnourishment, CYP2E1 inducers) are evaluated against the 100-line:
  $$C_{\text{high-risk}}(t) = 100 \times 2^{-\frac{t - 4}{4}} \quad (\mu\text{g/mL})$$

### 2. N-Acetylcysteine (NAC) Protocols
- **Standard 21-Hour IV (3-Bag)** (Weight capped at 100 kg):
  - Phase 1: $150\text{ mg/kg}$ in $200\text{ mL}$ D5W over 1 hour.
  - Phase 2: $50\text{ mg/kg}$ in $500\text{ mL}$ D5W over 4 hours ($12.5\text{ mg/kg/hr}$).
  - Phase 3: $100\text{ mg/kg}$ in $1000\text{ mL}$ D5W over 16 hours ($6.25\text{ mg/kg/hr}$).
  - Total: $300\text{ mg/kg}$ over 21 hours.
- **Simplified 20-Hour IV (2-Bag)**: $200\text{ mg/kg}$ over 4h, then $100\text{ mg/kg}$ over 16h.
- **Oral 72-Hour**: $140\text{ mg/kg}$ PO load, then $70\text{ mg/kg}$ q4h for 17 doses ($1330\text{ mg/kg}$ total).

### 3. Naloxone Titration for Opioids
- Starting dose: $0.04\text{ mg}$ IV push (avoids acute precipitated withdrawal and severe catecholamine surge).
- Titrate every 2-3 minutes ($0.04 \to 0.08 \to 0.2 \to 0.4 \to 2.0\text{ mg}$) to target spontaneous respiratory rate $\ge 10-12\text{ bpm}$.
- For synthetic opioids with prolonged elimination: continuous infusion at $2/3$ effective wake-up dose per hour.

### 4. Cholinergic / Organophosphate Crisis
- **Atropine Doubling Protocol**: Start $2-3\text{ mg}$ IV, double every 3-5 min ($3 \to 6 \to 12 \to 24\text{ mg}$) until **clear lung fields (drying of bronchial secretions)**, $\text{HR} > 80\text{ bpm}$, $\text{SBP} > 90\text{ mmHg}$.
- **Pralidoxime (2-PAM)**: $30\text{ mg/kg}$ (max $2000\text{ mg}$) IV load over 30 min, then $8-10\text{ mg/kg/hr}$ continuous infusion.

### 5. Toxic Alcohols & Osmolal Gap
$$\text{Calculated Osm} = 2[\text{Na}^+] + \frac{[\text{Glucose}]}{18} + \frac{[\text{BUN}]}{2.8} + \frac{[\text{Ethanol}]}{4.6}$$
$$\text{Osmolal Gap} = \text{Measured Osm} - \text{Calculated Osm} \quad (\text{Normal } \le 10\text{ mOsm/kg})$$
- **Fomepizole**: $15\text{ mg/kg}$ IV loading, then $10\text{ mg/kg}$ q12h x 4 doses, then $15\text{ mg/kg}$ q12h.
- **Emergent Hemodialysis Triggers**: $\text{pH} < 7.25$, $\text{HCO}_3^- < 10\text{ mEq/L}$, visual impairment, osmolal gap $> 25\text{ mOsm/kg}$.

---

## CLI Usage & Examples

### 1. APAP Nomogram Evaluation
```bash
python cli.py apap --hours 6.0 --level 125.0
```
Output:
```
===========================================================================
  ACETAMINOPHEN (APAP) RUMACK-MATTHEW NOMOGRAM
  Time Post-Ingestion: 6.0 hours | Level: 125.0 ug/mL
===========================================================================
  150-Treatment Line (US Standard): 106.1 ug/mL
  100-Treatment Line (High Risk):   70.7 ug/mL
  Risk Category:                   Above 150-Line (Treat with NAC)
  NAC Treatment Recommendation:    INITIATE NAC IMMEDIATELY
===========================================================================
```

### 2. NAC 3-Bag Weight-Based Calculation
```bash
python cli.py nac --weight 75.0 --regimen iv_3bag
```

### 3. Toxidrome Physical Exam Classifier
```bash
python cli.py toxidrome --hr 135 --sbp 155 --rr 20 --temp 38.8 --pupils mydriasis --skin dry --bowel-sounds hypoactive
```

---

## Python API Usage

```python
import antidote_tox_poisoning as atp

# APAP evaluation
res = atp.evaluate_rumack_matthew(hours_post_ingestion=7.5, apap_ug_ml=95.0)
print(f"Risk: {res.risk_tier}, Treat: {res.treat_with_nac}")

# Toxic alcohol evaluation
ta_plan = atp.evaluate_toxic_alcohol(
    toxicant="ethylene_glycol",
    weight_kg=70.0,
    measured_osmolality=325.0,
    sodium=140.0,
    glucose_mg_dl=90.0,
    bun_mg_dl=14.0,
    ph=7.20,
)
print(f"Osmolal Gap: {ta_plan.osmolal_gap}, Dialysis Needed: {ta_plan.hemodialysis_indicated}")
```

---

## Test Suite

```bash
python -m unittest test_antidote_tox_poisoning.py
```

27 comprehensive unit tests validate nomogram mathematical decay, high-risk lines, weight caps, doubling cascades, and physical exam classifications.

---

## License

MIT License. Copyright (c) 2026 Dr. Abu Suraih Sakhri.
