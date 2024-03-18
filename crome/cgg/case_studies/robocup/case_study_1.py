from crome.cgg.case_studies.robocup.world.world_ref import w_ref
from crome.cgg.case_studies.robocup.world.world_top import w_top
from crome.contracts.contract import Contract
from crome.cgg.goal import Goal
from crome.logic.patterns.robotic_movement import *
from crome.logic.specification.temporal import LTL

g_top = Goal(
    id="order_patrol",
    contract=Contract(
        _liveness_guarantees=LTL(StrictOrderedPatrolling(["lb", "lv"]), _typeset=w_top.typeset)
    ),
    world=w_top,
)

g_ref = Goal(
    id="order_patrol_ref",
    contract=Contract(
        _liveness_guarantees=LTL(StrictOrderedPatrolling(["b2", "l2"]), _typeset=w_ref.typeset)
    ),
    world=w_ref,
)

assert g_ref.contract <= g_top.contract
