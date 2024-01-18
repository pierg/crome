from crome.logic.specification.temporal import LTL
from crome.logic.tools.logic import Logic


def generateBasicExample():

    ## TODO: pasarlas a otro archivo o usar directamente de los contratos

    input_variables = ""
    output_variables = "r1,r2,r3,r4,r5, allowed, switch"

    exclude_rules = []
    for i in range(1, 6):
        exclude_rule = f"r{i}"
        for j in range(1, 6):
            if i != j:
                exclude_rule += f" & !r{j}"
        exclude_rules.append("(" + exclude_rule + ")")
    safety_exclude = ("G " + Logic.or_([safety_exclude_rule for safety_exclude_rule in exclude_rules]))

    # TODO ^ esto sería el mundo de la grilla no? cómo podemos sacar la fórmula desde el gridworld?
    rho_1 = LTL(
        "(!r2 U r1) & G(r2 -> X(!r2 U r1)) & G(r1 -> X(!r1 U r2)) & " + str(safety_exclude))  # day_safety_system
    rho_2 = LTL(
        "(!r4 U r3) & G(r4 -> X(!r4 U r3)) & G(r3 -> X(!r3 U r4)) & " + str(safety_exclude))  # night_safety_system
    current_pos = LTL("r1 & !r2 & !r3 & !r4 & !r5")
    target_pos = LTL("!r1 & !r2 & r3 & !r4 & !r5")
    switch_condition = True
    return rho_1, rho_2, current_pos, target_pos, switch_condition, input_variables,  output_variables



## this is the overleaf board robot example
def generateRobotPatrollingExample():
    input_variables = ""
    output_variables = "allowed, switch"

    for i in range(1, 6):
        output_variables += f"r{i}, "

    exclude_rules = []
    for i in range(1, 6):
        exclude_rule = f"r{i}"
        for j in range(1, 6):
            if i != j:
                exclude_rule += f" & !r{j}"
        exclude_rules.append("(" + exclude_rule + ")")
    safety_exclude = ("G " + Logic.or_([safety_exclude_rule for safety_exclude_rule in exclude_rules]))




    return