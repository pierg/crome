import subprocess
import platform
from typing import Tuple

from tools.logic import Logic

import time
import docker

from tools.strings import StringMng
from tools.strix.exceptions import *


class Strix:

    @staticmethod
    def generate_controller(
            assumptions: str, guarantees: str, ins: str, outs: str
    ) -> Tuple[bool, str, float]:
        """It returns:
        bool: indicating if a contorller has been synthetised
        str: mealy machine of the controller (if found) or of the counter-examples if not found in dot format
        float: indicating the controller time"""

        command: str = ""
        timeout: int = -1

        """Fix syntax"""
        assumptions = StringMng.strix_syntax_fix(assumptions)
        guarantees = StringMng.strix_syntax_fix(guarantees)

        try:
            if ins == "":
                strix_specs = f"-f '{Logic.implies_(assumptions, guarantees)}' --outs='{outs}'"
            else:
                strix_specs = f"-f '{Logic.implies_(assumptions, guarantees)}' --ins='{ins}' --outs='{outs}'"

            strix_bin = "strix "

            command = f"{strix_bin} {strix_specs}"

            timeout = 3600
            print(f"RUNNING COMMAND:\n{command}")
            start_time = time.time()

            result = subprocess.check_output(
                [command], shell=True, timeout=timeout, encoding="UTF-8"
            ).splitlines()

        except subprocess.TimeoutExpired:
            raise SynthesisTimeout(command=command, timeout=timeout)
        except Exception as e:
            raise UnknownStrixResponse(command=command, response=str(e))

        exec_time = time.time() - start_time

        if "REALIZABLE" in result:
            realizable = True
        elif "UNREALIZABLE" in result:
            realizable = False
        else:
            raise UnknownStrixResponse(command=command, response="\n".join(result))

        processed_return = ""

        for i, line in enumerate(result):
            if "HOA" not in line:
                continue
            else:
                processed_return = "\n".join(result[i:])
                break

        return realizable, processed_return, exec_time

