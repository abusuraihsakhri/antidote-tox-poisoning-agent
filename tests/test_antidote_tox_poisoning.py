#!/usr/bin/env python3
"""
Comprehensive Unit Test Suite for Medical Toxicology Antidote Dosing & Decision Support.
"""

import unittest
from antidote_tox_poisoning import (
    evaluate_rumack_matthew,
    calculate_nac_protocol,
    calculate_naloxone_plan,
    calculate_organophosphate_protocol,
    evaluate_toxic_alcohol,
    classify_toxidrome,
    ToxidromeType,
    RumackResult,
    NACProtocolPlan,
    NaloxonePlan,
    OrganophosphatePlan,
    ToxicAlcoholPlan,
    ToxidromeClassification,
)


class TestAntidoteToxPoisoning(unittest.TestCase):

    # 1. Rumack-Matthew Nomogram
    def test_rumack_matthew_at_4h_threshold(self):
        # Exactly at 4h, 150 ug/mL is the threshold
        res = evaluate_rumack_matthew(hours_post_ingestion=4.0, apap_ug_ml=150.0)
        self.assertEqual(res.treatment_threshold_150, 150.0)
        self.assertTrue(res.treat_with_nac)
        self.assertIn("Above 150-Line", res.risk_tier)

    def test_rumack_matthew_at_8h_half_life(self):
        # At 8h (1 half life after 4h), 150 * 0.5 = 75.0 ug/mL
        res = evaluate_rumack_matthew(hours_post_ingestion=8.0, apap_ug_ml=80.0)
        self.assertAlmostEqual(res.treatment_threshold_150, 75.0, places=1)
        self.assertTrue(res.treat_with_nac)

    def test_rumack_matthew_below_line(self):
        # At 8h, 40 ug/mL is well below 75 ug/mL
        res = evaluate_rumack_matthew(hours_post_ingestion=8.0, apap_ug_ml=40.0)
        self.assertFalse(res.treat_with_nac)
        self.assertIn("Below Treatment Line", res.risk_tier)

    def test_rumack_matthew_high_risk_100_line(self):
        # At 4h, level is 120 ug/mL (between 100 and 150). In high-risk patient -> treat!
        res_standard = evaluate_rumack_matthew(hours_post_ingestion=4.0, apap_ug_ml=120.0, high_risk_patient=False)
        self.assertFalse(res_standard.treat_with_nac)

        res_high_risk = evaluate_rumack_matthew(hours_post_ingestion=4.0, apap_ug_ml=120.0, high_risk_patient=True)
        self.assertTrue(res_high_risk.treat_with_nac)
        self.assertIn("High Risk (Above 100-Line)", res_high_risk.risk_tier)

    def test_rumack_matthew_before_4h_raises(self):
        with self.assertRaises(ValueError):
            evaluate_rumack_matthew(hours_post_ingestion=2.5, apap_ug_ml=200.0)

    def test_rumack_matthew_delayed_over_24h(self):
        res = evaluate_rumack_matthew(hours_post_ingestion=28.0, apap_ug_ml=15.0)
        self.assertTrue(res.treat_with_nac)
        self.assertEqual(res.risk_tier, "Delayed Presentation (>24h)")

    # 2. N-Acetylcysteine (NAC) Dosing
    def test_nac_iv_3bag_standard(self):
        # 70 kg -> 150 mg/kg (10.5g) + 50 mg/kg (3.5g) + 100 mg/kg (7.0g) = 21.0 g total
        plan = calculate_nac_protocol(weight_kg=70.0, regimen="iv_3bag")
        self.assertEqual(plan.total_duration_hours, 21)
        self.assertEqual(plan.dosing_weight_kg, 70.0)
        self.assertEqual(plan.total_dose_mg, 21000.0)
        self.assertEqual(len(plan.phases), 3)
        self.assertEqual(plan.phases[0]["dose_mg"], 10500.0)
        self.assertEqual(plan.phases[1]["dose_mg"], 3500.0)
        self.assertEqual(plan.phases[2]["dose_mg"], 7000.0)

    def test_nac_iv_weight_capping_at_100kg(self):
        # 140 kg patient -> dosing weight strictly capped at 100 kg
        plan = calculate_nac_protocol(weight_kg=140.0, regimen="iv_3bag")
        self.assertEqual(plan.dosing_weight_kg, 100.0)
        self.assertEqual(plan.total_dose_mg, 30000.0)
        self.assertEqual(plan.phases[0]["dose_mg"], 15000.0)

    def test_nac_iv_2bag_protocol(self):
        # 80 kg -> 200 mg/kg (16g) + 100 mg/kg (8g) = 24.0 g over 20h
        plan = calculate_nac_protocol(weight_kg=80.0, regimen="iv_2bag")
        self.assertEqual(plan.total_duration_hours, 20)
        self.assertEqual(plan.total_dose_mg, 24000.0)
        self.assertEqual(len(plan.phases), 2)

    def test_nac_oral_72hour_protocol(self):
        # 50 kg -> 140 mg/kg load (7000 mg) + 70 mg/kg x 17 (3500 x 17 = 59500 mg) = 66500 mg
        plan = calculate_nac_protocol(weight_kg=50.0, regimen="oral")
        self.assertEqual(plan.total_duration_hours, 72)
        self.assertEqual(plan.total_dose_mg, 66500.0)

    def test_nac_invalid_weight_raises(self):
        with self.assertRaises(ValueError):
            calculate_nac_protocol(weight_kg=-10.0)

    # 3. Naloxone Titration
    def test_naloxone_normal_rr_observation(self):
        plan = calculate_naloxone_plan(respiratory_rate=14.0)
        self.assertEqual(plan.initial_dose_mg, 0.0)
        self.assertFalse(plan.continuous_infusion_indicated)

    def test_naloxone_depressed_rr_low_dose(self):
        # RR 6 bpm -> Start 0.04 mg IV
        plan = calculate_naloxone_plan(respiratory_rate=6.0, suspected_potent_synthetic=False)
        self.assertEqual(plan.initial_dose_mg, 0.04)
        self.assertFalse(plan.continuous_infusion_indicated)

    def test_naloxone_synthetic_fentanyl_risk(self):
        plan = calculate_naloxone_plan(respiratory_rate=4.0, suspected_potent_synthetic=True)
        self.assertEqual(plan.initial_dose_mg, 0.4)
        self.assertTrue(plan.continuous_infusion_indicated)

    def test_naloxone_apnea_resuscitation(self):
        plan = calculate_naloxone_plan(respiratory_rate=0.0, apnea=True)
        self.assertGreaterEqual(plan.initial_dose_mg, 0.4)

    # 4. Organophosphates & Cholinergic Crisis
    def test_organophosphate_protocol_dosing(self):
        # 70 kg patient
        plan = calculate_organophosphate_protocol(weight_kg=70.0, is_severe=True)
        self.assertEqual(plan.atropine_starting_dose_mg, 3.0)
        self.assertEqual(plan.atropine_doubling_sequence_mg, [3.0, 6.0, 12.0, 24.0])
        # 2-PAM: 30 mg/kg * 70 kg = 2100 mg -> capped at 2000 mg
        self.assertEqual(plan.pralidoxime_loading_mg, 2000.0)
        # 2-PAM Infusion: 8 mg/kg * 70 kg = 560 mg/hr -> capped at 500 mg/hr
        self.assertEqual(plan.pralidoxime_infusion_mg_hr, 500.0)

    # 5. Toxic Alcohols & Osmolal Gap
    def test_toxic_alcohol_osmolal_gap_calculation(self):
        # Na 140, Glu 90 (5), BUN 14 (5), EtOH 0 -> Calc Osm = 280 + 5 + 5 = 290
        # Measured Osm = 320 -> Gap = 30 mOsm/kg (Elevated!)
        plan = evaluate_toxic_alcohol(
            toxicant="ethylene_glycol",
            weight_kg=70.0,
            measured_osmolality=320.0,
            sodium=140.0,
            glucose_mg_dl=90.0,
            bun_mg_dl=14.0,
            ph=7.30,
        )
        self.assertAlmostEqual(plan.calculated_osmolarity, 290.0, places=1)
        self.assertAlmostEqual(plan.osmolal_gap, 30.0, places=1)
        self.assertTrue(plan.fomepizole_indicated)
        self.assertEqual(plan.fomepizole_loading_mg, 1050.0)

    def test_toxic_alcohol_severe_acidosis_dialysis(self):
        plan = evaluate_toxic_alcohol(
            toxicant="methanol",
            weight_kg=80.0,
            measured_osmolality=340.0,
            sodium=135.0,
            glucose_mg_dl=108.0,
            bun_mg_dl=28.0,
            bicarbonate_meq_l=6.0,
            ph=7.10,
        )
        self.assertTrue(plan.hemodialysis_indicated)
        self.assertTrue(any("pH" in t for t in plan.hemodialysis_triggers))
        self.assertTrue(any("Leucovorin" in a or "Folinic" in a for a in plan.adjunctive_vitamins))

    # 6. Toxidrome Classification
    def test_toxidrome_anticholinergic(self):
        res = classify_toxidrome(
            heart_rate=130.0,
            systolic_bp=135.0,
            respiratory_rate=18.0,
            temperature_c=38.8,
            pupils="mydriasis",
            skin="dry",
            bowel_sounds="hypoactive",
        )
        self.assertEqual(res.primary_toxidrome, ToxidromeType.ANTICHOLINERGIC)
        self.assertEqual(res.confidence, "High")
        self.assertIn("Physostigmine", res.recommended_antidote)

    def test_toxidrome_cholinergic(self):
        res = classify_toxidrome(
            heart_rate=48.0,
            systolic_bp=100.0,
            respiratory_rate=20.0,
            temperature_c=36.5,
            pupils="miosis",
            skin="diaphoretic",
            bowel_sounds="hyperactive",
        )
        self.assertEqual(res.primary_toxidrome, ToxidromeType.CHOLINERGIC)
        self.assertIn("Atropine", res.recommended_antidote)

    def test_toxidrome_opioid(self):
        res = classify_toxidrome(
            heart_rate=52.0,
            systolic_bp=95.0,
            respiratory_rate=6.0,
            temperature_c=36.0,
            pupils="miosis",
            skin="normal",
            bowel_sounds="hypoactive",
        )
        self.assertEqual(res.primary_toxidrome, ToxidromeType.OPIOID)
        self.assertIn("Naloxone", res.recommended_antidote)

    def test_toxidrome_sympathomimetic(self):
        res = classify_toxidrome(
            heart_rate=145.0,
            systolic_bp=180.0,
            respiratory_rate=24.0,
            temperature_c=39.0,
            pupils="mydriasis",
            skin="diaphoretic",
            bowel_sounds="normal",
        )
        self.assertEqual(res.primary_toxidrome, ToxidromeType.SYMPATHOMIMETIC)
        self.assertIn("Benzodiazepines", res.recommended_antidote)

    # 7. Additional Edge & Corner Cases
    def test_sedative_hypnotic_toxidrome(self):
        res = classify_toxidrome(
            heart_rate=65.0,
            systolic_bp=100.0,
            respiratory_rate=8.0,
            temperature_c=36.2,
            pupils="normal",
            skin="normal",
            bowel_sounds="hypoactive",
        )
        self.assertIn(res.primary_toxidrome, [ToxidromeType.SEDATIVE_HYPNOTIC, ToxidromeType.OPIOID])

    def test_serotonergic_toxidrome(self):
        res = classify_toxidrome(
            heart_rate=125.0,
            systolic_bp=130.0,
            respiratory_rate=20.0,
            temperature_c=39.2,
            pupils="normal",
            skin="diaphoretic",
            bowel_sounds="hyperactive",
        )
        self.assertEqual(res.primary_toxidrome, ToxidromeType.SEROTONERGIC)
        self.assertIn("Cyproheptadine", res.recommended_antidote)

    def test_toxic_alcohol_normal_gap(self):
        # Na 140, Glu 90, BUN 14 -> Calc Osm = 290. Measured = 294 -> Gap = 4 (Normal)
        plan = evaluate_toxic_alcohol("ethylene_glycol", 70.0, 294.0, 140.0, 90.0, 14.0)
        self.assertEqual(plan.osmolal_gap, 4.0)
        self.assertFalse(plan.fomepizole_indicated)

    def test_nac_duration_hours(self):
        plan3 = calculate_nac_protocol(70.0, "iv_3bag")
        self.assertEqual(plan3.total_duration_hours, 21)
        plan2 = calculate_nac_protocol(70.0, "iv_2bag")
        self.assertEqual(plan2.total_duration_hours, 20)

    def test_cli_execution_smoke(self):
        from cli import main
        import io
        from unittest.mock import patch
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = main(["apap", "--hours", "4.0", "--level", "160", "--json"])
            self.assertEqual(code, 0)
            self.assertIn("Above 150-Line", fake_out.getvalue())

    def test_cli_batch(self):
        from cli import main
        import os
        import tempfile
        sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample.csv")
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "out_batch.csv")
            code = main(["batch", "-i", sample_path, "-o", out_file])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(out_file))


if __name__ == "__main__":
    unittest.main()

