import subprocess
import time

import pydot
import spot

from crome.logic.patterns.robotic_movement import StrictOrderedPatrolling
from crome.logic.specification.string_logic import implies_
from crome.logic.specification.temporal import LTL
from crome.logic.tools.logic import Logic
from crome.logic.typelement.robotic import BooleanAction, BooleanLocation, BooleanSensor, BooleanContext
from crome.logic.typeset import Typeset
from crome.synthesis.controller import Mealy, ControllerSpec, Controller
from crome.synthesis.controller.exceptions import UnknownStrixResponse
from crome.synthesis.world import World


def strix_example(assumptions="", guarantees="! GF! request_m | G(request_0 -> Fgrant_0)", ins="request_0, request_m",
                  outs="grant_0"):
    strix_specs = f"-f '{implies_(assumptions, guarantees)}' --ins='{ins}' --outs='{outs}'"

    strix_bin = "strix"
    command = f"{strix_bin} {strix_specs}"

    timeout = 3600
    print(f"RUNNING COMMAND:\n{command}")
    start_time = time.time()

    result = subprocess.check_output(
        [command], shell=True, timeout=timeout, encoding="UTF-8"
    ).splitlines()

    exec_time = time.time() - start_time

    if "REALIZABLE" in result:
        realizable = True
    elif "UNREALIZABLE" in result:
        realizable = False
    else:
        raise UnknownStrixResponse(command=command, response="\n".join(result))

    processed_return = ""

    for i, line in enumerate(result):
        if "HOA" not in line:
            continue
        else:
            processed_return = "\n".join(result[i:])
            break

    print("RESULT:")
    print(f"exec_time: {exec_time}")
    print(f"realizable: {realizable}")
    print(f"processed_return: \n{processed_return}")

    automaton = spot.automaton(processed_return)
    pydotgraph = pydot.graph_from_dot_data(automaton.to_str("dot"))[0]
    pydotgraph.write_png("example.png")
    return automaton


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

    day_patrol_12 = LTL(
        StrictOrderedPatrolling(locations=["r1", "r2"]).__str__(),
        _typeset=gridworld.typeset,
    )

    night_patrol_34 = LTL(
        StrictOrderedPatrolling(locations=["r3", "r4"]).__str__(),
        _typeset=gridworld.typeset,
    )

    # BRIDGE BUILDING
    gridworld.typeset.update({"switch": BooleanAction(name="switch"), "allowed": BooleanAction(name="allowed")})

    rho_s_1 = day_patrol_12
    rho_s_2 = night_patrol_34

    # building the bridge
    t1 = Logic.or_([str(rho_s_1), str(rho_s_2)])
    t2 = LTL(f"switch -> X({rho_s_2})", _typeset=gridworld.typeset)

    s1 = LTL("(~switch & X(switch)) -> X(allowed)", _typeset=gridworld.typeset)
    s2 = LTL("switch -> X(switch)", _typeset=gridworld.typeset)
    s3 = LTL(f"~{rho_s_1} -> X(switch)", _typeset=gridworld.typeset)
    p1 = LTL(f"X(allowed) -> (({rho_s_2}) | (allowed & {rho_s_2})) & "
             f"(({rho_s_2}) | (allowed & {rho_s_2})) -> X(allowed)", _typeset=gridworld.typeset)  # TODO hay un iff?
    # ^ allowed′↔((cond ∧ ρs 2)∨(allowed ∧ ρs 2))

    rho_s = Logic.and_([str(f) for f in [t1, t2, s1, s2, s3, p1]])

    current_pos = LTL("r1 & !r2 & !r3 & !r4 & !r5", _typeset=gridworld.typeset)
    target_pos = LTL("!r1 & !r2 & r3 & !r4 & !r5", _typeset=gridworld.typeset)

    assumptions = LTL("TRUE", _typeset=gridworld.typeset)
    guarantees = LTL(f"{str(current_pos)} & {rho_s} & (F ({target_pos}))", _typeset=gridworld.typeset)

    controller_spec_example = ControllerSpec.from_ltl(
        assumptions, guarantees, gridworld
    )

    controller_example = Controller(
        name=f"example_controller", spec=controller_spec_example, _typeset=gridworld.typeset
    )

    controller_example.save("dot", "example_controller.dot")
