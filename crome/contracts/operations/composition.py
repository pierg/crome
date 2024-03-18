from copy import deepcopy

from crome.contracts.contract import Contract, ContractOperation


def composition(contracts: set[Contract]) -> Contract:
    if len(contracts) == 1:
        return next(iter(contracts))
    if len(contracts) == 0:
        raise Exception("No contract specified in the composition")

    contract_list = list(contracts)
    new_assumptions = deepcopy(contract_list[0].liveness_assumptions)
    new_guarantees = deepcopy(contract_list[0].liveness_guarantees)

    for contract in contract_list[1:]:
        new_assumptions &= contract.liveness_assumptions
        new_guarantees &= contract.liveness_guarantees

    new_assumptions |= ~new_guarantees

    return Contract.from_operation(
        liveness_guarantees=new_guarantees,
        liveness_assumptions=new_assumptions,
        generated_by=ContractOperation.COMPOSITION,
        generators=contracts,
    )
