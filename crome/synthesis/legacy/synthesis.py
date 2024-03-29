import spot
from crome.logic.specification.temporal import LTL
from crome.logic.tools.crome_io import save_to_file
from crome.logic.typelement.robotic import BooleanAction, BooleanSensor
from crome.logic.typeset import Typeset

from crome.synthesis.controller import Controller
from crome.synthesis.controller.synthesis import generate_controller


def example() -> None:
    a = LTL(
        _init_formula="G(F(sens))",
        _typeset=Typeset({BooleanSensor(name="sens")}),
    )
    g = LTL(
        _init_formula="G(sens -> act)",
        _typeset=Typeset({BooleanAction(name="act")}),
    )
    controller = Controller(assumptions=a, guarantees=g)
    controller.save("dot")
    controller.save("lbtt")


def example_1() -> None:
    a1: str = "G(F(a1))"
    g1: str = "G(a1 <-> (b1 | c1))"
    i1: str = "a1"
    o1: str = "b1, c1"

    realizable1, controller1, time1 = generate_controller(a1, g1, i1, o1)

    print(f"\n\n{controller1}")
    file_path = save_to_file(controller1, "controller_1")

    automaton = spot.automaton(file_path)
    dotfile = automaton.to_str(format="dot")
    print(f"\n\n{dotfile}")

    lbtt = automaton.to_str(format="lbtt")
    print(f"\n\n{lbtt}")

    sens: str = "G(F(sens))"
    g2: str = "G(sens -> act)"
    i2: str = "sens"
    o2: str = "act"

    realizable2, controller2, time2 = generate_controller(sens, g2, i2, o2)

    print(f"\n\n{controller2}")


if __name__ == "__main__":
    example()
