from crome.contracts.contract import Contract, ContractOperation


def quotient(dividend: Contract, divisor: Contract) -> Contract:
    if dividend is None:
        raise Exception("No dividend specified in the quotient")
    if divisor is None:
        raise Exception("No divisor specified in the quotient")

    # concretization({dividend, divisor})

    c = dividend
    a = c.liveness_assumptions
    g = c.liveness_guarantees

    c1 = divisor
    a1 = c1.liveness_assumptions
    g1 = c1.liveness_guarantees

    a2 = a & g1
    g2 = g & a1 | ~(a & g1)

    return Contract.from_operation(
        liveness_guarantees=g2,
        liveness_assumptions=a2,
        generated_by=ContractOperation.QUOTIENT,
        generators={"dividend": dividend, "divisor": divisor},
    )
