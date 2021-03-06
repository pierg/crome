from __future__ import annotations

from typing import TYPE_CHECKING, Set, Union

import spot

from core.contract import Contract, IncompatibleContracts, InconsistentContracts
from core.controller import Controller
from core.controller.exceptions import ControllerException
from core.crometypes import Boolean
from core.goal.exceptions import (
    GoalAlgebraOperationFail,
    GoalException,
    GoalFailOperations,
    GoalSynthesisFail,
)
from core.specification import Specification
from tools.storage import Store
from tools.strings import StringMng
from tools.strix import Strix

if TYPE_CHECKING:
    from core.world import World


class Goal:
    def __init__(
        self,
        name: str = None,
        description: str = None,
        id: str = None,
        specification: Union[Specification, Contract] = None,
        context: Union[Specification, Boolean] = None,
        world: World = None,
        viewpoint: str = None,
    ):

        """Read only properties."""
        self.__realizable = None
        self.__controller = None

        self._custom_id = id

        """Properties defined on first instantiation"""
        self.name: str = name
        self.description: str = description
        self.specification: Contract = specification
        self.context: Specification = context
        self.world: World = world
        if viewpoint is None:
            self.viewpoint = self.specification.typeset.extract_viewpoint()
        else:
            self.viewpoint: str = viewpoint

        """Name of the session (i.e. the subfolder in the output folder)"""
        self.__session_name = None
        self._synth_time = -1

    def __str__(self):
        return Goal.pretty_print_goal(self)

    def __le__(self, other: Goal):
        return self.specification <= other.specification

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    @property
    def id(self) -> str:
        return self.__id

    @property
    def session_name(self) -> str:
        return self.__session_name

    @session_name.setter
    def session_name(self, value: str):
        self.__session_name: str = value

    @property
    def goal_folder_name(self) -> str:
        if self.name.startswith("SCEN"):
            return self.name
        else:
            return self.id

    @property
    def s_controller_folder_name(self) -> str:
        return "s_controllers"

    @name.setter
    def name(self, value: str):
        self.__name, self.__id = StringMng.get_name_and_id(value)
        if self._custom_id is not None:
            self.__id = self._custom_id

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, value: str):
        if value is None:
            self.__description: str = ""
        else:
            self.__description: str = value

    @property
    def specification(self) -> Contract:
        return self.__specification

    @specification.setter
    def specification(self, value: Union[Contract, Specification]):
        if isinstance(value, Contract):
            self.__specification: Contract = value
        elif isinstance(value, Specification):
            self.__specification: Contract = Contract(guarantees=value)

    @property
    def context(self) -> Specification:
        return self.__context

    @context.setter
    def context(self, value: Union[Specification, Boolean]):
        if isinstance(value, Boolean):
            self.__context = value.to_atom()
        else:
            self.__context = value

    @property
    def world(self) -> World:
        return self.__world

    @world.setter
    def world(self, value: World):
        self.__world = value

    @property
    def realizable(self) -> bool:
        return self.__realizable

    @property
    def controller(self) -> Controller:
        return self.__controller

    @property
    def synth_time(self) -> float:
        return self._synth_time

    @synth_time.setter
    def synth_time(self, time):
        self._synth_time = time

    def translate_to_buchi(self):

        if self.session_name is None:
            folder_name = self.goal_folder_name
        else:
            folder_name = f"{self.session_name}/{self.goal_folder_name}"

        self.specification.assumptions.translate_to_buchi("assumptions", folder_name)
        self.specification.guarantees.translate_to_buchi("guarantees", folder_name)

    def realize_to_controller(self):
        """Realize the goal into a Controller object."""

        if self.controller is not None:
            return

        if self.session_name is None:
            folder_name = f"{self.s_controller_folder_name}/{self.goal_folder_name}"
        else:
            folder_name = f"{self.session_name}/{self.s_controller_folder_name}/{self.goal_folder_name}"

        try:
            controller_info = self.specification.get_controller_info()
            a, g, i, o = controller_info.get_strix_inputs()
            controller_synthesis_input = StringMng.get_controller_synthesis_str(
                controller_info
            )
            Store.save_to_file(
                controller_synthesis_input, "controller.txt", folder_name
            )
            realized, hoa_mealy, time = Strix.generate_controller(a, g, i, o)

            if not realized:
                controller_info = self.specification.get_controller_info(
                    world_ts=self.__world.typeset
                )
                a, g, i, o = controller_info.get_strix_inputs()
                controller_synthesis_input = StringMng.get_controller_synthesis_str(
                    controller_info
                )
                Store.save_to_file(
                    controller_synthesis_input, "controller.txt", folder_name
                )
                realized, hoa_mealy, time = Strix.generate_controller(a, g, i, o)

            self.__realizable = realized

            if realized:
                path = Store.save_to_file(hoa_mealy, "controller_hoa", folder_name)
                automaton = spot.automaton(path)
                dot_format = automaton.to_str(format="dot")
                Store.generate_eps_from_dot(dot_format, "controller_dot", folder_name)
                # Store.generate_eps_from_dot(dot_mealy, "controller", folder_name)
            else:
                Store.save_to_file(hoa_mealy, "controller_inverted_hoa", folder_name)
                # Store.generate_eps_from_dot(dot_mealy, "controller_inverted", folder_name)

            # self.__controller = Controller(
            #     mealy_machine=hoa_mealy,
            #     world=self.world,
            #     name=self.name,
            #     synth_time=time,
            # )
            self.synth_time = time
            # print(f"NAME:\t{self.__name} ({self.__id})")
            # print(self.__controller)
            # Store.save_to_file(str(self.__controller), "controller_table", folder_name)

        except ControllerException as e:
            raise GoalSynthesisFail(self, e)

    @staticmethod
    def pretty_print_goal(goal: Goal, level=0):
        ret = "\t" * level + f"|---GOAL\t {goal.id} {repr(goal.name)}\n"
        if goal.context is not None:
            ret += "\t" * level + f"|\tCONTEXT:\t {str(goal.context)}\n"
        if not goal.specification.assumptions.is_true():
            ret += "\t" * level + "|\t  ASSUMPTIONS:\n"
            ret += "\t" * level + f"|\t  {str(goal.specification.assumptions)} \n"
        ret += "\t" * level + "|\t  GUARANTEES:\n"
        ret += "\t" * level + f"|\t  {str(goal.specification.guarantees)} \n"
        if goal.realizable is not None:
            if goal.realizable:
                ret += (
                    "\t" * level + f"|\t  REALIZABLE:\tYES\t{goal.synth_time} seconds\n"
                )
            else:
                ret += "\t" * level + f"|\t  REALIZABLE:\tNO\n"
        return ret

    @staticmethod
    def composition(
        goals: Set[Goal], name: str = None, description: str = None
    ) -> Goal:
        if name is None:
            names = []
            for goal in goals:
                names.append(goal.name)
            names.sort()
            conj_name = ""
            for name in names:
                conj_name += name + "||"
            name = conj_name[:-2]

        set_of_contracts = set()
        new_goal_world = None
        for g in goals:
            set_of_contracts.add(g.specification)
            if g.world is not None:
                if new_goal_world is None:
                    new_goal_world = g.world
                else:
                    if not new_goal_world.equals(g.world):
                        raise GoalException(
                            "conjoining goals that have different 'variables'"
                        )

        try:
            new_contract = Contract.composition(set_of_contracts)

        except IncompatibleContracts as e:

            raise GoalAlgebraOperationFail(
                goals=goals, operation=GoalFailOperations.composition, contr_ex=e
            )

        except InconsistentContracts as e:

            raise GoalAlgebraOperationFail(
                goals=goals, operation=GoalFailOperations.composition, contr_ex=e
            )

        except UnfeasibleContracts as e:

            raise GoalAlgebraOperationFail(
                goals=goals, operation=GoalFailOperations.composition, contr_ex=e
            )

        new_goal = Goal(
            name=name,
            description=description,
            specification=new_contract,
            world=new_goal_world,
        )

        return new_goal

    @staticmethod
    def conjunction(
        goals: Set[Goal], name: str = None, description: str = None
    ) -> Goal:
        if name is None:
            names = []
            for goal in goals:
                names.append(goal.name)
            names.sort()
            conj_name = ""
            for name in names:
                conj_name += name + "^^"
            name = conj_name[:-2]

        set_of_contracts = set()

        new_goal_world = None
        for g in goals:
            set_of_contracts.add(g.specification)
            if g.world is not None:
                if new_goal_world is None:
                    new_goal_world = g.world
                else:
                    if not new_goal_world.equals(g.world):
                        raise GoalException(
                            "conjoining goals that have different 'variables'"
                        )

        try:
            new_contract = Contract.conjunction(set_of_contracts)

        except InconsistentContracts as e:

            raise GoalAlgebraOperationFail(
                goals=goals, operation=GoalFailOperations.conjunction, contr_ex=e
            )

        new_goal = Goal(
            name=name,
            description=description,
            specification=new_contract,
            world=new_goal_world,
        )

        return new_goal

    @staticmethod
    def merging(goals: Set[Goal], name: str = None, description: str = None) -> Goal:

        if name is None:
            names = []
            for goal in goals:
                names.append(goal.name)
            names.sort()
            conj_name = ""
            for name in names:
                conj_name += name + "**"
            name = conj_name[:-2]

        set_of_contracts = set()

        new_goal_world = None
        for g in goals:
            set_of_contracts.add(g.specification)
            if g.world is not None:
                if new_goal_world is None:
                    new_goal_world = g.world
                else:
                    if not new_goal_world.equals(g.world):
                        raise GoalException(
                            "merging goals that have different 'variables'"
                        )

        try:
            new_contract = Contract.merging(set_of_contracts)

        except InconsistentContracts as e:

            raise GoalAlgebraOperationFail(
                goals=goals, operation=GoalFailOperations.merging, contr_ex=e
            )

        new_goal = Goal(
            name=name,
            description=description,
            specification=new_contract,
            world=new_goal_world,
        )

        return new_goal

    @staticmethod
    def disjunction(
        goals: Set[Goal], name: str = None, description: str = None
    ) -> Goal:
        if name is None:
            names = []
            for goal in goals:
                names.append(goal.name)
            names.sort()
            conj_name = ""
            for name in names:
                conj_name += name + "vv"
            name = conj_name[:-2]

        set_of_contracts = set()

        new_goal_world = None
        for g in goals:
            set_of_contracts.add(g.specification)
            if g.world is not None:
                if new_goal_world is None:
                    new_goal_world = g.world
                else:
                    if not new_goal_world.equals(g.world):
                        raise GoalException(
                            "disjoining goals that have different 'variables'"
                        )

        try:
            new_contract = Contract.disjunction(set_of_contracts)

        except InconsistentContracts as e:

            raise GoalAlgebraOperationFail(
                goals=goals, operation=GoalFailOperations.conjunction, contr_ex=e
            )

        new_goal = Goal(
            name=name,
            description=description,
            specification=new_contract,
            world=new_goal_world,
        )

        return new_goal

    @staticmethod
    def quotient(dividend: Goal, divisor: Goal) -> Goal:

        name = f"({dividend.name}/{divisor.name})"

        set_of_contracts = set()

        new_goal_world = None
        for g in {dividend, divisor}:
            set_of_contracts.add(g.specification)
            if g.world is not None:
                if new_goal_world is None:
                    new_goal_world = g.world
                else:
                    if not new_goal_world.equals(g.world):
                        raise GoalException(
                            "quotient on goals that have different 'variables'"
                        )

        try:
            new_contract = Contract.quotient(
                dividend.specification, divisor.specification
            )

        except InconsistentContracts as e:

            raise GoalAlgebraOperationFail(
                goals={dividend, divisor},
                operation=GoalFailOperations.quotient,
                contr_ex=e,
            )

        new_goal = Goal(
            name=name,
            description=f"Quotient between {dividend.name} and {divisor.name}",
            specification=new_contract,
            world=new_goal_world,
        )

        return new_goal

    @staticmethod
    def separation(dividend, divisor: Goal) -> Goal:

        name = f"({dividend.name}:{divisor.name})"

        set_of_contracts = set()

        new_goal_world = None
        for g in {dividend, divisor}:
            set_of_contracts.add(g.specification)
            if g.world is not None:
                if new_goal_world is None:
                    new_goal_world = g.world
                else:
                    if not new_goal_world.equals(g.world):
                        raise GoalException(
                            "separation on goals that have different 'variables'"
                        )

        try:
            new_contract = Contract.separation(
                dividend.specification, divisor.specification
            )

        except InconsistentContracts as e:

            raise GoalAlgebraOperationFail(
                goals={dividend, divisor},
                operation=GoalFailOperations.separation,
                contr_ex=e,
            )

        new_goal = Goal(
            name=name,
            description=f"Separation between {dividend.name} and {divisor.name}",
            specification=new_contract,
            world=new_goal_world,
        )

        return new_goal

    @staticmethod
    def disjunction(
        goals: Set[Goal], name: str = None, description: str = None
    ) -> Goal:
        if name is None:
            names = []
            for goal in goals:
                names.append(goal.name)
            names.sort()
            conj_name = ""
            for name in names:
                conj_name += name + "vv"
            name = conj_name[:-2]

        set_of_contracts = set()

        new_goal_world = None
        for g in goals:
            set_of_contracts.add(g.specification)
            if g.world is not None:
                if new_goal_world is None:
                    new_goal_world = g.world
                else:
                    if not new_goal_world.equals(g.world):
                        raise GoalException(
                            "disjoining goals that have different 'variables'"
                        )

        try:
            new_contract = Contract.disjunction(set_of_contracts)

        except InconsistentContracts as e:

            raise GoalAlgebraOperationFail(
                goals=goals, operation=GoalFailOperations.conjunction, contr_ex=e
            )

        new_goal = Goal(
            name=name,
            description=description,
            specification=new_contract,
            world=new_goal_world,
        )

        return new_goal
