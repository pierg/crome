from crome.cgg.case_studies.robocup.world.world_top import w_top
from crome.contracts.contract import Contract
from crome.cgg.goal import Goal
from crome.logic.patterns.basic import *
from crome.logic.patterns.robotic_movement import *
from crome.logic.patterns.robotic_triggers import *
from crome.logic.specification.temporal import LTL

goals_top = {
    Goal(
        id="init",
        contract=Contract(_liveness_guarantees=LTL(Init("lb"), _typeset=w_top.typeset)),
        world=w_top,
    ),
    Goal(
        id="order_patrol",
        contract=Contract(
            _liveness_guarantees=LTL(OrderedPatrolling(["lb", "lv"]), _typeset=w_top.typeset)
        ),
        world=w_top,
    ),
    Goal(
        id="cleanup",
        contract=Contract(
            _liveness_guarantees=LTL(InstantaneousReaction("oj", "hl"), _typeset=w_top.typeset)
        ),
        world=w_top,
    ),
    Goal(
        id="drop",
        description="drop only when you are in the garbage location and you're holding an object",
        contract=Contract(
            _liveness_guarantees=LTL(
                InstantaneousReaction(pre="lg & oj", post="dp"), _typeset=w_top.typeset
            )
        ),
        world=w_top,
    ),
    Goal(
        id="remove",
        description="remove all the objects continuously",
        contract=Contract(_liveness_guarantees=LTL(InfOft("!ob"), _typeset=w_top.typeset)),
        world=w_top,
    ),
}
