#!/usr/bin/env python3

import math
import unittest

from utm_principle_vector import (
    ComplexNode,
    PrincipleVectorState,
    TAU,
    chronon_step,
    secret_check,
    validate_transition,
)


class PrincipleVectorTests(unittest.TestCase):
    def base(self):
        return PrincipleVectorState(
            tick=0,
            tau=0,
            towel=ComplexNode(1.0, math.pi / 4),
            secret=ComplexNode(2.0, -math.pi / 4),
        )

    def test_log_composition_identity(self):
        s = self.base()
        lhs = s.existential_image
        rhs = __import__("cmath").exp(s.towel.as_complex()) * __import__("cmath").exp(s.secret.as_complex())
        self.assertAlmostEqual(lhs.real, rhs.real, places=12)
        self.assertAlmostEqual(lhs.imag, rhs.imag, places=12)

    def test_phase_coherence(self):
        s = self.base()
        self.assertTrue(s.peace)
        self.assertAlmostEqual(s.phase_class, 0.0, places=12)

    def test_equivalence_under_two_pi_shift(self):
        s0 = self.base()
        s1 = chronon_step(
            s0,
            +1,
            towel=ComplexNode(1.0, math.pi / 4 + TAU),
        )
        self.assertNotEqual(s0.z, s1.z)
        self.assertEqual(s0.equivalence_class, s1.equivalence_class)
        self.assertTrue(validate_transition(s0, s1))

    def test_bidirectional_chronon(self):
        s0 = self.base()
        forward = chronon_step(s0, +1)
        backward = chronon_step(s0, -1)
        self.assertEqual(forward.tau, 1)
        self.assertEqual(backward.tau, -1)
        self.assertEqual(forward.tick, 1)
        self.assertEqual(backward.tick, 1)

    def test_invalid_chronon_rejected(self):
        with self.assertRaises(ValueError):
            chronon_step(self.base(), 0)

    def test_empirical_claim_is_rejected_by_towel_gate(self):
        s = PrincipleVectorState(
            tick=0,
            tau=0,
            towel=ComplexNode(1.0, 0.0),
            secret=ComplexNode(1.0, 0.0),
            empirical_claim=True,
        )
        self.assertFalse(secret_check(s))

    def test_invariant_break_is_detected(self):
        s0 = self.base()
        s1 = chronon_step(
            s0,
            +1,
            towel=ComplexNode(1.5, math.pi / 4),
        )
        self.assertFalse(validate_transition(s0, s1))


if __name__ == "__main__":
    unittest.main()
