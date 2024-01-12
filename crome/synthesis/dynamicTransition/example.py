import os
import Path

from crome.synthesis.controller import Controller


controller_name = "arbiter"
spec_path = Path(os.path.abspath(os.path.dirname(__file__)))
controller_spec = "spec.txt"

print(f"controller selected: {controller_spec}")
