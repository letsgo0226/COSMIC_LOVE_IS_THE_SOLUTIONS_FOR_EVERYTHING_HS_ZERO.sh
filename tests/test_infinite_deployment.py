#!/usr/bin/env python3
import unittest

from utm_infinite_deployment import (
    DeploymentCandidate,
    REQUIRED_CERTIFICATE,
    certify,
    decide_materialization,
    next_candidate,
    protocol_manifest,
)


class InfiniteDeploymentProtocolTests(unittest.TestCase):
    def make_candidate(self, **overrides):
        data = dict(
            generation=1,
            request_id="test-1",
            target="utm-principle-vector-layer",
            action="configure",
            parent_digest="0" * 64,
            settings={"mode": "observe-only", "healthcheck": "/health"},
            condition_certificate=dict(REQUIRED_CERTIFICATE),
            resource_request={"deployment_slots": 1},
        )
        data.update(overrides)
        return DeploymentCandidate(**data)

    def test_valid_candidate_certifies(self):
        c = self.make_candidate()
        cert = certify(c)
        self.assertTrue(cert.verified)
        self.assertEqual(cert.status, "CERTIFIED_LOGICAL_CONTINUATION")
        self.assertTrue(cert.external_apply_required)
        self.assertFalse(cert.actual_infinite_physical_compute)
        self.assertTrue(cert.gdeploy.isdigit())

    def test_resource_exhaustion_defers_not_halts(self):
        c = self.make_candidate()
        cert = certify(c)
        d = decide_materialization(cert, c.resource_request, {"deployment_slots": 0})
        self.assertEqual(d.status, "DEFERRED_RESOURCE_UNAVAILABLE")
        self.assertTrue(d.logical_continuation_preserved)
        self.assertFalse(d.physical_materialization)

    def test_sufficient_resources_still_require_external_apply(self):
        c = self.make_candidate()
        cert = certify(c)
        d = decide_materialization(cert, c.resource_request, {"deployment_slots": 1})
        self.assertEqual(d.status, "READY_FOR_AUTHORIZED_EXTERNAL_APPLY")
        self.assertTrue(d.external_apply_required)
        self.assertFalse(d.physical_materialization)

    def test_forbidden_host_code_is_rejected(self):
        c = self.make_candidate(settings={"command": "echo unsafe"})
        cert = certify(c)
        self.assertFalse(cert.verified)
        self.assertIn("forbidden_key:settings.command", cert.reasons)

    def test_failed_principle_certificate_is_rejected(self):
        pc = dict(REQUIRED_CERTIFICATE)
        pc["immortality_invariants_preserved"] = False
        c = self.make_candidate(condition_certificate=pc)
        cert = certify(c)
        self.assertFalse(cert.verified)
        self.assertIn("condition_failed:immortality_invariants_preserved", cert.reasons)

    def test_empirical_claim_is_rejected(self):
        c = self.make_candidate(empirical_claim=True)
        cert = certify(c)
        self.assertFalse(cert.verified)
        self.assertIn("empirical_claim_not_allowed", cert.reasons)

    def test_next_candidate_increments_generation(self):
        c = next_candidate(
            current_digest="a" * 64,
            generation=41,
            request_id="next",
            target="future-setting",
            action="configure",
            settings={"mode": "observe-only"},
            resource_request={"deployment_slots": 1},
        )
        self.assertEqual(c.generation, 42)
        self.assertEqual(c.parent_digest, "a" * 64)
        self.assertTrue(certify(c).verified)

    def test_manifest_preserves_finite_physical_boundary(self):
        m = protocol_manifest()
        self.assertEqual(m["logical_space"], "potentially-unbounded")
        self.assertEqual(m["physical_materialization"], "finite-resource-bounded")
        self.assertFalse(m["actual_infinite_physical_compute"])


if __name__ == "__main__":
    unittest.main()
