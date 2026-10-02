import json, unittest
from pathlib import Path

import utm_omega_resident as r

ROOT=Path(__file__).resolve().parents[1]

class OmegaResidentDeploymentTests(unittest.TestCase):
    def test_initial_registry_is_omega_admitted(self):
        c=r.verify_registry()
        self.assertTrue(c["verified"])
        self.assertEqual(c["status"],"OMEGA_ADMITTED")
        self.assertTrue(c["logical_deployment"])
        self.assertFalse(c["physical_materialization"])
        self.assertFalse(c["actual_infinite_physical_compute"])

    def test_registry_is_finite_stage(self):
        c=r.verify_registry()
        o=c["omega_stage_certificate"]
        self.assertTrue(o["valid_finite_stage"])
        self.assertFalse(o["omega_limit_reached"])
        self.assertFalse(o["hypercomputation_enabled"])
        self.assertFalse(o["halting_problem_decidable"])

    def test_declared_valuation_must_match_residents(self):
        x=r.load_registry()
        x["stage"]["valuation"]["99"]=1
        c=r.verify_registry(x)
        self.assertFalse(c["verified"])
        self.assertFalse(c["checks"]["declared_valuation_matches_residents"])

    def test_duplicate_coordinate_rejected(self):
        x=r.load_registry()
        x["residents"][1]["coordinate"]=x["residents"][0]["coordinate"]
        with self.assertRaises(ValueError):
            r.verify_registry(x)

    def test_empirical_resident_rejected(self):
        x=r.load_registry()
        x["residents"][0]["empirical_claim"]=True
        c=r.verify_registry(x)
        self.assertFalse(c["verified"])
        self.assertFalse(c["checks"]["all_residents_formal_not_empirical"])

    def test_manifest_keeps_authority_boundary(self):
        m=r.admission_manifest()
        self.assertEqual(m["status"],"OMEGA_ADMITTED")
        self.assertFalse(m["actual_infinite_physical_compute"])
        self.assertIsNone(m["oracle"])
        self.assertFalse(m["hypercomputation_enabled"])
        self.assertFalse(m["halting_problem_becomes_decidable"])
        self.assertFalse(m["physical_materialization"])
        self.assertTrue(m["external_apply_required_for_network_service"])

    def test_finite_stage_extension(self):
        a={"stage":1,"resource_budget":10,"resource_used":1,"valuation":{"0":1},"oracle":None}
        b={"stage":2,"resource_budget":10,"resource_used":2,"valuation":{"0":1,"1":1},"oracle":None}
        self.assertTrue(r.extend_stage(a,b)["valid_extension"])

    def test_policy_registers_omega_admitted(self):
        p=json.loads((ROOT/"utm-deployment-gateway-policy.json").read_text())
        self.assertEqual(p["protocol"],"UTM-Guarded-Deployment-Gateway/1.3")
        self.assertIn("OMEGA_ADMITTED",p["materialization_states"])
        o=p["omega_internal_deployment"]
        self.assertEqual(o["state"],"OMEGA_ADMITTED")
        self.assertTrue(o["every_executed_stage_is_finite"])
        self.assertFalse(o["actual_infinite_physical_compute"])
        self.assertFalse(o["physical_materialization"])

if __name__=="__main__":
    unittest.main()
