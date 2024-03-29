from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from crome.synthesis.controller import Controller, ControllerSpec
from crome.synthesis.world import World

from crome.cgg.context import Context
from crome.contracts.contract import Contract
from crome.cgg.tools.names import generate_goal_id
from crome.cgg.tools.strings import tab
from crome.logic.specification.temporal import LTL


@dataclass
class Goal:
    contract: Contract
    id: str = ""
    description: str = ""
    context: Context = Context(_init_formula="TRUE")
    world: World = field(default_factory=lambda: World())
    viewpoint: str = ""

    _parents: dict = field(init=False, repr=False, default_factory=dict)
    _children: dict = field(init=False, repr=False, default_factory=dict)

    _controller: Controller | None = field(init=False, repr=False, default=None)

    def __hash__(self):
        return hash(
            self.id
            + self.description
            + self.context.__str__()
            + self.world.__str__()
            + self.contract.__str__()
        )

    def __post_init__(self):
        if self.id == "":
            self.id = generate_goal_id(repr(self.contract))

        if len(self.world) == 0:
            self.world = World(typeset=self.contract.typeset)
        else:
            self.world.typeset += self.contract.typeset

        if self.viewpoint == "":
            self.viewpoint: str = self.contract.typeset.extract_viewpoint()

    def __le__(self: Goal, other: Goal):
        from crome.cgg.goal.operations.refinement import g_refinement

        return g_refinement(self, other)

    @property
    def controller(self) -> Controller | None:
        return self._controller

    def realize(self):
        cspec = ControllerSpec.from_ltl(
            self.contract.assumptions, self.contract.guarantees, self.world
        )
        self._controller = Controller(
            name=f"ctrl_{self.id}", spec=cspec, _typeset=self.contract.typeset
        )

    def export_to_json(self) -> dict[str, Any]:
        json_content = {"contract": {}}
        world_values = []
        for typeset in self.context.typeset:
            world_values.append(typeset)
        json_content["context"] = {
            "formula": self.context.formula,
            "world_values": world_values,
        }

        # We put the contracts with their LTL value only.
        contract = self.contract
        json_assumptions = contract.assumptions.export_to_json()
        json_guarantees = contract.guarantees.export_to_json()

        json_content["contract"]["assumptions"] = [json_assumptions]
        json_content["contract"]["guarantees"] = [json_guarantees]

        # Get the information of the new goal :
        json_content["id"] = self.id
        json_content["description"] = self.description

        return json_content

    def compare_with(self: Goal, other: Goal):
        typeset = self.world.typeset + other.world.typeset

        from crome.logic.specification.rules_extractors import extract_refinement_rules

        rules = extract_refinement_rules(typeset)
        print(self.contract)
        print(other.contract)
        print(rules)
        print(rules)

    def __str__(self):
        res = []

        res.append(tab(f"GOAL {self.id}", how_many=0, init_character="|---"))
        if not self.context.is_true_expression:
            res.append(tab("CONTEXT", how_many=1, init_character="|"))
            res.append(tab(str(self.context), how_many=2, init_character="|"))

        res.append(tab(str(self.contract), how_many=1, init_character="|"))

        return "\n".join(res)


if __name__ == "__main__":
    g = Goal(contract=Contract(LTL("Ga")))
    print(g)
