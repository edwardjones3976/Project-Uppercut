# Live-runtime strategic-success rule

> **No phase after Q is strategically successful unless its implementation is reusable by the shared live simulation without copying its rules.**

A phase may be analytically proven by a dedicated contract or commandlet. That proof remains valuable. After Phase Q, however, strategic completion additionally requires that the same authoritative implementation can be consumed by the live Unreal runtime.

## Allowed

- phase-specific contracts and null-hypothesis harnesses;
- commandlets as clients of shared runtime code;
- frozen unit pins beside a newer integrated contract;
- presentation adapters that cannot write back to authority.

## Not allowed

- copying proven rules into a separate Play-in-Editor implementation;
- declaring a product milestone complete because an isolated commandlet passes;
- rewriting historical phase pins to disguise integration as continuity;
- using test count as a substitute for a visible, complete experience.

Decision 0022 defines the integrated-contract and RNG-partitioning policy that makes this rule executable.
