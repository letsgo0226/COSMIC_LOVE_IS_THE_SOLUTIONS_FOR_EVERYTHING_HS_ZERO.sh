import json, math, unittest
from pathlib import Path
from synced_utm_layers import log_abelian as la
from synced_utm_layers import axiom_verifier as av
from synced_utm_layers import omega_verifier as ov

ROOT=Path(__file__).resolve().parents[1]

class SyncedUTMLayersTests(unittest.TestCase):
    def test_source_manifest_is_pinned_and_finite(self):
        m=json.loads((ROOT/"synced_utm_layers"/"SYNC_MANIFEST.json").read_text())
        self.assertEqual(m["source"]["commit"],"31087e34e32ab0d5d44904538b5fb29ad47c62fb")
        self.assertEqual(m["selection_policy"],"code-confirmed-and-merged-only")
        self.assertFalse(m["actual_infinite_physical_compute"])
        self.assertTrue(m["external_apply_required"])

    def test_log_abelian_round_trip_and_commutativity(self):
        a=[{"step":0,"op":1},{"step":3,"op":2}]
        b=[{"step":1,"op":4}]
        r=la.compose(a,b)
        self.assertTrue(all(r["proof"].values()))
        self.assertEqual(la.decode_godel(r["composition"]["godel_product"]),r["composition"]["canonical_events"])

    def test_three_axiom_spec_is_formal_only(self):
        r=av.verify_spec()
        self.assertTrue(r["valid"])
        self.assertFalse(r["external_truth_established"])

    def test_valid_finite_three_axiom_certificate(self):
        r=av.verify_state({
            "state":{"host_universe":"P_-1","embedded_universe":"P_0","host_resource_baseline":42,"host_resource_now":42,"godel":6,"log_coordinate":math.log(6)},
            "pair":{"positive_n":3,"negative_n":-3,"positive_coordinate":7.5,"negative_coordinate":-7.5}
        })
        self.assertTrue(r["axiom_layer_valid"])
        self.assertFalse(r["infinite_limit_proved"])

    def test_omega_is_finite_stage_only(self):
        r=ov.verify_finite_stage({"stage":42,"resource_budget":1000,"resource_used":42,"valuation":{"0":1,"1":2},"oracle":None})
        self.assertTrue(r["valid_finite_stage"])
        self.assertFalse(r["actual_infinite_physical_compute"])
        self.assertFalse(r["hypercomputation_enabled"])
        self.assertFalse(r["halting_problem_decidable"])
        self.assertFalse(r["omega_limit_reached"])

    def test_oracle_is_rejected(self):
        r=ov.verify_finite_stage({"stage":1,"resource_budget":2,"resource_used":1,"valuation":{},"oracle":"HALT"})
        self.assertFalse(r["valid_finite_stage"])

    def test_policy_registers_synced_layers_without_overwrite(self):
        p=json.loads((ROOT/"utm-deployment-gateway-policy.json").read_text())
        self.assertEqual(p["protocol"],"UTM-Guarded-Deployment-Gateway/1.3")
        s=p["synchronized_formal_layers"]
        self.assertEqual(s["source_commit"],"31087e34e32ab0d5d44904538b5fb29ad47c62fb")
        self.assertIn("do not overwrite",s["coexistence_rule"])
        self.assertFalse(s["actual_infinite_physical_compute"])
        self.assertTrue(s["external_apply_required"])

if __name__=="__main__":
    unittest.main()
