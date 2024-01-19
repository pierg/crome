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
        self.transition_world = world_1
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
        guarantees = LTL(f"{current_pos} & {self.rho_s} & (F ({target_pos}))", _typeset=self.transition_world.typeset)

        # controller_spec = ControllerSpec.from_ltl(assumptions, guarantees, self.transition_world)
        i, o = self.transition_world.typeset.extract_inputs_outputs()
        inputs = ', '.join([x.name for x in i])
        outputs = ', '.join([x.name for x in o])

        _, controller, _ = Controller.generate_from_spec(str(assumptions), str(guarantees), inputs, outputs)

        spot_automaton = spot.automaton(controller)

        pydotgraph = pydot.graph_from_dot_data(spot_automaton.to_str("dot"))[0]
        mealy = Mealy.from_pydotgraph(
            pydotgraph, input_aps=i, output_aps=o
        )

        # TODO remove after development, only for debugging
        pydotgraph.write(controller_name + ".dot")

        return mealy

    def _get_dynamic_transition_rules(self):
        """
        Generate context-switching specific rules
        Section 4.1 Bridge-Controller Construction
        Dynamic Update for Synthesized GR(1) Controllers, Maoz, Amram paper.
        """
        t1 = Logic.or_([str(self.rho_1), str(self.rho_2)])
        t2 = LTL(f"switch -> X({self.rho_2})", _typeset=self.transition_world.typeset)

        # TODO the typeset defining this bridge should be world 1, 2 or a mix of both?
        s1 = LTL("(~switch & X(switch)) -> X(allowed)", _typeset=self.transition_world.typeset)
        s2 = LTL("switch -> X(switch)", _typeset=self.transition_world.typeset)
        s3 = LTL(f"~{self.rho_1} -> X(switch)", _typeset=self.transition_world.typeset)
        p1 = LTL(f"X(allowed) -> (({self.rho_2}) | (allowed & {self.rho_2})) & "
                 f"(({self.rho_2}) | (allowed & {self.rho_2})) -> X(allowed)", _typeset=self.transition_world.typeset)
        # TODO is there an iff?
        # ^ allowed′↔((cond ∧ ρs 2)∨(allowed ∧ ρs 2))

        rho_s = Logic.and_([str(f) for f in [t1, t2, s1, s2, s3, p1]])
        return rho_s

    @staticmethod
    def _get_safety_from(contract_guarantees: LTL, world: World,
                         contract_assumptions=LTL("TRUE")) -> LTL:
        typeset_c, typeset_u = world.typeset.split_controllable_uncontrollable
        a_mtx = extract_mutex_rules(typeset_u)
        a_adj = extract_adjacency_rules(typeset_u,)
        a_rules, _ = world.get_rules(environment=True)
        g_mtx = extract_mutex_rules(typeset_c)
        g_adj = extract_adjacency_rules(typeset_c)
        g_rules, _ = world.get_rules(environment=False)

        if len(a_rules) == 0:
            a_rules = LTL("TRUE", _typeset=world.typeset)
        else:
            a_rules = Logic.and_([str(x) for x in a_rules])

        if len(g_rules) == 0:
            g_rules = LTL("TRUE", _typeset=world.typeset)
        else:
            g_rules = Logic.and_([str(x) for x in g_rules])

        # TODO make Logic be able to process LTL (and maybe return LTL)
        assumptions = LTL(Logic.and_([str(x) for x in [a_mtx, a_adj, a_rules, contract_assumptions]]),
                          _typeset=world.typeset)
        guarantees = LTL(Logic.and_([str(x) for x in [g_mtx, g_adj, g_rules, contract_guarantees]]),
                         _typeset=world.typeset)

        return LTL(Logic.implies_(str(assumptions), str(guarantees)))
