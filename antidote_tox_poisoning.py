#!/usr/bin/env python3
"""
Medical Toxicology Decision Support & Antidote Dosing Engine.

Domain: Emergency Toxicology & Critical Care Poisoning Management
Clinical Protocols & Standards:
- Rumack-Matthew Nomogram for Acetaminophen (APAP) Toxicity (150-Line & 100-Line)
- NAC (N-Acetylcysteine) 21-Hour IV, 2-Bag IV, and 72-Hour Oral Protocols
- Naloxone Titration & Synthetic Opioid Infusion Strategy
- Organophosphate / Carbamate Atropinization Doubling Rule & Pralidoxime (2-PAM)
- Osmolal Gap Calculation & Fomepizole / Hemodialysis Dosing for Toxic Alcohols
- Hydroxocobalamin Cyanide Protocol & High-Dose Insulin (HIET) for CCB/BB Overdose
- Systematic Toxidrome Diagnostic Classifier

Pure Python standard library implementation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union


# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

class ToxidromeType(str, Enum):
    CHOLINERGIC = "cholinergic"
    ANTICHOLINERGIC = "anticholinergic"
    SYMPATHOMIMETIC = "sympathomimetic"
    OPIOID = "opioid"
    SEDATIVE_HYPNOTIC = "sedative_hypnotic"
    SEROTONERGIC = "serotonergic"
    UNKNOWN = "unknown"


RUMACK_150_LINE_AT_4H = 150.0  # ug/mL at 4h post-ingestion
RUMACK_100_LINE_AT_4H = 100.0  # High-risk line (fasting, alcohol, CYP inducers)
APAP_HALF_LIFE_HOURS = 4.0     # 4.0-hour elimination half-life decay


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass(frozen=True)
class RumackResult:
    hours_post_ingestion: float
    apap_ug_ml: float
    treatment_threshold_150: float
    treatment_threshold_100: float
    risk_tier: str  # "Above 150-Line (Treat with NAC)", "High Risk (Above 100-Line)", "Borderline", "Below Treatment Line"
    treat_with_nac: bool
    clinical_rationale: str


@dataclass(frozen=True)
class NACProtocolPlan:
    route: str  # "IV (3-Bag)", "IV (2-Bag)", "Oral (72-Hour)"
    patient_weight_kg: float
    dosing_weight_kg: float
    total_duration_hours: int
    total_dose_mg: float
    phases: List[Dict[str, Any]]
    discontinuation_criteria: List[str]


@dataclass(frozen=True)
class NaloxonePlan:
    respiratory_rate: float
    suspected_potent_synthetic: bool
    initial_dose_mg: float
    route: str
    titration_steps: List[str]
    continuous_infusion_indicated: bool
    infusion_rate_mg_hr: Optional[float]
    clinical_guidance: List[str]


@dataclass(frozen=True)
class OrganophosphatePlan:
    weight_kg: float
    atropine_starting_dose_mg: float
    atropine_doubling_sequence_mg: List[float]
    atropinization_endpoints: List[str]
    pralidoxime_loading_mg: float
    pralidoxime_infusion_mg_hr: float
    clinical_warnings: List[str]


@dataclass(frozen=True)
class ToxicAlcoholPlan:
    toxicant: str
    measured_osmolality: float
    calculated_osmolarity: float
    osmolal_gap: float
    anion_gap: float
    fomepizole_indicated: bool
    fomepizole_loading_mg: float
    fomepizole_maintenance_mg: float
    hemodialysis_indicated: bool
    hemodialysis_triggers: List[str]
    adjunctive_vitamins: List[str]


@dataclass(frozen=True)
class ToxidromeClassification:
    primary_toxidrome: ToxidromeType
    confidence: str  # "High", "Moderate", "Low"
    matching_features: List[str]
    differentials: List[str]
    recommended_antidote: str
    immediate_actions: List[str]


# =============================================================================
# DOMAIN PROTOCOLS & ALGORITHMS
# =============================================================================

def evaluate_rumack_matthew(
    hours_post_ingestion: float,
    apap_ug_ml: float,
    high_risk_patient: bool = False,
) -> RumackResult:
    """
    Calculate Rumack-Matthew nomogram risk line for acute acetaminophen ingestion.
    Valid between 4.0 and 24.0 hours post-ingestion.
    """
    if hours_post_ingestion < 4.0:
        raise ValueError(
            f"Nomogram is valid only >= 4.0 hours post-ingestion (provided: {hours_post_ingestion:.1f}h). "
            "APAP absorption is not complete before 4 hours; repeat level at 4h."
        )
    if hours_post_ingestion > 24.0:
        # After 24h, nomogram is not strictly interpretable; any detectable APAP or elevated ALT requires NAC.
        treat = apap_ug_ml > 5.0
        return RumackResult(
            hours_post_ingestion=hours_post_ingestion,
            apap_ug_ml=apap_ug_ml,
            treatment_threshold_150=0.0,
            treatment_threshold_100=0.0,
            risk_tier="Delayed Presentation (>24h)",
            treat_with_nac=treat,
            clinical_rationale="Ingestion occurred >24 hours ago. Treat with NAC if APAP detectable or AST/ALT elevated.",
        )

    # 150-Line equation: C(t) = 150 * 2^(-(t-4)/4)
    line_150 = RUMACK_150_LINE_AT_4H * math.pow(2.0, -(hours_post_ingestion - 4.0) / APAP_HALF_LIFE_HOURS)
    # 100-Line equation: C(t) = 100 * 2^(-(t-4)/4)
    line_100 = RUMACK_100_LINE_AT_4H * math.pow(2.0, -(hours_post_ingestion - 4.0) / APAP_HALF_LIFE_HOURS)

    effective_threshold = line_100 if high_risk_patient else line_150

    if apap_ug_ml >= line_150:
        tier = "Above 150-Line (Treat with NAC)"
        treat = True
        rationale = f"Level ({apap_ug_ml:.1f} ug/mL) is above the 150-treatment line ({line_150:.1f} ug/mL). High risk of severe hepatotoxicity."
    elif apap_ug_ml >= line_100:
        if high_risk_patient:
            tier = "High Risk (Above 100-Line)"
            treat = True
            rationale = f"Level ({apap_ug_ml:.1f} ug/mL) is above the high-risk 100-treatment line ({line_100:.1f} ug/mL) in a high-risk patient."
        else:
            tier = "Borderline (Between 100 and 150 lines)"
            treat = False
            rationale = f"Level ({apap_ug_ml:.1f} ug/mL) is between 100 and 150 lines. Standard patient; consider repeat level in 2-4 hours or clinical context."
    else:
        tier = "Below Treatment Line"
        treat = False
        rationale = f"Level ({apap_ug_ml:.1f} ug/mL) is below treatment threshold ({effective_threshold:.1f} ug/mL). Low risk of hepatotoxicity."

    return RumackResult(
        hours_post_ingestion=round(hours_post_ingestion, 1),
        apap_ug_ml=round(apap_ug_ml, 1),
        treatment_threshold_150=round(line_150, 1),
        treatment_threshold_100=round(line_100, 1),
        risk_tier=tier,
        treat_with_nac=treat,
        clinical_rationale=rationale,
    )


def calculate_nac_protocol(
    weight_kg: float,
    regimen: str = "iv_3bag",
) -> NACProtocolPlan:
    """
    Calculate exact weight-based N-Acetylcysteine (NAC) dosing.
    Weight is capped at 100 kg per FDA / tox consensus guidelines.
    """
    if weight_kg <= 0:
        raise ValueError("Patient weight must be positive")

    dosing_w = min(weight_kg, 100.0)
    discon = [
        "Serum APAP concentration is undetectable (< 5-10 ug/mL)",
        "ALT and AST are normal or demonstrably decreasing",
        "INR is < 1.5 (or <= 1.3) and patient is clinically well",
        "At least one full cycle of NAC completed",
    ]

    reg_clean = regimen.lower().replace("-", "_")

    if reg_clean in ("iv_3bag", "iv_21hour", "iv"):
        # 150 mg/kg over 1h, 50 mg/kg over 4h, 100 mg/kg over 16h
        p1_mg = 150.0 * dosing_w
        p2_mg = 50.0 * dosing_w
        p3_mg = 100.0 * dosing_w
        total_mg = p1_mg + p2_mg + p3_mg

        phases = [
            {
                "phase": 1,
                "name": "Loading Infusion",
                "dose_mg": p1_mg,
                "fluid": "200 mL D5W (or 0.45% NS)",
                "duration_hours": 1.0,
                "rate_ml_hr": 200.0,
                "rate_mg_hr": p1_mg,
            },
            {
                "phase": 2,
                "name": "Second Infusion",
                "dose_mg": p2_mg,
                "fluid": "500 mL D5W",
                "duration_hours": 4.0,
                "rate_ml_hr": 125.0,
                "rate_mg_hr": p2_mg / 4.0,
            },
            {
                "phase": 3,
                "name": "Third Infusion",
                "dose_mg": p3_mg,
                "fluid": "1000 mL D5W",
                "duration_hours": 16.0,
                "rate_ml_hr": 62.5,
                "rate_mg_hr": p3_mg / 16.0,
            },
        ]
        return NACProtocolPlan(
            route="IV (Standard 3-Bag / 21-Hour Protocol)",
            patient_weight_kg=weight_kg,
            dosing_weight_kg=dosing_w,
            total_duration_hours=21,
            total_dose_mg=total_mg,
            phases=phases,
            discontinuation_criteria=discon,
        )

    elif reg_clean in ("iv_2bag", "iv_20hour"):
        # Bag 1: 200 mg/kg over 4h; Bag 2: 100 mg/kg over 16h
        p1_mg = 200.0 * dosing_w
        p2_mg = 100.0 * dosing_w
        total_mg = p1_mg + p2_mg

        phases = [
            {
                "phase": 1,
                "name": "First Infusion",
                "dose_mg": p1_mg,
                "fluid": "200 mL D5W",
                "duration_hours": 4.0,
                "rate_ml_hr": 50.0,
                "rate_mg_hr": p1_mg / 4.0,
            },
            {
                "phase": 2,
                "name": "Second Infusion",
                "dose_mg": p2_mg,
                "fluid": "1000 mL D5W",
                "duration_hours": 16.0,
                "rate_ml_hr": 62.5,
                "rate_mg_hr": p2_mg / 16.0,
            },
        ]
        return NACProtocolPlan(
            route="IV (Modified 2-Bag / 20-Hour Protocol)",
            patient_weight_kg=weight_kg,
            dosing_weight_kg=dosing_w,
            total_duration_hours=20,
            total_dose_mg=total_mg,
            phases=phases,
            discontinuation_criteria=discon,
        )

    else:
        # Oral 72-Hour protocol: 140 mg/kg loading, then 70 mg/kg q4h x 17 doses
        load_mg = 140.0 * dosing_w
        maint_mg = 70.0 * dosing_w
        total_mg = load_mg + (maint_mg * 17)

        phases = [
            {
                "phase": 1,
                "name": "Oral Loading Dose",
                "dose_mg": load_mg,
                "route": "Oral / NG tube diluted to 5% with juice or soda",
                "frequency": "Once",
            },
            {
                "phase": 2,
                "name": "Oral Maintenance Doses",
                "dose_mg": maint_mg,
                "route": "Oral / NG tube diluted to 5%",
                "frequency": "Every 4 hours for 17 doses (total 18 doses over 72 hours)",
            },
        ]
        return NACProtocolPlan(
            route="Oral (72-Hour Protocol)",
            patient_weight_kg=weight_kg,
            dosing_weight_kg=dosing_w,
            total_duration_hours=72,
            total_dose_mg=total_mg,
            phases=phases,
            discontinuation_criteria=discon,
        )


def calculate_naloxone_plan(
    respiratory_rate: float,
    suspected_potent_synthetic: bool = False,
    apnea: bool = False,
) -> NaloxonePlan:
    """
    Titrated Naloxone dosing to restore adequate ventilation while preventing severe withdrawal.
    """
    if respiratory_rate >= 12.0 and not apnea:
        return NaloxonePlan(
            respiratory_rate=respiratory_rate,
            suspected_potent_synthetic=suspected_potent_synthetic,
            initial_dose_mg=0.0,
            route="Observation",
            titration_steps=["Maintain continuous pulse oximetry and capnography. Naloxone not indicated at current RR."],
            continuous_infusion_indicated=False,
            infusion_rate_mg_hr=None,
            clinical_guidance=["Goal is ventilation (RR 10-12 bpm), not full arousal."],
        )

    if apnea:
        init_dose = 0.4 if not suspected_potent_synthetic else 1.0
    elif suspected_potent_synthetic:
        init_dose = 0.4
    else:
        init_dose = 0.04  # Low dose titration to avoid acute withdrawal storm

    steps = [
        f"Administer {init_dose} mg IV push.",
        "Re-evaluate spontaneous respiratory rate and chest rise at 2-3 minutes.",
        "If RR remains < 10 bpm, double the dose (0.08 mg -> 0.2 mg -> 0.4 mg -> 2.0 mg).",
        "If severe fentanyl/nitazene chest wall rigidity ('wooden chest'), escalate rapidly to 2.0 - 4.0 mg IV.",
    ]

    infusion_needed = suspected_potent_synthetic
    infusion_rate = 0.4 if infusion_needed else None

    guidance = [
        "Goal of naloxone is adequate ventilation (RR > 10 bpm, SpO2 > 92%), NOT complete alertness.",
        "Naloxone half-life is 30-90 minutes; long-acting opioids (methadone, extended-release oxycodone/morphine, synthetic fentanyl) will outlast naloxone.",
        "If bolus requirement recurs within 1 hour, start continuous IV infusion at 2/3 of successful wake-up dose per hour.",
    ]

    return NaloxonePlan(
        respiratory_rate=respiratory_rate,
        suspected_potent_synthetic=suspected_potent_synthetic,
        initial_dose_mg=init_dose,
        route="IV push (IM / IN if no IV access: 2.0 - 4.0 mg IN)",
        titration_steps=steps,
        continuous_infusion_indicated=infusion_needed,
        infusion_rate_mg_hr=infusion_rate,
        clinical_guidance=guidance,
    )


def calculate_organophosphate_protocol(
    weight_kg: float,
    is_severe: bool = True,
) -> OrganophosphatePlan:
    """
    Calculate Atropine doubling protocol and Pralidoxime (2-PAM) dosing.
    """
    if weight_kg <= 0:
        raise ValueError("Patient weight must be positive")

    init_atropine = 2.0 if not is_severe else 3.0
    doubling = [init_atropine, init_atropine * 2, init_atropine * 4, init_atropine * 8]

    endpoints = [
        "Lungs clear to auscultation with complete drying of copious bronchial secretions (CRITICAL ENDPOINT)",
        "Resolution of severe bronchospasm and wheezing",
        "Heart rate > 80 bpm",
        "Systolic Blood Pressure > 90 mmHg",
        "Dry axillae and skin",
        "Note: Pupil size is an unreliable marker of adequate atropinization",
    ]

    # 2-PAM loading: 30 mg/kg (max 2000 mg) over 30 min, then 8-10 mg/kg/hr infusion
    pam_load = min(round(30.0 * weight_kg), 2000.0)
    pam_infusion = min(round(8.0 * weight_kg), 500.0)

    warnings = [
        "Atropine treats muscarinic symptoms (secretions, bronchospasm, bradycardia) but does NOT treat nicotinic muscle paralysis.",
        "Pralidoxime (2-PAM) reactivates acetylcholinesterase before irreversible 'aging' occurs (aging takes hours to days depending on pesticide/nerve agent).",
        "Do NOT administer succinylcholine for intubation due to prolonged paralysis from pseudocholinesterase inhibition.",
    ]

    return OrganophosphatePlan(
        weight_kg=weight_kg,
        atropine_starting_dose_mg=init_atropine,
        atropine_doubling_sequence_mg=doubling,
        atropinization_endpoints=endpoints,
        pralidoxime_loading_mg=pam_load,
        pralidoxime_infusion_mg_hr=pam_infusion,
        clinical_warnings=warnings,
    )


def evaluate_toxic_alcohol(
    toxicant: str,
    weight_kg: float,
    measured_osmolality: float,
    sodium: float,
    glucose_mg_dl: float,
    bun_mg_dl: float,
    ethanol_mg_dl: float = 0.0,
    bicarbonate_meq_l: float = 24.0,
    chloride_meq_l: float = 100.0,
    ph: float = 7.40,
) -> ToxicAlcoholPlan:
    """
    Calculate Osmolal Gap, Anion Gap, and Fomepizole / Hemodialysis indications.
    """
    # Calculated Osm = 2*Na + Glucose/18 + BUN/2.8 + Ethanol/4.6
    calc_osm = (2.0 * sodium) + (glucose_mg_dl / 18.0) + (bun_mg_dl / 2.8) + (ethanol_mg_dl / 4.6)
    osmolal_gap = measured_osmolality - calc_osm

    # Anion Gap = Na - (Cl + HCO3)
    anion_gap = sodium - (chloride_meq_l + bicarbonate_meq_l)

    fomepizole_indicated = (osmolal_gap > 10.0) or (anion_gap > 16.0) or (bicarbonate_meq_l < 18.0)

    fomep_load = round(15.0 * weight_kg, 1)
    fomep_maint = round(10.0 * weight_kg, 1)

    hd_triggers: List[str] = []
    if ph < 7.25:
        hd_triggers.append(f"Severe refractory metabolic acidosis (pH {ph:.2f} < 7.25)")
    if bicarbonate_meq_l < 10.0:
        hd_triggers.append(f"Severe base deficit (Bicarbonate {bicarbonate_meq_l:.1f} < 10 mEq/L)")
    if osmolal_gap > 25.0:
        hd_triggers.append(f"Markedly elevated osmolal gap ({osmolal_gap:.1f} mOsm/kg)")
    if toxicant.lower().startswith("meth"):
        hd_triggers.append("Visual changes / optic nerve impairment (Methanol)")

    hd_indicated = len(hd_triggers) > 0

    adjuncts = []
    if "meth" in toxicant.lower():
        adjuncts.append("Folinic acid (Leucovorin) 50 mg IV q4h (or Folic acid 50 mg IV q4h) to promote formic acid breakdown")
    elif "ethylene" in toxicant.lower():
        adjuncts.append("Thiamine 100 mg IV q6h and Pyridoxine 50 mg IV q6h to shunt glyoxylic acid into benign metabolites")

    return ToxicAlcoholPlan(
        toxicant=toxicant,
        measured_osmolality=round(measured_osmolality, 1),
        calculated_osmolarity=round(calc_osm, 1),
        osmolal_gap=round(osmolal_gap, 1),
        anion_gap=round(anion_gap, 1),
        fomepizole_indicated=fomepizole_indicated,
        fomepizole_loading_mg=fomep_load,
        fomepizole_maintenance_mg=fomep_maint,
        hemodialysis_indicated=hd_indicated,
        hemodialysis_triggers=hd_triggers,
        adjunctive_vitamins=adjuncts,
    )


def classify_toxidrome(
    heart_rate: float,
    systolic_bp: float,
    respiratory_rate: float,
    temperature_c: float,
    pupils: str,  # "miosis", "mydriasis", "normal"
    skin: str,    # "diaphoretic", "dry", "normal"
    bowel_sounds: str = "normal",  # "hypoactive", "hyperactive", "normal"
) -> ToxidromeClassification:
    """
    Classify presenting toxicology toxidrome based on vital sign clusters and physical exam.
    """
    pupils_c = pupils.lower()
    skin_c = skin.lower()
    bs_c = bowel_sounds.lower()

    # Scores for each toxidrome
    scores: Dict[ToxidromeType, int] = {t: 0 for t in ToxidromeType}
    features: Dict[ToxidromeType, List[str]] = {t: [] for t in ToxidromeType}

    # Cholinergic: Bradycardia/normal, miosis, diaphoretic/secretions, hyperactive bowel
    if pupils_c == "miosis":
        scores[ToxidromeType.CHOLINERGIC] += 3
        features[ToxidromeType.CHOLINERGIC].append("Miosis")
        scores[ToxidromeType.OPIOID] += 3
        features[ToxidromeType.OPIOID].append("Miosis")
    if skin_c == "diaphoretic":
        scores[ToxidromeType.CHOLINERGIC] += 2
        features[ToxidromeType.CHOLINERGIC].append("Diaphoresis / secretions")
        scores[ToxidromeType.SYMPATHOMIMETIC] += 3
        features[ToxidromeType.SYMPATHOMIMETIC].append("Diaphoresis")
        scores[ToxidromeType.SEROTONERGIC] += 2
        features[ToxidromeType.SEROTONERGIC].append("Diaphoresis")
    if bs_c == "hyperactive":
        scores[ToxidromeType.CHOLINERGIC] += 2
        features[ToxidromeType.CHOLINERGIC].append("Hyperactive bowel sounds / diarrhea")
        scores[ToxidromeType.SEROTONERGIC] += 2
        features[ToxidromeType.SEROTONERGIC].append("Hyperactive bowel sounds")

    # Opioid: Bradypnea, miosis, bradycardia, hypoactive bowel
    if respiratory_rate < 12.0:
        scores[ToxidromeType.OPIOID] += 4
        features[ToxidromeType.OPIOID].append(f"Depressed respiratory rate ({respiratory_rate:.0f} bpm)")
        scores[ToxidromeType.SEDATIVE_HYPNOTIC] += 2
        features[ToxidromeType.SEDATIVE_HYPNOTIC].append(f"Depressed respiratory rate ({respiratory_rate:.0f} bpm)")
    if heart_rate < 60.0:
        scores[ToxidromeType.OPIOID] += 2
        features[ToxidromeType.OPIOID].append(f"Bradycardia ({heart_rate:.0f} bpm)")
        scores[ToxidromeType.CHOLINERGIC] += 2
        features[ToxidromeType.CHOLINERGIC].append(f"Bradycardia ({heart_rate:.0f} bpm)")
    if bs_c == "hypoactive":
        scores[ToxidromeType.OPIOID] += 2
        features[ToxidromeType.OPIOID].append("Hypoactive bowel sounds")
        scores[ToxidromeType.ANTICHOLINERGIC] += 2
        features[ToxidromeType.ANTICHOLINERGIC].append("Hypoactive bowel sounds")
        scores[ToxidromeType.SEDATIVE_HYPNOTIC] += 2
        features[ToxidromeType.SEDATIVE_HYPNOTIC].append("Hypoactive bowel sounds")

    # Anticholinergic: Tachycardia, mydriasis, dry skin, hyperthermia, hypoactive bowel
    if pupils_c == "mydriasis":
        scores[ToxidromeType.ANTICHOLINERGIC] += 3
        features[ToxidromeType.ANTICHOLINERGIC].append("Mydriasis")
        scores[ToxidromeType.SYMPATHOMIMETIC] += 3
        features[ToxidromeType.SYMPATHOMIMETIC].append("Mydriasis")
    if skin_c == "dry":
        scores[ToxidromeType.ANTICHOLINERGIC] += 4
        features[ToxidromeType.ANTICHOLINERGIC].append("Dry, flushed skin and mucous membranes")
    if heart_rate > 100.0:
        scores[ToxidromeType.ANTICHOLINERGIC] += 2
        features[ToxidromeType.ANTICHOLINERGIC].append(f"Tachycardia ({heart_rate:.0f} bpm)")
        scores[ToxidromeType.SYMPATHOMIMETIC] += 3
        features[ToxidromeType.SYMPATHOMIMETIC].append(f"Tachycardia ({heart_rate:.0f} bpm)")
        scores[ToxidromeType.SEROTONERGIC] += 2
        features[ToxidromeType.SEROTONERGIC].append(f"Tachycardia ({heart_rate:.0f} bpm)")
    if systolic_bp > 140.0:
        scores[ToxidromeType.SYMPATHOMIMETIC] += 3
        features[ToxidromeType.SYMPATHOMIMETIC].append(f"Hypertension ({systolic_bp:.0f} mmHg)")
    if temperature_c > 38.0:
        scores[ToxidromeType.ANTICHOLINERGIC] += 2
        features[ToxidromeType.ANTICHOLINERGIC].append(f"Hyperthermia ({temperature_c:.1f} °C)")
        scores[ToxidromeType.SYMPATHOMIMETIC] += 2
        features[ToxidromeType.SYMPATHOMIMETIC].append(f"Hyperthermia ({temperature_c:.1f} °C)")
        scores[ToxidromeType.SEROTONERGIC] += 3
        features[ToxidromeType.SEROTONERGIC].append(f"Hyperthermia ({temperature_c:.1f} °C)")

    # Identify top toxidrome
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_type, top_score = sorted_scores[0]

    if top_score < 4:
        top_type = ToxidromeType.UNKNOWN
        conf = "Low"
    elif top_score >= 8:
        conf = "High"
    else:
        conf = "Moderate"

    antidote_map = {
        ToxidromeType.CHOLINERGIC: "Atropine (titrated to dry secretions) + Pralidoxime (2-PAM)",
        ToxidromeType.OPIOID: "Naloxone (titrated to spontaneous RR >= 10-12 bpm)",
        ToxidromeType.ANTICHOLINERGIC: "Physostigmine (1-2 mg IV slow push) or Benzodiazepines for agitation",
        ToxidromeType.SYMPATHOMIMETIC: "Benzodiazepines (Lorazepam/Diazepam IV) + active external cooling",
        ToxidromeType.SEDATIVE_HYPNOTIC: "Supportive airway management (Flumazenil generally avoided due to seizure risk)",
        ToxidromeType.SEROTONERGIC: "Cyproheptadine (12 mg PO load) + Benzodiazepines + Active Cooling",
        ToxidromeType.UNKNOWN: "Supportive ABC management; obtain APAP/Salicylate/ECG/Blood gas",
    }

    actions_map = {
        ToxidromeType.CHOLINERGIC: ["Decontamination / remove clothes", "Establish patent airway & suction secretions", "Initiate Atropine doubling"],
        ToxidromeType.OPIOID: ["Bag-valve-mask ventilation with 100% O2", "Administer low-dose titrated Naloxone", "Continuous capnography"],
        ToxidromeType.ANTICHOLINERGIC: ["ECG to assess QRS/QT prolongation", "Sedate with IV benzodiazepines", "Avoid physical restraints"],
        ToxidromeType.SYMPATHOMIMETIC: ["Aggressive IV benzodiazepines", "Active cooling for temperature > 38.5 C", "Avoid pure beta-blockers"],
        ToxidromeType.SEDATIVE_HYPNOTIC: ["Airway protection", "Evaluate for co-ingestants", "Supportive care"],
        ToxidromeType.SEROTONERGIC: ["Discontinue all serotonergic agents", "IV fluids and sedation", "Avoid antipyretics"],
        ToxidromeType.UNKNOWN: ["Evaluate Airway, Breathing, Circulation", "Check point-of-care glucose", "Order toxicology laboratory panel"],
    }

    diffs = [s[0].value for s in sorted_scores[1:4] if s[1] > 2]

    return ToxidromeClassification(
        primary_toxidrome=top_type,
        confidence=conf,
        matching_features=features[top_type],
        differentials=diffs,
        recommended_antidote=antidote_map[top_type],
        immediate_actions=actions_map[top_type],
    )
