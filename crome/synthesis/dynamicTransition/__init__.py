import os
import subprocess
import time

from pathlib import Path

import pydot
import spot

from crome.contracts.contract import Contract
from crome.logic.patterns.robotic_movement import StrictOrderedPatrolling
from crome.logic.specification.string_logic import implies_
from crome.logic.specification.temporal import LTL
from crome.logic.tools.logic import Logic
from crome.synthesis.controller import Controller, Mealy
from crome.synthesis.controller.exceptions import UnknownStrixResponse


def generate_controller_strix(assumptions="", guarantees="", ins="", outs=""):
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
    mealy_controller = Mealy.from_pydotgraph(pydotgraph, input_aps=ins, output_aps=outs)
    return mealy_controller


def prepareLTL():
    controller_name = "arbiter"
    spec_path = Path(os.path.abspath(os.path.dirname(__file__)))
    controller_spec = spec_path / f"spec.txt"

    print(f"controller selected: {controller_spec}")

    # METHOD 1: MONOLITHIC SYNTHESIS FROM STRIX
    controller = Controller.from_file(file_path=controller_spec, name=controller_name)
    print(f"Monolithic synthesis realized in {controller.synth_time} s")


class DynamicTransition:

    def __init__(self, rho_1, rho_2, current_pos, target_pos, switch_condition):
        self.rho_1 = rho_1
        self.rho_2 = rho_2
        self.current_pos = current_pos
        self.target_pos = target_pos
        self.switch_condition = switch_condition

    # Generate bridge controller solving this game:
    # === true => current_pos & rho_s & F target_pos
    def generate_bridge_controller(self):
        # TODO: read output_variables from Contract parameter
        output_variables = "r1,r2,r3,r4,r5, allowed, switch"
        rho_s = self.dynamic_switch_rules()
        controller = generate_controller_strix("", f"{str(self.current_pos)} & {rho_s} & (F ({self.target_pos}))",
                                               ins="",
                                               outs=output_variables)

        return controller

    # Generate context-switching specific rules
    # Section 4.1 Bridge-Controller Construction
    # Dynamic Update for Synthesized GR(1) Controllers, Maoz, Amram paper.
    def dynamic_switch_rules(self):
        t1 = Logic.or_([str(self.rho_1), str(self.rho_2)])
        t2 = LTL(f"switch -> X({self.rho_2})")
        s1 = LTL("(~switch & X(switch)) -> X(allowed)")
        s2 = LTL("switch -> X(switch)")
        s3 = LTL(f"~{self.rho_1} -> X(switch)")
        p1 = LTL(f"X(allowed) -> (({self.rho_2} & {self.switch_condition}) | (allowed & {self.rho_2})) & "
                 f"(({self.rho_2} & {self.switch_condition}) | (allowed & {self.rho_2})) -> X(allowed)")  # TODO hay un iff?
        return Logic.and_([str(f) for f in [t1, t2, s1, s2, s3, p1]])



## Reglas puntuales de este ejemplo
## TODO: pasarlas a otro archivo o usar directamente de los contratos
exclude_rules = []
for i in range(1,6):
    exclude_rule = f"r{i}"
    for j in range(1,6):
        if i!=j:
            exclude_rule += f" & !r{j}"
    exclude_rules.append("(" + exclude_rule + ")")
safety_exclude = ("G " + Logic.or_([safety_exclude_rule for safety_exclude_rule in exclude_rules]))


# TODO ^ esto sería el mundo de la grilla no? cómo podemos sacar la fórmula desde el gridworld?
rho_1 = LTL("(!r2 U r1) & G(r2 -> X(!r2 U r1)) & G(r1 -> X(!r1 U r2)) & " + str(safety_exclude))  # day_safety_system
rho_2 = LTL("(!r4 U r3) & G(r4 -> X(!r4 U r3)) & G(r3 -> X(!r3 U r4)) & " + str(safety_exclude))  # night_safety_system
current_pos=LTL("r1 & !r2 & !r3 & !r4 & !r5")
target_pos=LTL("!r1 & !r2 & r3 & !r4 & !r5")
switch_condition = True

bridgeGenerator = DynamicTransition(rho_1, rho_2, current_pos, target_pos, switch_condition)
controller = bridgeGenerator.generate_bridge_controller()
pass
