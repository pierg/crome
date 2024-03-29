from crome.logic.specification.temporal import LTL
from crome.logic.typeset import Typeset

from crome.synthesis.controller import Controller


def example() -> None:
    a = LTL("G(F(a)) & G(F(b))", _typeset=Typeset.from_aps(uncontrollable={"a", "b"}))
    g = LTL(
        "G(a <-> x) & F(x) & G(b <->y) & F(y)",
        _typeset=Typeset.from_aps(uncontrollable={"a", "b"}, controllable={"x", "y"}),
    )
    spec = a >> g
    print(spec)
    print("\n")
    c_spec = Controller(guarantees=spec, name="spec")
    print(c_spec.mealy)


if __name__ == "__main__":
    example()
