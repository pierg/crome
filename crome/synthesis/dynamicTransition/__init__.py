import os

from pathlib import Path

from crome.contracts.contract import Contract
from crome.logic.patterns.robotic_movement import StrictOrderedPatrolling
from crome.logic.specification.temporal import LTL
from crome.synthesis.controller import Controller


class DynamicTransition:

    def prepareLTL(self):
        controller_name = "arbiter"
        spec_path = Path(os.path.abspath(os.path.dirname(__file__)))
        controller_spec = spec_path / f"spec.txt"

        print(f"controller selected: {controller_spec}")

        # METHOD 1: MONOLITHIC SYNTHESIS FROM STRIX
        controller = Controller.from_file(file_path=controller_spec, name=controller_name)
        print(f"Monolithic synthesis realized in {controller.synth_time} s")


transition = DynamicTransition()
transition.prepareLTL()
contrato = Contract(LTL(StrictOrderedPatrolling(locations=["r1", "r2"]).__str__()))
pass