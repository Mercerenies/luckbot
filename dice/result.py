
from dataclasses import dataclass
from typing import TypeVar, Generic, Optional, Callable

_T_co = TypeVar("_T_co", covariant=True)
_S = TypeVar("_S")


@dataclass(frozen=True)
class DieResult(Generic[_T_co]):
    value: _T_co
    image: Optional[str] = None

    def map(self, callback: Callable[[_T_co], _S]) -> "DieResult[_S]":
        return DieResult(callback(self.value), self.image)
