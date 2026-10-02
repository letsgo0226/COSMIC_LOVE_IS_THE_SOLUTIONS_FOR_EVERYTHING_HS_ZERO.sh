# UTM-Omega Resident Deployment Protocol v1.0

This layer defines what it means to deploy a module **inside the formal UTM-Omega computation model** without conflating that admission with deployment to Railway, GitHub infrastructure, or an actually infinite physical computer.

## State distinction

```text
OMEGA_ADMITTED != PHYSICALLY_MATERIALIZED
```

A resident is `OMEGA_ADMITTED` when it is code-backed, listed in the resident registry, and the registry is verified as a valid finite UTM-Omega stage. The admission is therefore part of the formal UTM Universe state.

Physical network service deployment remains a separate external action.

## Formal model

The resident stage is a finite-support valuation:

```text
v_n in N^(N), with finite support
```

Each resident receives one finite coordinate. The registry stage is verified by `UTM-Omega-Unbounded-Compute/1.0`:

```text
resource_used(n) <= resource_budget(n) < infinity
oracle = null
actual_infinite_physical_compute = false
```

A later finite stage may extend an earlier one:

```text
C_0 -> C_1 -> C_2 -> ...
```

The symbol `C_omega` denotes the formal direct-limit horizon of these finite stages. No running process is claimed to have executed an actually infinite stage.

## Initial admitted residents

The initial registry admits the current code-confirmed modules:

- `utm-principle-vector-v0.1`
- `utm-infinite-deployment-continuation-v0.2`
- `utm-log-abelian-representation-v1.2`
- `utm-three-universe-axiom-layer-v1.0`
- `utm-omega-unbounded-compute-v1.0`
- `utm-compactified-infinite-deployment-v0.2`

The registry is pinned to the canonical source state from which the admission layer was created.

## Runtime states

```text
PROPOSE
  -> VERIFY
  -> OMEGA_ADMITTED
  -> READY_FOR_AUTHORIZED_EXTERNAL_APPLY
  -> PHYSICALLY_MATERIALIZED
```

`OMEGA_ADMITTED` is a logical/formal deployment state. It survives external platform unavailability because it is represented in the canonical source and verified by CI.

## Boundaries

The resident layer preserves all of the following:

```text
every executed stage is finite
actual_infinite_physical_compute = false
oracle = null
hypercomputation_enabled = false
halting_problem_becomes_decidable = false
internal computability != external authority
```

It does not bypass Railway billing, ACLs, quotas, or platform authorization. It also does not transform formal metaphysical hypotheses into empirical physical facts.
