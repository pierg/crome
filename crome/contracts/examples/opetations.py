from crome.contracts.contract import Contract
from crome.contracts.operations.composition import composition
from crome.contracts.operations.conjunction import conjunction
from crome.contracts.operations.merging import merging
from crome.contracts.operations.quotient import quotient
from crome.contracts.operations.separation import separation
from crome.logic.specification.temporal import LTL


def example() -> None:
    a = LTL("GF(sens)")
    g = LTL("GF(r1 & r2)")
    print(a)
    print(g)

    c1 = Contract(_liveness_assumptions=a, _liveness_guarantees=g)

    print(c1)

    c2 = Contract(_liveness_assumptions=LTL("G(F(a1))"), _liveness_guarantees=LTL("G(a1 <-> (b1 | c1))"))

    print(c2)

    c = composition({c1, c2})

    print(c)

    c2 = quotient(dividend=c, divisor=c1)

    print(c2)

    c = conjunction({c1, c2})

    print(c)

    c = merging({c1, c2})

    print(c)

    c1 = separation(dividend=c, divisor=c2)

    print(c1)


if __name__ == "__main__":
    example()
