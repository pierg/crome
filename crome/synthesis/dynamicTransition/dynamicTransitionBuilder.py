import itertools

import pydot
import spot

from crome.logic.specification.rules_extractors import extract_mutex_rules, extract_adjacency_rules
from crome.logic.specification.temporal import LTL
from crome.logic.tools.logic import Logic
from crome.logic.typelement.robotic import BooleanAction, BooleanLocation, BooleanSensor, BooleanContext
from crome.logic.typeset import Typeset
from crome.synthesis.controller import Mealy, Controller
from crome.synthesis.controller import generate_controller
from crome.synthesis.tools import output_folder_synthesis
from crome.synthesis.tools.atomic_propositions import extract_in_out_atomic_propositions
from crome.synthesis.tools.crome_io import save_to_file
from crome.synthesis.world import World


class DynamicTransitionBuilder:

    def __init__(self, safety_guarantees_1: LTL, safety_guarantees_2: LTL, switch_condition: LTL, world_1: World,
                 world_2: World, safety_assumptions_1=LTL("TRUE"), safety_assumptions_2=LTL("TRUE")):

        self.assumptions_1, self.guarantees_1 = self._get_safety_from(safety_guarantees_1, world_1, safety_assumptions_1)
        self.assumptions_2, self.guarantees_2 = self._get_safety_from(safety_guarantees_2, world_2, safety_assumptions_2)

        self.rho_1 = Logic.implies_(str(self.assumptions_1), str(self.guarantees_1))
        self.rho_2 = Logic.implies_(str(self.assumptions_2), str(self.guarantees_2))

        self.switch_condition = switch_condition

        transition_typeset = world_1.typeset + world_2.typeset
        transition_typeset.update({"switch": BooleanAction(name="switch"), "allowed": BooleanAction(name="allowed")})
        inputs, outputs = transition_typeset.extract_inputs_outputs()
        self.input_aps, self.output_aps = extract_in_out_atomic_propositions(inputs, outputs)
        self.i, self.o = transition_typeset.extract_inputs_outputs(string=True)

        self.rho_s = self._get_dynamic_transition_rules()

    def build_transition_controller(self, current_pos: str, target_pos: str,
                                    controller_name: str = "transition_controller") -> Mealy:
        """
        Generates a controller capable of going from current_pos to target_pos,
        satisfying the safety rules of both contracts in turn and the switch condition in between.
        """

        a = "G((! day & night) | (day & ! night))"  # TODO take the assumptions from the contracts
        g = f"(({current_pos}) & ! switch & ! allowed) & {self.rho_s} & (F (switch & ({target_pos})))"
        realizable, automaton, synth_time = Controller.generate_from_spec(a, g, ','.join(self.i), ','.join(self.o))

        spot_automaton = spot.automaton(automaton)
        pydotgraph = pydot.graph_from_dot_data(spot_automaton.to_str("dot"))[0]
        mealy = Mealy.from_pydotgraph(
            pydotgraph, input_aps=self.input_aps, output_aps=self.output_aps
        )

        # TODO remove, only for debugging
        save_to_file(
            file_content=spot_automaton.to_str("dot"), file_name=f"{controller_name}.dot",
            absolute_folder_path=output_folder_synthesis
        )
        gra = pydot.graph_from_dot_file(f"crome/output/{controller_name}.dot")[0]
        gra.write_png(f"{output_folder_synthesis}/{controller_name}.png")
        ####

        return mealy

    def _get_dynamic_transition_rules(self):
        """
        Generate context-switching specific rules
        Section 4.1 Bridge-Controller Construction
        Dynamic Update for Synthesized GR(1) Controllers, Maoz, Amram paper.
        """
        t1 = Logic.or_([self.rho_1, self.rho_2])
        t2 = f"switch -> {self.rho_2}"

        s1 = "(!switch & X(switch)) -> X(allowed)"
        s2 = "switch -> X(switch)"
        s3 = f"!{self.rho_1} -> X(switch)"
        p1 = (f"X(allowed) -> (({self.switch_condition} & {self.rho_2}) | (allowed & {self.rho_2})) & "
              f"(({self.switch_condition} & {self.rho_2}) | (allowed & {self.rho_2})) -> X(allowed)")
        # TODO is there an iff?
        # ^ allowed′↔((cond ∧ ρs 2)∨(allowed ∧ ρs 2))

        ####  new try
        # s1 = LTL("(~switch & X(switch)) -> allowed", _typeset=self.transition_world.typeset)
        # p1 = LTL(f"(({self.switch_condition}) & ({self.rho_2})) -> X(allowed)", _typeset=self.transition_world.typeset)
        ####

        rho_s = Logic.and_([str(f) for f in [t1, t2, s1, s2, s3, p1]])
        return rho_s

    @staticmethod
    def _get_safety_from(contract_guarantees: LTL, world: World,
                         contract_assumptions=LTL("TRUE")):
        typeset_c, typeset_u = world.typeset.split_controllable_uncontrollable

        # assumptions
        a_mtx, _ = extract_mutex_rules(typeset_u, output_list=True)
        a_adj, t = extract_adjacency_rules(typeset_u, output_list=True)
        a_rules, _ = world.get_rules(environment=True)

        # guarantees
        g_mtx, _ = extract_mutex_rules(typeset_c, output_list=True)
        g_adj, _ = extract_adjacency_rules(typeset_c, output_list=True)
        g_rules, _ = world.get_rules(environment=False)

        # TODO make Logic be able to process LTL (and maybe return LTL)
        assumptions = Logic.and_(list(itertools.chain(
            [str(contract_assumptions)],
            a_adj,
            a_mtx,
            [r[0] for r in a_rules]
        )))

        guarantees = Logic.and_(list(itertools.chain(
            [str(contract_guarantees)],
            g_adj,
            g_mtx,
            [r[0] for r in g_rules]
        )))

        return assumptions, guarantees
