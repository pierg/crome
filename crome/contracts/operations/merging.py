from copy import deepcopy

from crome.contracts.contract import Contract, ContractOperation


def merging(contracts: set[Contract]) -> Contract:
    if len(contracts) == 1:
        return next(iter(contracts))
    if len(contracts) == 0:
        raise Exception("No contract specified in the merging")

    contract_list = list(contracts)
    new_assumptions = deepcopy(contract_list[0].liveness_assumptions)
    new_guarantees = deepcopy(contract_list[0].liveness_guarantees)

    for contract in contract_list[1:]:
        new_assumptions &= contract.liveness_assumptions
        new_guarantees &= contract.liveness_guarantees

    new_guarantees = new_guarantees | ~new_assumptions

    return Contract.from_operation(
        liveness_guarantees=new_guarantees,
        liveness_assumptions=new_assumptions,
        generated_by=ContractOperation.MERGING,
        generators=contracts,
    )
