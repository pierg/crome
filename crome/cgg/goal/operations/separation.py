from crome.cgg.cgg import Cgg, Link
from crome.cgg.context import group_conjunction
from crome.contracts.contract.exceptions import ContractException
from crome.cgg.goal import Goal
from crome.cgg.goal.exceptions import GoalAlgebraOperationFail, GoalFailOperations
from crome.cgg.goal.operations._shared import (
    GoalOperation,
    generate_goal_operations_name_description,
    generate_shared_world,
)
from crome.cgg.operations.separation import separation


def g_separation(dividend: Goal, divisor: Goal, cgg: Cgg | None = None) -> Goal:
    if dividend is None:
        raise Exception("No dividend specified in the separation")
    if divisor is None:
        raise Exception("No divisor specified in the separation")

    world = generate_shared_world({dividend, divisor})

    id, description = generate_goal_operations_name_description(
        [dividend, divisor], GoalOperation.Separation
    )

    context = group_conjunction(set(map(lambda g: g.context, {dividend, divisor})))

    try:
        contract = separation(dividend.contract, divisor.contract)

    except ContractException as e:

        raise GoalAlgebraOperationFail(
            goals={dividend, divisor},
            operation=GoalFailOperations.separation,
            contr_ex=e,
        )

    goal = Goal(
        contract=contract,
        id=id,
        description=description,
        context=context,
        world=world,
    )

    # Fix Cgg
    if cgg is not None:
        cgg.add_edge(node_a=dividend, node_b=goal, link=Link.separation_dividend)
        cgg.add_edge(node_a=divisor, node_b=goal, link=Link.separation_divisor)

    return goal
