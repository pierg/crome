import os
from pathlib import Path

from crome.synthesis.rule import Rule

from crome.cgg.case_studies.robocup.world.world_ref import w_ref
from crome.contracts.contract import Contract
from crome.cgg.goal import Goal
from crome.cgg.goal.operations.composition import g_composition
from crome.logic.patterns.robotic_triggers import InstantaneousReaction
from crome.logic.specification.temporal import LTL
from crome.logic.tools.crome_io import save_to_file

folder_spec_name: str = "clean"
output_folder: Path = (
    Path(os.path.dirname(__file__)).parent / "output" / "ref" / folder_spec_name
)

"""Environment Rules"""
w_ref.environment_rules = {
    Rule(
        description="Object infinitely often",
        specification=LTL("GF(oj) & GF(!oj)", _typeset=w_ref.typeset),
    )
}

"""System Rules"""
w_ref.system_rules = {
    Rule(
        description="keep robots with free hands",
        specification=LTL("GF(!hl)", _typeset=w_ref.typeset),
    ),
    Rule(
        description="keep holding unless the robot drops the object",
        specification=LTL("G((hl & !dp) -> X hl)", _typeset=w_ref.typeset),
    ),
    Rule(
        description="if it drops the object then it does not hold anymore in the next step",
        specification=LTL("G(dp -> X !hl)", _typeset=w_ref.typeset),
    ),
    Rule(
        description="if it drops an object in the next step then it is holding an object currently",
        specification=LTL("G((X dp) -> hl)", _typeset=w_ref.typeset),
    ),
}


goals = {
    Goal(
        id="g1",
        description="drop only when you are in the garbage location and you're holding an object",
        contract=Contract(
            _guarantees=LTL(
                InstantaneousReaction(pre="dp", post="k3 & hl"), _typeset=w_ref.typeset
            )
        ),
        world=w_ref,
    )
}

g = g_composition(goals)
g.realize()
save_to_file(
    file_content=g.controller.spec.to_str,
    file_name="spec",
    absolute_folder_path=output_folder,
)
g.controller.save("png", file_name="spec", absolute_folder_path=output_folder)
simulation = g.controller.simulate(50)
save_to_file(
    file_content=simulation, file_name=f"run", absolute_folder_path=output_folder
)
print(g.controller.mealy)
print(simulation)
