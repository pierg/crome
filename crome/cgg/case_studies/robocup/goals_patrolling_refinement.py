import os
from pathlib import Path

from crome.cgg.case_studies.robocup.world.world_top import w_top
from crome.contracts.contract import Contract
from crome.cgg.goal import Goal
from crome.cgg.goal.operations.composition import g_composition
from crome.cgg.tools.crome_io import save_to_file
from crome.logic.patterns.basic import *
from crome.logic.patterns.robotic_movement import *
from crome.logic.patterns.robotic_triggers import *
from crome.logic.specification.temporal import LTL

goals_top = {
    Goal(
        id="init",
        contract=Contract(_guarantees=LTL(Init("lb"), _typeset=w_top.typeset)),
        world=w_top,
    ),
    Goal(
        id="order_patrol",
        contract=Contract(
            _guarantees=LTL(OrderedPatrolling(["lb", "lv"]), _typeset=w_top.typeset)
        ),
        world=w_top,
    ),
    Goal(
        id="cleanup",
        contract=Contract(
            _guarantees=LTL(InstantaneousReaction("oj", "hl"), _typeset=w_top.typeset)
        ),
        world=w_top,
    ),
    Goal(
        id="drop",
        description="Only drop when near the trash",
        contract=Contract(
            _guarantees=LTL(
                InstantaneousReaction(pre="dp", post="lg"), _typeset=w_top.typeset
            )
        ),
        world=w_top,
    ),
    Goal(
        id="pickup",
        description="if object seen hold it",
        contract=Contract(
            _guarantees=LTL(
                InstantaneousReaction(pre="oj", post="hl"), _typeset=w_top.typeset
            )
        ),
        world=w_top,
    ),
    Goal(
        id="remove",
        description="keep free hands",
        contract=Contract(_guarantees=LTL(InfOft("!hl"), _typeset=w_top.typeset)),
        world=w_top,
    ),
}

spec_name = "spec"
output_folder: Path = Path(os.path.dirname(__file__)) / "output" / "top"

g = g_composition(goals_top)
g.realize()
save_to_file(
    file_content=g.controller.spec.to_str,
    file_name=spec_name,
    absolute_folder_path=output_folder,
)
g.controller.save("png", file_name=spec_name, absolute_folder_path=output_folder)
simulation = g.controller.mealy.simulate(50)
save_to_file(
    file_content=simulation,
    file_name=f"{spec_name}_run",
    absolute_folder_path=output_folder,
)
print(g.controller.mealy)
print(simulation)
