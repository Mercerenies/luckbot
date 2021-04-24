
from typing import Dict, Any, Union, Callable, TypeVar, Generic, Optional

# Manager for the JSON storage data

T = TypeVar('T', bound='WithData[object]')
S_co = TypeVar('S_co', covariant=True)

class WithData(Generic[S_co]):
    data: Dict[str, S_co]

class dict_delegator(Generic[T, S_co]):
    func: Callable[[T], S_co]

    def __init__(self, func: Callable[[T], S_co]) -> None:
        self.func = func # type: ignore

    @property
    def name(self):
        return self.func.__name__

    def __get__(self, instance: T, _owner):
        if self.name in instance.data:
            return instance.data[self.name]
        else:
            return self.func(instance) # type: ignore

    def __set__(self, instance, value):
        instance.data[self.name] = value

    def __delete__(self, instance):
        if self.name in instance.data:
            del instance.data[self.name]

class JSONData(WithData[Any]):
    data: Dict[str, Any]

    def __init__(self, data):
        self.data = data

    def __getitem__(self, idx):
        return self.data[idx]

    def __setitem__(self, idx, v):
        self.data[idx] = v

    def __contains__(self, idx):
        return idx in self.data

    @dict_delegator
    def good(self) -> int:
        return 0

    @dict_delegator
    def bad(self) -> int:
        return 0

    @dict_delegator
    def linky(self) -> Optional[str]:
        return None
