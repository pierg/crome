from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from crome.logic.typelement import TypeKind
from crome.logic.typelement.basic import Boolean


class Val(Enum):
    true = auto()
    false = auto()
    undefined = auto()


@dataclass
class Atom:
    typelement: Boolean
    value: Val = Val.undefined

    def __invert__(self):
        if self.value == Val.true:
            self.value = Val.false
        elif self.value == Val.false:
            self.value = Val.true
        else:
            raise AttributeError

    def is_compatible_with(self, other: Atom):
        if other.typelement == self.typelement:
            if (self.value == Val.true and other.value == Val.false) or (
                    self.value == Val.false and other.value == Val.true
            ):
                return False
        return True

    @property
    def is_any(self):
        return self.typelement.name == "TRUE"

    @property
    def name(self) -> str:
        return self.typelement.name

    def __str__(self):
        if self.is_any:
            return f"-"
        elif self.value == Val.false:
            return f"{self.typelement.name}!"
        elif self.value == Val.undefined:
            return f"{self.typelement.name}?"
        else:
            return f"{self.typelement.name} "

    def __hash__(self):
        return hash(f"{self.typelement.__hash__()}{str(self.value)}")


@dataclass
class Atoms:
    atoms: frozenset[Atom]

    def is_compatible_with(self, other: Atoms):
        pass

    def determinize_from(self, other: Atoms):
        pass

    @property
    def sorted(self) -> list[Atom]:
        data = list(self.atoms)
        data = sorted(data, key=lambda atom: atom.name)
        for i, a in enumerate(data):
            if a.typelement.kind == TypeKind.LOCATION and a.value == Val.true:
                data[0], data[i] = data[i], data[0]
        return data

    @classmethod
    def any(cls):
        return Atoms(frozenset({Atom(Boolean(name="TRUE"))}))

    @property
    def str_positive_only(self):
        return " ".join([str(a) for a in list(filter(lambda a: a.value == Val.true or a.is_any, self.sorted))])

    def __str__(self):
        return " ".join([str(a) for a in self.sorted])

    def __hash__(self):
        return hash(self.atoms)


class AtomValues:
    def __init__(self, typelement: Boolean):
        self._true: Atom = Atom(typelement=typelement, value=Val.true)
        self._false: Atom = Atom(typelement=typelement, value=Val.false)
        self._undefined: Atom = Atom(typelement=typelement, value=Val.undefined)

    @property
    def true(self):
        return self._true

    @property
    def false(self):
        return self._false

    @property
    def undefined(self):
        return self._undefined
