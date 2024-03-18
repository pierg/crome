from crome.cgg.goal import Goal
from crome.cgg.goal.operations.merging import g_merging
from crome.cgg.goal.operations.separation import g_separation
from crome.contracts.contract import Contract
from crome.logic.specification.temporal import LTL

top_spec = Goal(contract=Contract(_liveness_assumptions=LTL("a1"), _liveness_guarantees=LTL("g1")))

print(f"TOP_SPEC:\n{top_spec}")

lib_spec = Goal(contract=Contract(_liveness_assumptions=LTL("a2"), _liveness_guarantees=LTL("g2")))


print(f"LIB_SPEC:\n{lib_spec}")


sep = g_separation(lib_spec, top_spec)
print(f"M1:\n{sep}")


new = g_merging({top_spec, sep})
print(f"M2:\n{new}")

print(new.contract.liveness_assumptions.boolean.dnf)
print(new.contract.liveness_guarantees.boolean.cnf)
