import itertools

import pydot
import spot

from crome.logic.specification.rules_extractors import extract_mutex_rules, extract_adjacency_rules
from crome.logic.specification.temporal import LTL
from crome.logic.tools.logic import Logic
from crome.logic.typelement.robotic import BooleanAction, BooleanLocation, BooleanSensor, BooleanContext
from crome.logic.typeset import Typeset
from crome.synthesis.controller import ControllerSpec, Controller, Mealy
from crome.synthesis.world import World


class DynamicTransitionBuilder:

    def __init__(self, c1_safety_guarantees: LTL, c2_safety_guarantees: LTL, switch_condition: LTL, world_1: World,
                 world_2: World, c1_safety_assumptions=LTL("TRUE"), c2_safety_assumptions=LTL("TRUE")):
        self.rho_1 = self._get_safety_from(c1_safety_guarantees, world_1, c1_safety_assumptions)
        self.rho_2 = self._get_safety_from(c2_safety_guarantees, world_2, c2_safety_assumptions)
        self.switch_condition = switch_condition

        # self.world_1 = world_1
        # self.world_2 = world_2

        self.transition_world = World(
            project_name="gridworld",
            typeset=Typeset(
                {
                    BooleanAction(name="greet"),
                    BooleanAction(name="register"),
                    BooleanLocation(
                        name="r1", mutex_group="locations"
                    ),
                    BooleanLocation(
                        name="r2", mutex_group="locations"
                    ),
                    BooleanLocation(
                        name="r3", mutex_group="locations"
                    ),
                    BooleanLocation(
                        name="r4", mutex_group="locations"
                    ),
                    BooleanLocation(
                        name="r5", mutex_group="locations"
                    ),
                    BooleanSensor(name="person"),
                    BooleanContext(name="day", mutex_group="time"),
                    BooleanContext(name="night", mutex_group="time"),
                }
            ),
        )

        # TODO is this necessary? should we remove it afterwards?
        # self.world_1.typeset.update({"switch": BooleanAction(name="switch"), "allowed": BooleanAction(name="allowed")})
        # self.world_2.typeset.update({"switch": BooleanAction(name="switch"), "allowed": BooleanAction(name="allowed")})
        # self.transition_world = world_1
        self.transition_world.typeset.update({"switch": BooleanAction(name="switch"), "allowed": BooleanAction(name="allowed")})

        self.rho_s = self._get_dynamic_transition_rules()

    def build_transition_controller(self, current_pos: LTL, target_pos: LTL,
                                    controller_name: str = "transition_controller") -> Controller:
        """
        Generates a controller capable of going from current_pos to target_pos,
        satisfying the safety rules of both contracts in turn
        """
        # TODO rewrite because it's notation abuse, our guarantees already contains the assumptions
        assumptions = LTL("TRUE", _typeset=self.transition_world.typeset)
        guarantees = LTL(f"({current_pos}) & {self.rho_s} & (F ({target_pos}))", _typeset=self.transition_world.typeset)

        controller_spec = ControllerSpec.from_ltl(assumptions, guarantees, self.transition_world)

        controller = Controller(name=controller_name, spec=controller_spec, _typeset=self.transition_world.typeset)

        controller.save("dot", controller_name)  # TODO remove after development, only for debugging

        ####  building it manually
        from crome.synthesis.controller import generate_controller
        from crome.synthesis.tools.crome_io import save_to_file
        from crome.synthesis.tools import output_folder_synthesis

        a = str(assumptions)
        a = "G((! day & night) | (day & ! night))"
        # g = str(guarantees)
        g = f"(({current_pos}) & ! switch & ! allowed) & {self.rho_s} & (F ({target_pos}))"
        i, o = self.transition_world.typeset.extract_inputs_outputs(string=True)
        i = ','.join(i)
        o = ','.join(o)
        _, automaton, _ = generate_controller(a, g, i, o)
        spot_automaton = spot.automaton(automaton)
        save_to_file(
            file_content=spot_automaton.to_str("dot"), file_name="a_mano.dot",
            absolute_folder_path=output_folder_synthesis
        )
        gra = pydot.graph_from_dot_file("crome/output/a_mano.dot")[0]
        gra.write_png("a_mano.png")
        ####

        return controller

    def _get_dynamic_transition_rules(self):
        """
        Generate context-switching specific rules
        Section 4.1 Bridge-Controller Construction
        Dynamic Update for Synthesized GR(1) Controllers, Maoz, Amram paper.
        """
        t1 = Logic.or_([self.rho_1, self.rho_2])
        t2 = LTL(f"switch -> X({self.rho_2})", _typeset=self.transition_world.typeset)

        # TODO the typeset defining this bridge should be world 1, 2 or a mix of both?
        s1 = LTL("(~switch & X(switch)) -> X(allowed)", _typeset=self.transition_world.typeset)
        s2 = LTL("switch -> X(switch)", _typeset=self.transition_world.typeset)
        s3 = LTL(f"~{self.rho_1} -> X(switch)", _typeset=self.transition_world.typeset)
        p1 = LTL(f"X(allowed) -> (({self.switch_condition} & {self.rho_2}) | (allowed & {self.rho_2})) & "
                 f"(({self.switch_condition} & {self.rho_2})| (allowed & {self.rho_2})) -> X(allowed)", _typeset=self.transition_world.typeset)
        # TODO is there an iff?
        # ^ allowed′↔((cond ∧ ρs 2)∨(allowed ∧ ρs 2))

        ####  new try
        s1 = LTL("(~switch & X(switch)) -> allowed", _typeset=self.transition_world.typeset)
        # p1 = LTL(f"(({self.switch_condition}) & ({self.rho_2})) -> X(allowed)", _typeset=self.transition_world.typeset)
        ####

        rho_s = Logic.and_([str(f) for f in [t1, t2, s1, s2, s3, p1]])
        return rho_s

    @staticmethod
    def _get_safety_from(contract_guarantees: LTL, world: World,
                         contract_assumptions=LTL("TRUE")) -> str:
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

        return Logic.implies_(str(assumptions), str(guarantees))
