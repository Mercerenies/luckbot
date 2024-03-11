
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Callable

_T_co = TypeVar("_T_co", covariant=True)
_S = TypeVar("_S")
_U = TypeVar("_U")


@dataclass(frozen=True)
class DieResult(Generic[_T_co]):
    value: _T_co
    images: list[str] = field(default_factory=list)

    def map(self, callback: Callable[[_T_co], _S]) -> "DieResult[_S]":
        return DieResult(callback(self.value), self.images)

    def concat(self, other: 'DieResult[_S]', by: Callable[[_T_co, _S], _U]) -> "DieResult[_U]":
        return DieResult(by(self.value, other.value), self.images + other.images)
