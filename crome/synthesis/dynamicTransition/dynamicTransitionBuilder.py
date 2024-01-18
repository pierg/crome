from crome.logic.specification.temporal import LTL
from crome.logic.tools.logic import Logic
from crome.logic.typelement.robotic import BooleanAction
from crome.synthesis.controller import ControllerSpec, Controller
from crome.synthesis.world import World


class DynamicTransitionBuilder:

    def __init__(self, rho_1: LTL, rho_2: LTL, switch_condition: LTL,
                 world_1: World, world_2: World):
        self.rho_1 = rho_1
        self.rho_2 = rho_2
        self.switch_condition = switch_condition
        self.world_1 = world_1
        self.world_2 = world_2

        # TODO is this necessary? should we remove it afterwards?
        self.world_1.typeset.update({"switch": BooleanAction(name="switch"), "allowed": BooleanAction(name="allowed")})
        self.world_2.typeset.update({"switch": BooleanAction(name="switch"), "allowed": BooleanAction(name="allowed")})

        self.rho_s = self._get_dynamic_transition_rules()

    def build_transition_controller(self, current_pos: LTL, target_pos: LTL,
                                    controller_name: str = "transition_controller") -> Controller:
        """
        Generates a controller capable of going from current_pos to target_pos,
        satisfying the safety rules of both contracts in turn
        """
        # TODO do we need stronger assumptions? and the typeset is always from world_1?
        assumptions = LTL("TRUE", _typeset=self.world_1.typeset)
        guarantees = LTL(f"{current_pos} & {self.rho_s} & (F ({target_pos}))", _typeset=self.world_1.typeset)

        controller_spec = ControllerSpec.from_ltl(assumptions, guarantees, self.world_1)

        controller = Controller(name=controller_name, spec=controller_spec, _typeset=self.world_1.typeset)

        controller.save("dot", controller_name) # TODO remove after development, only for debugging
        return controller

    def _get_dynamic_transition_rules(self):
        """
        Generate context-switching specific rules
        Section 4.1 Bridge-Controller Construction
        Dynamic Update for Synthesized GR(1) Controllers, Maoz, Amram paper.
        """
        t1 = Logic.or_([str(self.rho_1), str(self.rho_2)])
        t2 = LTL(f"switch -> X({self.rho_2})", _typeset=self.world_1.typeset)

        # TODO the typeset defining this bridge should be world 1, 2 or a mix of both?
        s1 = LTL("(~switch & X(switch)) -> X(allowed)", _typeset=self.world_1.typeset)
        s2 = LTL("switch -> X(switch)", _typeset=self.world_1.typeset)
        s3 = LTL(f"~{self.rho_1} -> X(switch)", _typeset=self.world_1.typeset)
        p1 = LTL(f"X(allowed) -> (({self.rho_2}) | (allowed & {self.rho_2})) & "
                 f"(({self.rho_2}) | (allowed & {self.rho_2})) -> X(allowed)", _typeset=self.world_1.typeset)
        # TODO is there an iff?
        # ^ allowed′↔((cond ∧ ρs 2)∨(allowed ∧ ρs 2))

        rho_s = Logic.and_([str(f) for f in [t1, t2, s1, s2, s3, p1]])
        return rho_s
