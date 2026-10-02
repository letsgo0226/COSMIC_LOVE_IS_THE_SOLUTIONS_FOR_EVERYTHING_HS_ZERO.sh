"""Log-Abelian UTM representation synchronized from letsgo0226/UTM.sh.

Representation-only semantics:
x+y = log(a)+log(b) = log(ab).
This does not make ordinary UTM transition composition commutative.
"""
import math

MAX_EVENTS = 64
MAX_COORD = 200
MAX_GODEL_DIGITS = 20000

def cantor(a: int, b: int) -> int:
    s = a + b
    return s * (s + 1) // 2 + b

def unpair(z: int):
    w = (math.isqrt(8*z + 1) - 1) // 2
    t = w * (w + 1) // 2
    b = z - t
    a = w - b
    return a, b

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d*d <= n:
        if n % d == 0:
            return False
        d += 2
    return True

_PRIMES = [2]

def nth_prime(n: int) -> int:
    if n < 0:
        raise ValueError("prime index must be nonnegative")
    c = _PRIMES[-1] + 1
    if c % 2 == 0:
        c += 1
    while len(_PRIMES) <= n:
        if is_prime(c):
            _PRIMES.append(c)
        c += 2
    return _PRIMES[n]

def prime_index(p: int) -> int:
    if not is_prime(p):
        raise ValueError("factor is not prime")
    i = 0
    while True:
        q = nth_prime(i)
        if q == p:
            return i
        if q > p:
            raise ValueError("prime not in canonical enumeration")
        i += 1

def normalize_event(e):
    step = int(e["step"])
    op = int(e["op"])
    if step < 0 or op < 0 or step > MAX_COORD or op > MAX_COORD:
        raise ValueError(f"step/op must be integers in 0..{MAX_COORD}")
    return {"step": step, "op": op}

def event_prime(e):
    e = normalize_event(e)
    return nth_prime(cantor(e["step"], e["op"]))

def encode_events(events):
    if not isinstance(events, list) or len(events) > MAX_EVENTS:
        raise ValueError(f"events must be a list with at most {MAX_EVENTS} entries")
    norm = [normalize_event(e) for e in events]
    ps = [event_prime(e) for e in norm]
    g = math.prod(ps) if ps else 1
    x = math.fsum(math.log(p) for p in ps)
    return {
        "events": norm,
        "godel_product": str(g),
        "log_coordinate": x,
        "canonical_events": sorted(norm, key=lambda e:(e["step"], e["op"])),
    }

def decode_godel(godel):
    s = str(godel)
    if len(s) > MAX_GODEL_DIGITS:
        raise ValueError("godel integer too large")
    n = int(s)
    if n < 1:
        raise ValueError("godel must be a positive integer")
    factors = []
    pidx = 0
    while n > 1:
        p = nth_prime(pidx)
        while n % p == 0:
            factors.append(p)
            n //= p
            if len(factors) > MAX_EVENTS:
                raise ValueError("too many encoded events")
        pidx += 1
        if p*p > n and n > 1:
            if not is_prime(n):
                raise ValueError("factorization exceeded canonical bound")
            factors.append(n)
            n = 1
    events = []
    for p in factors:
        idx = prime_index(p)
        step, op = unpair(idx)
        if step > MAX_COORD or op > MAX_COORD:
            raise ValueError("decoded coordinate exceeds bound")
        events.append({"step": step, "op": op})
    return sorted(events, key=lambda e:(e["step"], e["op"]))

def compose(left, right):
    L, R = encode_events(left), encode_events(right)
    both = encode_events(left + right)
    rev = encode_events(right + left)
    gl, gr = int(L["godel_product"]), int(R["godel_product"])
    return {
        "left": L,
        "right": R,
        "composition": both,
        "law": "log(a)+log(b)=log(ab)",
        "proof": {
            "product_identity": int(both["godel_product"]) == gl * gr,
            "commutative_product": gl * gr == gr * gl,
            "commutative_log": math.isclose(
                both["log_coordinate"], rev["log_coordinate"],
                rel_tol=1e-12, abs_tol=1e-12
            ),
            "causal_order_recoverable": decode_godel(both["godel_product"]) == both["canonical_events"],
        },
    }

def spec():
    return {
        "protocol": "UTM-Log-Abelian-Representation/1.2",
        "kernel": "x+y=log(a)+log(b)=log(ab)",
        "representation": "finite events (step,op) -> Cantor index -> nth prime",
        "composition": "integer multiplication / log-space addition",
        "semantics": "representation is Abelian; decoded UTM causality remains ordered",
        "limits": {"max_events": MAX_EVENTS, "max_coordinate": MAX_COORD},
        "actual_infinite_physical_compute": False,
    }
