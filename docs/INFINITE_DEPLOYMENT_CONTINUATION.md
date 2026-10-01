# UTM Infinite Deployment Continuation Protocol v0.1

This specification defines a potentially unbounded *logical* deployment sequence for the existing UTM Universe while keeping every physical deployment finite, resource-bounded, reversible, and externally authorized.

## Core distinction

`Certified logical continuation != immediate physical deployment.`

If a finite platform such as Railway has insufficient resources, the candidate state is `DEFERRED_RESOURCE_UNAVAILABLE`, not `HALTED`.

## Formal model

Let `D_n` be the nth logical deployment state. The protocol does not require all `D_n` to exist simultaneously as physical services. It requires only that a finite current state may generate a finite next candidate:

`D_(n+1) = F(D_n, Q_n)`

The logical deployment space may be potentially unbounded. At every finite time, physical materialization remains finite.

## Constitution

A candidate is certifiable only when all of the following remain true:

- Towel Principle: source, runtime, snapshot, simulation, and empirical claim remain type-separated.
- Secret Principle: the candidate is admissible, explicit, testable, and contains no arbitrary host-code execution payload.
- Immortality Principle: declared deployment invariants remain preserved across the transition.
- Human override, authorized shutdown, reversibility/rollback, and empirical/formal separation remain preserved.

## Materialization states

- `CERTIFIED_LOGICAL_CONTINUATION`: formally admissible and addressable.
- `DEFERRED_RESOURCE_UNAVAILABLE`: logically retained, but no physical resources are currently available.
- `READY_FOR_AUTHORIZED_EXTERNAL_APPLY`: resources are sufficient, but platform authorization is still required.
- `REJECTED`: the candidate violates the deployment constitution.

No certificate grants GitHub, Railway, Dropbox, shell, or host privileges.

## No Final Deployment Axiom

No finite deployment is terminal merely because it is labeled final. A later candidate may always be proposed. This is potential unboundedness, not actual infinite physical computation.

## Platform roles

- GitHub: canonical source/specification and candidate history.
- Railway: finite materialization substrate.
- Dropbox: archival/snapshot witness after verified materialization.

These are distinct roles. A GitHub merge does not imply a Railway deployment, and a logical candidate does not imply physical materialization.

## IFR

The deployment IFR is:

`potentially unbounded valid continuations / minimum necessary physical materialization`

The goal is not infinitely many simultaneous servers. The goal is an indefinitely extensible logical deployment space whose finite physical realizations are created only when required and authorized.

## Relationship to Principle-Vector v0.1

The deployment constitution uses the same three formal roles as `utm_principle_vector.py`:

- Towel -> proper attribution / type separation.
- Secret -> admissibility / validation.
- Immortality -> preservation of declared invariants under admissible transformation.

The deployment layer does not reinterpret these as measured physical chakra or cosmological quantities.

## Boundary

This protocol is a formal/software architecture. It does not create infinite hardware, infinite energy, infinite computation, or physical cosmological effects.