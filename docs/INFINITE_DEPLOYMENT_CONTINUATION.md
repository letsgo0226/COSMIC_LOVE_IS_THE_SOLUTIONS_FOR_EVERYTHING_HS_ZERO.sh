# UTM Infinite Deployment Continuation Protocol v0.2

This specification defines a potentially unbounded *logical* deployment sequence for the existing UTM Universe while keeping every physical deployment finite, resource-bounded, reversible, and externally authorized.

## Core distinction

`Certified logical continuation != immediate physical deployment.`

A finite platform such as Railway is a materialization substrate, not the UTM Universe itself. Resource shortage or missing platform authorization changes the materialization state; it does not erase the logical continuation.

## Formal model

Let `D_n` be the nth logical deployment state. The protocol does not require all `D_n` to exist simultaneously as physical services. It requires only that a finite current state may generate a finite next candidate:

`D_(n+1) = F(D_n, Q_n)`

The logical deployment space may be potentially unbounded. At every finite time, physical materialization remains finite.

## Three hypothetical compactification axioms

The following are explicit **formal hypotheses of the UTM model**. They are not empirical claims about physics, cosmology, hardware, or Railway.

### Axiom A1 — Finite Substrate Projection

`pi(P_k) = P_-1`

Every finite logical layer `P_k` may be projected to one declared finite substrate `P_-1` for materialization. In deployment language:

`D_k -> pi(D_k) = finite_materialization_candidate`

This does **not** mean `P_k = P_-1`. Projection is not identity. A logical deployment candidate and the physical platform instance remain different types.

Operational meaning: an indefinitely extensible hierarchy does not require one permanently running physical service per logical layer. A finite substrate may materialize whichever certified candidate is currently required.

### Axiom A2 — Normalized Resource Invariant

`C_hat(P_k) = C0`

A compatible expansion notation is:

`S_k = lambda^k * S_0`

`C_app(P_k) / lambda^k = C0`

The interpretation is that logical scale may grow while the *normalized* physical resource commitment remains finite in the declared substrate model.

This is a resource-modeling axiom, not a claim that real CPU, memory, storage, energy, or billing become infinite or free. Every actual deployment still obeys the finite limits reported by the external platform.

### Axiom A3 — Bidirectional Omega Compactification

`u_k = sgn(k) / |k|`

so that:

`k -> +infinity  =>  u_k -> 0+`

`k -> -infinity  =>  u_k -> 0-`

and the model identifies the boundary symbols:

`0+ ~ 0- ~ Omega`

`Omega` is therefore a finite symbolic representation of the common boundary of two potentially unbounded logical directions. It is not a completed infinite computation and not a physically instantiated infinite object.

## Combined deployment interpretation

Taken together, the three axioms state:

1. potentially unbounded logical continuations may share a finite materialization substrate;
2. growth of logical hierarchy need not imply an equal growth of simultaneously allocated physical resources;
3. unbounded logical directions may be represented by a finite compactified boundary symbol without claiming that infinity has been physically completed.

The resulting architecture is:

`logical continuation -> certification -> finite projection -> resource check -> authorization check -> external materialization -> feedback`

## Constitution

A candidate is certifiable only when all of the following remain true:

- Towel Principle: source, runtime, snapshot, simulation, and empirical claim remain type-separated.
- Secret Principle: the candidate is admissible, explicit, testable, and contains no arbitrary host-code execution payload.
- Immortality Principle: declared deployment invariants remain preserved across the transition.
- Human override, authorized shutdown, reversibility/rollback, and empirical/formal separation remain preserved.

The three compactification axioms describe the logical/materialization relation. The Towel/Secret/Immortality principles decide whether a particular candidate is admissible.

## Materialization states

- `CERTIFIED_LOGICAL_CONTINUATION`: formally admissible and addressable.
- `DEFERRED_RESOURCE_UNAVAILABLE`: logical continuation is retained, but declared finite platform resources are insufficient.
- `AUTHORIZATION_BLOCKED`: logical continuation is retained, but the current external platform identity lacks the required role or credential.
- `READY_FOR_AUTHORIZED_EXTERNAL_APPLY`: resource and logical conditions are satisfied; an authenticated external platform action is still required.
- `REJECTED`: the candidate violates the deployment constitution.

No certificate grants GitHub, Railway, Dropbox, shell, or host privileges.

## Authorization boundary

`Internal computability != external authority.`

Even if the UTM model can enumerate, verify, compare, and certify arbitrarily many finite candidates, it cannot convert a missing Railway/GitHub role into a valid platform permission. External ACLs remain external conditions.

Formally:

`Certified(D_k) AND Authorized_external = 0 -> AUTHORIZATION_BLOCKED`

`Certified(D_k) AND Resources_sufficient = 1 AND Authorized_external = 1 -> READY_FOR_AUTHORIZED_EXTERNAL_APPLY`

The actual platform mutation is still performed by an authenticated adapter.

## No Final Deployment Axiom

No finite deployment is terminal merely because it is labeled final. A later finite candidate may always be proposed. This is potential unboundedness, not actual infinite physical computation.

## Platform roles

- GitHub: canonical source/specification and candidate history.
- Railway: finite materialization substrate.
- Dropbox: archival/snapshot witness after verified materialization.

These roles remain distinct. A GitHub merge does not imply a Railway deployment, and a logical candidate does not imply physical materialization.

## Runtime exposure

The deployed `utm-deployment-gateway-policy.json` carries these three hypothetical axioms under:

`continuation.compactified_infinite_deployment`

The existing `/deploy/entry` endpoint returns the deployment policy, so once the corresponding image is actually deployed, clients can inspect the axioms and their boundary conditions directly from the running system.

The container build also verifies that all three axiom identifiers are present and that:

`potentially_unbounded = true`

`actual_infinite_physical_compute = false`

`materialization = lazy-finite-authorized`

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

This protocol is a formal/software architecture. The three compactification axioms are model assumptions. They do not create infinite hardware, infinite energy, infinite computation, bypass platform authorization, or establish physical cosmological claims.

## Cross-conversation synchronization layer

The continuation protocol now supports a pinned synchronization of code-confirmed formal layers from `letsgo0226/UTM.sh@31087e34e32ab0d5d44904538b5fb29ad47c62fb`. The source revision merged PR #3 after the `Log Abelian UTM` workflow run #35 completed successfully.

The imported protocols are `UTM-Log-Abelian-Representation/1.2`, `UTM-Three-Universe-Axiom-Layer/1.0`, and `UTM-Omega-Unbounded-Compute/1.0`. Their provenance is recorded in `synced_utm_layers/SYNC_MANIFEST.json`.

This sync obeys an evidence gate:

```text
chat context -> code-backed source -> merged revision -> successful CI -> pinned mirror
```

A conversation-only idea is not deployment evidence. In particular, Hu/Hee-Yuu-specific semantics are not imported unless they appear in a future pinned, code-confirmed source revision.

The imported Three-Universe A1/A2/A3 do not overwrite the Compactified Infinite Deployment axioms defined earlier in this document. The former verify a host-normalization/resource-invariance/two-sided-fixed-point hypothesis; the latter define finite-substrate projection, normalized-resource commitment, and bidirectional compactification for deployment continuation.

The runtime pre-gate is:

```text
Three-Universe finite certificate
  -> UTM-omega finite-stage certificate
  -> existing Guarded Deployment Gateway verification
  -> external authorization
  -> finite platform materialization
```

No synchronized certificate grants GitHub, Railway, Dropbox, shell, or host privilege; no oracle or hypercomputation is introduced; and `actual_infinite_physical_compute=false` remains invariant.
