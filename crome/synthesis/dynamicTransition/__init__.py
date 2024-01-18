import os
import subprocess
import time

from pathlib import Path

import pydot
import spot

from crome.logic.specification.string_logic import implies_
from crome.logic.specification.temporal import LTL
from crome.logic.tools.logic import Logic
from crome.synthesis.controller import Controller, Mealy
from crome.synthesis.controller.exceptions import UnknownStrixResponse

from crome.synthesis.dynamicTransition.examples import example


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

class DynamicTransition:

    def __init__(self, rho_1, rho_2, current_pos, target_pos, switch_condition, input_vars, output_vars):
        self.rho_1 = rho_1
        self.rho_2 = rho_2
        self.current_pos = current_pos
        self.target_pos = target_pos
        self.switch_condition = switch_condition
        self.input_vars = input_vars
        self.output_vars = output_vars

    # Generate bridge controller solving this game:
    # === true => current_pos & rho_s & F target_pos
    def generate_bridge_controller(self):
        # TODO: read output_variables from Contract parameter
        rho_s = self.dynamic_switch_rules()
        controller = generate_controller_strix("", f"{str(self.current_pos)} & {rho_s} & (F ({self.target_pos}))",
                                               ins="",
                                               outs=self.output_vars)

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
rho_1, rho_2, current_pos, target_pos, switch_condition, input_vars, output_vars = example.generateBasicExample()


bridgeGenerator = DynamicTransition(rho_1, rho_2, current_pos, target_pos, switch_condition, input_vars, output_vars)
controller = bridgeGenerator.generate_bridge_controller()
pass
