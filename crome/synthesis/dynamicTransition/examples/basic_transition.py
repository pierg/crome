from crome.logic.patterns.robotic_movement import StrictOrderedPatrolling
from crome.logic.specification.temporal import LTL
from crome.logic.typelement.robotic import BooleanAction, BooleanLocation, BooleanSensor, BooleanContext
from crome.logic.typeset import Typeset
from crome.synthesis.dynamicTransition.dynamicTransitionBuilder import DynamicTransitionBuilder
from crome.synthesis.world import World


if __name__ == '__main__':
    # WORLD MODELING
    gridworld = World(
        project_name="gridworld",
        typeset=Typeset(
            {
                BooleanAction(name="greet"),
                BooleanAction(name="register"),
                BooleanLocation(
                    name="r1", mutex_group="locations", adjacency_set={"r2", "r5"}
                ),
                BooleanLocation(
                    name="r2", mutex_group="locations", adjacency_set={"r1", "r5"}
                ),
                BooleanLocation(
                    name="r3", mutex_group="locations", adjacency_set={"r4", "r5"}
                ),
                BooleanLocation(
                    name="r4", mutex_group="locations", adjacency_set={"r3", "r5"}
                ),
                BooleanLocation(
                    name="r5",
                    mutex_group="locations",
                    adjacency_set={"r1", "r2", "r3", "r4"},
                ),
                BooleanSensor(name="person"),
                BooleanContext(name="day", mutex_group="time"),
                BooleanContext(name="night", mutex_group="time"),
            }
        ),
    )

    # CONTEXT/CONTRACTS only LTL part TODO create complete contracts for the example
    day_patrol_12 = LTL(
        StrictOrderedPatrolling(locations=["r1", "r2"]).__str__(),
        _typeset=gridworld.typeset,
    )

    night_patrol_34 = LTL(
        StrictOrderedPatrolling(locations=["r3", "r4"]).__str__(),
        _typeset=gridworld.typeset,
    )

    # TRANSITION CONTROLLER BUILDING
    # suppose
    current_pos = LTL("r1 & !r2 & !r3 & !r4 & !r5", _typeset=gridworld.typeset)
    target_pos = LTL("!r1 & !r2 & r3 & !r4 & !r5", _typeset=gridworld.typeset)

    dtb_ctx1_to_ctx2 = DynamicTransitionBuilder(day_patrol_12, night_patrol_34,
                                                switch_condition=LTL("TRUE"), world_1=gridworld, world_2=gridworld)

    transition_controller = dtb_ctx1_to_ctx2.build_transition_controller(current_pos, target_pos)