#!/usr/bin/env python3
"""
Command-Line Interface for Medical Toxicology Antidote Dosing & Poisoning Agent.

Domain: Medical Toxicology, Emergency Medicine & Critical Care
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

import antidote_tox_poisoning as atp


def cmd_apap(args: argparse.Namespace) -> None:
    res = atp.evaluate_rumack_matthew(
        hours_post_ingestion=args.hours,
        apap_ug_ml=args.level,
        high_risk_patient=args.high_risk,
    )

    if args.json:
        out = {
            "hours_post_ingestion": res.hours_post_ingestion,
            "apap_ug_ml": res.apap_ug_ml,
            "treatment_threshold_150": res.treatment_threshold_150,
            "treatment_threshold_100": res.treatment_threshold_100,
            "risk_tier": res.risk_tier,
            "treat_with_nac": res.treat_with_nac,
            "clinical_rationale": res.clinical_rationale,
        }
        print(json.dumps(out, indent=2))
        return

    print("=" * 75)
    print("  ACETAMINOPHEN (APAP) RUMACK-MATTHEW NOMOGRAM")
    print(f"  Time Post-Ingestion: {res.hours_post_ingestion} hours | Level: {res.apap_ug_ml} ug/mL")
    print("=" * 75)
    print(f"  150-Treatment Line (US Standard): {res.treatment_threshold_150} ug/mL")
    print(f"  100-Treatment Line (High Risk):   {res.treatment_threshold_100} ug/mL")
    print(f"  Risk Category:                   {res.risk_tier}")
    print(f"  NAC Treatment Recommendation:    {'INITIATE NAC IMMEDIATELY' if res.treat_with_nac else 'DO NOT TREAT WITH NAC (Observe)'}")
    print(f"  Clinical Rationale:              {res.clinical_rationale}")
    print("=" * 75)


def cmd_nac(args: argparse.Namespace) -> None:
    plan = atp.calculate_nac_protocol(weight_kg=args.weight, regimen=args.regimen)

    if args.json:
        out = {
            "route": plan.route,
            "patient_weight_kg": plan.patient_weight_kg,
            "dosing_weight_kg": plan.dosing_weight_kg,
            "total_duration_hours": plan.total_duration_hours,
            "total_dose_mg": plan.total_dose_mg,
            "phases": plan.phases,
            "discontinuation_criteria": plan.discontinuation_criteria,
        }
        print(json.dumps(out, indent=2))
        return

    print("=" * 75)
    print(f"  N-ACETYLCYSTEINE (NAC) PROTOCOL: {plan.route.upper()}")
    print(f"  Patient Weight: {plan.patient_weight_kg} kg (Dosing Capped Weight: {plan.dosing_weight_kg} kg)")
    print(f"  Total Dose: {plan.total_dose_mg / 1000.0:.2f} g over {plan.total_duration_hours} hours")
    print("=" * 75)
    for p in plan.phases:
        print(f"  [Phase {p.get('phase', '')}: {p.get('name', '')}]")
        print(f"    - Dose: {p.get('dose_mg', 0) / 1000.0:.2f} g ({p.get('fluid', p.get('route', ''))})")
        if "duration_hours" in p:
            print(f"    - Duration: {p['duration_hours']} hours (Rate: {p.get('rate_ml_hr', '')} mL/hr)")
        elif "frequency" in p:
            print(f"    - Frequency: {p['frequency']}")
    print("\n  Discontinuation Criteria:")
    for crit in plan.discontinuation_criteria:
        print(f"    - {crit}")
    print("=" * 75)


def cmd_naloxone(args: argparse.Namespace) -> None:
    plan = atp.calculate_naloxone_plan(
        respiratory_rate=args.rr,
        suspected_potent_synthetic=args.synthetic,
        apnea=args.apnea,
    )

    if args.json:
        out = {
            "respiratory_rate": plan.respiratory_rate,
            "suspected_potent_synthetic": plan.suspected_potent_synthetic,
            "initial_dose_mg": plan.initial_dose_mg,
            "route": plan.route,
            "titration_steps": plan.titration_steps,
            "continuous_infusion_indicated": plan.continuous_infusion_indicated,
            "infusion_rate_mg_hr": plan.infusion_rate_mg_hr,
            "clinical_guidance": plan.clinical_guidance,
        }
        print(json.dumps(out, indent=2))
        return

    print("=" * 75)
    print("  NALOXONE TITRATION & OPIOID RESUSCITATION PLAN")
    print(f"  Presenting RR: {plan.respiratory_rate} bpm | Synthetic Risk: {plan.suspected_potent_synthetic}")
    print("=" * 75)
    print(f"  Initial Dose:      {plan.initial_dose_mg} mg via {plan.route}")
    print("  Titration Steps:")
    for step in plan.titration_steps:
        print(f"    - {step}")
    if plan.continuous_infusion_indicated:
        print(f"  Continuous Infusion: Indicated ({plan.infusion_rate_mg_hr} mg/hr IV)")
    print("\n  Clinical Guidance:")
    for g in plan.clinical_guidance:
        print(f"    - {g}")
    print("=" * 75)


def cmd_organophosphate(args: argparse.Namespace) -> None:
    plan = atp.calculate_organophosphate_protocol(weight_kg=args.weight, is_severe=args.severe)

    if args.json:
        out = {
            "weight_kg": plan.weight_kg,
            "atropine_starting_dose_mg": plan.atropine_starting_dose_mg,
            "atropine_doubling_sequence_mg": plan.atropine_doubling_sequence_mg,
            "atropinization_endpoints": plan.atropinization_endpoints,
            "pralidoxime_loading_mg": plan.pralidoxime_loading_mg,
            "pralidoxime_infusion_mg_hr": plan.pralidoxime_infusion_mg_hr,
            "clinical_warnings": plan.clinical_warnings,
        }
        print(json.dumps(out, indent=2))
        return

    print("=" * 75)
    print("  ORGANOPHOSPHATE / CHOLINERGIC CRISIS MANAGEMENT")
    print(f"  Patient Weight: {plan.weight_kg} kg")
    print("=" * 75)
    print(f"  ATROPINE STARTING DOSE: {plan.atropine_starting_dose_mg} mg IV")
    print(f"  Doubling Sequence:      {plan.atropine_doubling_sequence_mg} mg every 3-5 minutes until dry")
    print(f"  PRALIDOXIME (2-PAM):    {plan.pralidoxime_loading_mg} mg IV load, then {plan.pralidoxime_infusion_mg_hr} mg/hr infusion")
    print("\n  Critical Endpoints of Atropinization:")
    for ep in plan.atropinization_endpoints:
        print(f"    - {ep}")
    print("\n  Clinical Warnings:")
    for w in plan.clinical_warnings:
        print(f"    - {w}")
    print("=" * 75)


def cmd_toxic_alcohol(args: argparse.Namespace) -> None:
    plan = atp.evaluate_toxic_alcohol(
        toxicant=args.toxicant,
        weight_kg=args.weight,
        measured_osmolality=args.measured_osm,
        sodium=args.na,
        glucose_mg_dl=args.glucose,
        bun_mg_dl=args.bun,
        ethanol_mg_dl=args.ethanol,
        bicarbonate_meq_l=args.hco3,
        chloride_meq_l=args.cl,
        ph=args.ph,
    )

    if args.json:
        out = {
            "toxicant": plan.toxicant,
            "measured_osmolality": plan.measured_osmolality,
            "calculated_osmolarity": plan.calculated_osmolarity,
            "osmolal_gap": plan.osmolal_gap,
            "anion_gap": plan.anion_gap,
            "fomepizole_indicated": plan.fomepizole_indicated,
            "fomepizole_loading_mg": plan.fomepizole_loading_mg,
            "fomepizole_maintenance_mg": plan.fomepizole_maintenance_mg,
            "hemodialysis_indicated": plan.hemodialysis_indicated,
            "hemodialysis_triggers": plan.hemodialysis_triggers,
            "adjunctive_vitamins": plan.adjunctive_vitamins,
        }
        print(json.dumps(out, indent=2))
        return

    print("=" * 75)
    print(f"  TOXIC ALCOHOL EVALUATION: {plan.toxicant.upper()}")
    print("=" * 75)
    print(f"  Measured Osmolality:   {plan.measured_osmolality} mOsm/kg")
    print(f"  Calculated Osmolarity: {plan.calculated_osmolarity} mOsm/L")
    print(f"  Osmolal Gap:           {plan.osmolal_gap} mOsm/kg (Normal <= 10)")
    print(f"  Anion Gap:             {plan.anion_gap} mEq/L (Normal 8-12)")
    print(f"  Fomepizole Indication: {'INDICATED' if plan.fomepizole_indicated else 'NOT INDICATED'}")
    if plan.fomepizole_indicated:
        print(f"    - Loading Dose:      {plan.fomepizole_loading_mg} mg IV (15 mg/kg)")
        print(f"    - Maintenance:       {plan.fomepizole_maintenance_mg} mg IV q12h (10 mg/kg)")
    print(f"  Hemodialysis Status:   {'EMERGENT HEMODIALYSIS INDICATED' if plan.hemodialysis_indicated else 'Not currently triggered'}")
    for trig in plan.hemodialysis_triggers:
        print(f"    * {trig}")
    if plan.adjunctive_vitamins:
        print("\n  Cofactor Therapy:")
        for v in plan.adjunctive_vitamins:
            print(f"    - {v}")
    print("=" * 75)


def cmd_toxidrome(args: argparse.Namespace) -> None:
    res = atp.classify_toxidrome(
        heart_rate=args.hr,
        systolic_bp=args.sbp,
        respiratory_rate=args.rr,
        temperature_c=args.temp,
        pupils=args.pupils,
        skin=args.skin,
        bowel_sounds=args.bowel_sounds,
    )

    if args.json:
        out = {
            "primary_toxidrome": res.primary_toxidrome.value,
            "confidence": res.confidence,
            "matching_features": res.matching_features,
            "differentials": res.differentials,
            "recommended_antidote": res.recommended_antidote,
            "immediate_actions": res.immediate_actions,
        }
        print(json.dumps(out, indent=2))
        return

    print("=" * 75)
    print("  TOXIDROME DIAGNOSTIC CLASSIFIER")
    print(f"  Identified Toxidrome: {res.primary_toxidrome.value.upper()} (Confidence: {res.confidence})")
    print("=" * 75)
    print("  Matching Physical Findings:")
    for f in res.matching_features:
        print(f"    - {f}")
    if res.differentials:
        print(f"  Differential Considerations: {', '.join(res.differentials)}")
    print(f"\n  Recommended Antidote / Therapy: {res.recommended_antidote}")
    print("  Immediate Resuscitation Actions:")
    for a in res.immediate_actions:
        print(f"    - {a}")
    print("=" * 75)


def cmd_interactive() -> None:
    print("\n--- Medical Toxicology & Poisoning Interactive Console ---")
    print("Select diagnostic / antidote tool:")
    print("1. Acetaminophen (APAP) Rumack-Matthew Nomogram")
    print("2. N-Acetylcysteine (NAC) Dosing Calculator")
    print("3. Opioid Naloxone Titration Plan")
    print("4. Organophosphate / Cholinergic Poisoning Protocol")
    print("5. Toxic Alcohol Osmolal Gap & Fomepizole Engine")
    print("6. Physical Exam Toxidrome Classifier")

    choice = input("\nSelect choice [1-6]: ").strip()

    if choice == "1":
        hours = float(input("Hours post acute ingestion [e.g. 6.0]: ") or "6.0")
        level = float(input("APAP level in ug/mL [e.g. 140.0]: ") or "140.0")
        res = atp.evaluate_rumack_matthew(hours, level)
        print(f"\nResult: Threshold = {res.treatment_threshold_150} ug/mL -> {res.risk_tier} -> {'TREAT WITH NAC' if res.treat_with_nac else 'OBSERVE'}")
    elif choice == "2":
        w = float(input("Patient weight in kg [e.g. 70]: ") or "70")
        plan = atp.calculate_nac_protocol(w, "iv_3bag")
        print(f"\nResult: Total NAC Dose = {plan.total_dose_mg/1000:.2f} g IV over 21 hours.")
    elif choice == "3":
        rr = float(input("Respiratory rate [e.g. 6]: ") or "6")
        plan = atp.calculate_naloxone_plan(rr)
        print(f"\nResult: Start {plan.initial_dose_mg} mg IV push, titrate every 2-3 min to RR >= 10.")
    elif choice == "4":
        w = float(input("Patient weight in kg [e.g. 75]: ") or "75")
        plan = atp.calculate_organophosphate_protocol(w)
        print(f"\nResult: Start Atropine {plan.atropine_starting_dose_mg} mg IV, double every 3-5 min to dry lungs. 2-PAM: {plan.pralidoxime_loading_mg} mg IV load.")
    elif choice == "5":
        w = float(input("Weight kg [e.g. 70]: ") or "70")
        osm = float(input("Measured Osmolality [e.g. 330]: ") or "330")
        na = float(input("Sodium [e.g. 140]: ") or "140")
        glu = float(input("Glucose [e.g. 100]: ") or "100")
        bun = float(input("BUN [e.g. 14]: ") or "14")
        plan = atp.evaluate_toxic_alcohol("ethylene_glycol", w, osm, na, glu, bun)
        print(f"\nResult: Osmolal Gap = {plan.osmolal_gap} mOsm/kg. Fomepizole: {'GIVE ' + str(plan.fomepizole_loading_mg) + ' mg' if plan.fomepizole_indicated else 'NOT INDICATED'}")
    elif choice == "6":
        hr = float(input("Heart rate [e.g. 120]: ") or "120")
        sbp = float(input("SBP [e.g. 150]: ") or "150")
        rr = float(input("RR [e.g. 22]: ") or "22")
        temp = float(input("Temp C [e.g. 38.5]: ") or "38.5")
        pupils = input("Pupils (miosis/mydriasis/normal) [mydriasis]: ").strip() or "mydriasis"
        skin = input("Skin (dry/diaphoretic/normal) [dry]: ").strip() or "dry"
        res = atp.classify_toxidrome(hr, sbp, rr, temp, pupils, skin)
        print(f"\nResult: Classified Toxidrome = {res.primary_toxidrome.value.upper()} ({res.confidence} confidence). Antidote: {res.recommended_antidote}")
    else:
        print("Invalid selection.")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="antidote-tox-poisoning-agent",
        description="Medical Toxicology Decision Support & Antidote Dosing Engine",
    )
    subparsers = parser.add_subparsers(dest="command")

    # apap
    p_apap = subparsers.add_parser("apap", help="Acetaminophen Rumack-Matthew nomogram evaluation")
    p_apap.add_argument("--hours", type=float, required=True, help="Hours post ingestion")
    p_apap.add_argument("--level", type=float, required=True, help="Serum APAP in ug/mL")
    p_apap.add_argument("--high-risk", action="store_true", help="High risk patient (use 100-line)")
    p_apap.add_argument("--json", action="store_true", help="JSON output")

    # nac
    p_nac = subparsers.add_parser("nac", help="N-Acetylcysteine weight-based dosing")
    p_nac.add_argument("--weight", type=float, required=True, help="Patient weight in kg")
    p_nac.add_argument("--regimen", choices=["iv_3bag", "iv_2bag", "oral"], default="iv_3bag")
    p_nac.add_argument("--json", action="store_true", help="JSON output")

    # naloxone
    p_nal = subparsers.add_parser("naloxone", help="Naloxone titration for opioid overdose")
    p_nal.add_argument("--rr", type=float, required=True, help="Respiratory rate")
    p_nal.add_argument("--synthetic", action="store_true", help="Suspected fentanyl/synthetic")
    p_nal.add_argument("--apnea", action="store_true", help="Patient is apneic")
    p_nal.add_argument("--json", action="store_true", help="JSON output")

    # organophosphate
    p_op = subparsers.add_parser("organophosphate", help="Atropine / Pralidoxime for cholinergic toxicity")
    p_op.add_argument("--weight", type=float, required=True, help="Patient weight in kg")
    p_op.add_argument("--severe", action="store_true", default=True, help="Severe poisoning")
    p_op.add_argument("--json", action="store_true", help="JSON output")

    # toxic-alcohol
    p_ta = subparsers.add_parser("toxic-alcohol", help="Osmolal gap and Fomepizole evaluation")
    p_ta.add_argument("--toxicant", choices=["methanol", "ethylene_glycol", "isopropanol"], default="ethylene_glycol")
    p_ta.add_argument("--weight", type=float, required=True, help="Patient weight in kg")
    p_ta.add_argument("--measured-osm", type=float, required=True, help="Measured osmolality mOsm/kg")
    p_ta.add_argument("--na", type=float, required=True, help="Sodium mEq/L")
    p_ta.add_argument("--glucose", type=float, default=100.0, help="Glucose mg/dL")
    p_ta.add_argument("--bun", type=float, default=15.0, help="BUN mg/dL")
    p_ta.add_argument("--ethanol", type=float, default=0.0, help="Ethanol mg/dL")
    p_ta.add_argument("--hco3", type=float, default=24.0, help="Bicarbonate mEq/L")
    p_ta.add_argument("--cl", type=float, default=100.0, help="Chloride mEq/L")
    p_ta.add_argument("--ph", type=float, default=7.40, help="Arterial pH")
    p_ta.add_argument("--json", action="store_true", help="JSON output")

    # toxidrome
    p_tox = subparsers.add_parser("toxidrome", help="Classify clinical toxidrome from physical exam")
    p_tox.add_argument("--hr", type=float, required=True, help="Heart rate bpm")
    p_tox.add_argument("--sbp", type=float, required=True, help="Systolic BP mmHg")
    p_tox.add_argument("--rr", type=float, required=True, help="Respiratory rate bpm")
    p_tox.add_argument("--temp", type=float, required=True, help="Temperature Celsius")
    p_tox.add_argument("--pupils", choices=["miosis", "mydriasis", "normal"], required=True)
    p_tox.add_argument("--skin", choices=["dry", "diaphoretic", "normal"], required=True)
    p_tox.add_argument("--bowel-sounds", choices=["hypoactive", "hyperactive", "normal"], default="normal")
    p_tox.add_argument("--json", action="store_true", help="JSON output")

    # interactive
    subparsers.add_parser("interactive", help="Interactive toxicology walkthrough")

    args = parser.parse_args(argv)

    if args.command == "apap":
        cmd_apap(args)
    elif args.command == "nac":
        cmd_nac(args)
    elif args.command == "naloxone":
        cmd_naloxone(args)
    elif args.command == "organophosphate":
        cmd_organophosphate(args)
    elif args.command == "toxic-alcohol":
        cmd_toxic_alcohol(args)
    elif args.command == "toxidrome":
        cmd_toxidrome(args)
    elif args.command == "interactive":
        cmd_interactive()
    else:
        parser.print_help()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
