
import deck

from typing import Dict, Any, Union, Callable, TypeVar, Generic, Optional, List

# Manager for the JSON storage data

T = TypeVar('T', bound='WithData[object]')
S_co = TypeVar('S_co', covariant=True)
K = TypeVar('K')

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
        if self.name not in instance.data:
            instance.data[self.name] = self.func(instance) # type: ignore
        return instance.data[self.name]

    def __set__(self, instance, value):
        instance.data[self.name] = value

    def __delete__(self, instance):
        if self.name in instance.data:
            del instance.data[self.name]

class JSONData(WithData[Any]):
    data: Dict[str, Any]

    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
        self.data = data or {}

    @dict_delegator
    def good(self) -> int:
        return 0

    @dict_delegator
    def bad(self) -> int:
        return 0

    @dict_delegator
    def linky(self) -> Optional[str]:
        return None

    @dict_delegator
    def key(self) -> str:
        return ""

    @property
    def roles(self) -> 'JSONCollection[int, RoleData]':
        if 'roles' not in self.data:
            self.data['roles'] = {}
        return JSONCollection(self.data['roles'], RoleData)

class JSONCollection(Generic[K, T], WithData[Any]):
    data: Dict[str, Any]
    ctor: Callable[[Any], T]

    def __init__(self, data: Dict[str, Any], ctor: Callable[[Any], T]) -> None:
        self.data = data
        self.ctor = ctor # type: ignore

    def __contains__(self, id: K) -> bool:
        return str(id) in self.data

    def __getitem__(self, id: K) -> T:
        return self.ctor(self.data[str(id)]) # type: ignore

    def __setitem__(self, id: K, v: T) -> None:
        self.data[str(id)] = v.data

    def __delitem__(self, id: K) -> None:
        del self.data[str(id)]

class RoleData(WithData[Any]):
    data: Dict[str, Any]

    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
        self.data = data or {}

    @dict_delegator
    def owners(self) -> List[int]:
        return []

    @dict_delegator
    def voluntary(self) -> bool:
        return False

    @dict_delegator
    def name(self) -> str:
        return ''

# TODO It's just a flat global right now. We should store this in the
# main file and pass it only to functions that need it.
json_data = JSONData()
