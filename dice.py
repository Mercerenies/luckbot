
from permission import InputsTooLarge

import re
import random
from numbers import Complex
import alakazam as zz
from alakazam import _1, _2, _3, _4, _5

from typing import List, TypeVar, Generic, Sequence, Union, Callable, Optional, Tuple

class TooManyDice(InputsTooLarge):
    pass

T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)

MAXIMUM = 40
MAXIMUM_INDIVIDUAL = 99999

class AbstractDie(Generic[T_co]):

    def count(self) -> int:
        return 0

    def eval(self, arr: List[T_co]) -> T_co:
        raise NotImplementedError()

class Die(AbstractDie[int]):
    n: int
    x: int
    y: int

    def __init__(self, n: int, x: int, y: int) -> None:
        self.n = n
        self.x = x
        self.y = y

    def count(self) -> int:
        return self.n

    def eval(self, arr: List[int]) -> int:
        m = 0
        for i in range(self.n):
            j = random.randint(self.x, self.y)
            m += j
            arr.append(j)
        return m

    def __repr__(self) -> str:
        return "Die({!r}, {!r}, {!r})".format(self.n, self.x, self.y)

class ChoiceDie(AbstractDie[Union[str, int]]):
    n: int
    choices: Sequence[Union[str, int]]

    def __init__(self, n: int, choices: Sequence[Union[str, int]]) -> None:
        self.n = n
        self.choices = choices

    def count(self) -> int:
        return self.n

    def eval(self, arr: List[Union[int, str]]) -> Union[int, str]:
        m: Union[int, str] = ''
        for i in range(self.n):
            j = random.choice(self.choices)
            m = add_together(m, j)
            arr.append(j)
        return m

    def __repr__(self) -> str:
        return "ChoiceDie({!r}, {!r})".format(self.n, self.choices)

class Negate(AbstractDie[T_co]):
    expr: AbstractDie[T_co]

    def __init__(self, expr: AbstractDie[T_co]) -> None:
        self.expr = expr

    def count(self) -> int:
        return self.expr.count()

    def eval(self, arr: List[T_co]) -> T_co:
        return neg(self.expr.eval(arr))

    def __repr__(self):
        return "Negate({!r})".format(self.expr)

class Lit(AbstractDie[T_co]):
    n: T_co

    def __init__(self, n: T_co) -> None:
        self.n = n

    def count(self) -> int:
        return 0

    def eval(self, arr: List[T_co]) -> T_co:
        return self.n

    def __repr__(self) -> str:
        return "Lit({!r})".format(self.n)

class Oper(AbstractDie[T_co]):
    data: Sequence[AbstractDie[T_co]]
    oper: Callable[[T_co, T_co], T_co]

    def __init__(self, data: Sequence[AbstractDie[T_co]], oper: Callable[[T_co, T_co], T_co]) -> None:
        self.data = data
        self.oper = oper # type: ignore # (https://github.com/python/mypy/issues/5485)

    def count(self) -> int:
        return zz.of(self.data).map(lambda x: x.count()).sum()

    def eval(self, arr: List[T_co]) -> T_co:
        return zz.of(self.data).map(lambda x: x.eval(arr)).reduce(self.oper)

    def __repr__(self) -> str:
        return "Oper({!r}, {!r})".format(self.data, self.oper)

def neg(x: T) -> T:
    if isinstance(x, Complex):
        return - x
    else:
        return x # ???

def add_together(x: Union[int, str], y: Union[int, str]) -> Union[int, str]:
    if x == '':
        # Neutral monoidal element :)
        return y
    elif isinstance(x, Complex) and isinstance(y, Complex):
        return x + y
    else:
        return str(x) + str(y)

def _read_prefix(arg: str, value: str) -> Optional[Tuple[None, str]]:
    if arg.startswith(value):
        return None, arg[len(value):]
    return None

def _read_none(arg: str, value: Sequence[str]) -> Optional[Tuple[str, str]]:
    for s in value:
        if arg.startswith(s):
            return None
    return arg[:1], arg[1:]

def _read_number(arg: str) -> Optional[Tuple[Lit[int], str]]:
    match = re.match(r'\d+', arg)
    if match:
        return Lit(int(match.group(0))), arg[match.span()[1]:]
    return None

def _read_die(arg: str) -> Optional[Tuple[Die, str]]:
    test = _read_number(arg)
    if test:
        n0, arg1 = test
        n = n0.n
    else:
        n = 1
        arg1 = arg
    if not (_read_prefix(arg1, 'd') or _read_prefix(arg1, 'D')):
        return None
    arg2 = arg1[1:]
    test2 = _read_prefix(arg2, 'f') or _read_prefix(arg2, 'F')
    test1 = _read_number(arg2)
    if test2:
        x = -1
        y = 1
        _, arg3 = test2
    elif test1:
        x = 1
        y0, arg3 = test1
        y = y0.n
    else:
        x = 1
        y = 6
        arg3 = arg2
    if y < x:
        return None
    if x > MAXIMUM_INDIVIDUAL or y > MAXIMUM_INDIVIDUAL:
        raise InputsTooLarge()
    return Die(n=n, x=x, y=y), arg3

def _read_str(arg: str, chars: Callable[[str], Optional[Tuple[str, str]]]) -> Optional[Tuple[str, str]]:
    m = ""
    while True:
        curr = chars(arg)
        if not curr:
            break
        x, arg = curr
        m += x
    return m, arg

def _read_str_lit(arg: str) -> Optional[Tuple[Lit[str], str]]:
    if not (_read_prefix(arg, "'")):
        return None
    arg = arg[1:]
    match = _read_str(arg, lambda a: _read_none(a, "'"))
    if not match:
        return None
    m, arg = match
    if not (_read_prefix(arg, "'")):
        return None
    arg = arg[1:]
    return Lit(m), arg

def _read_choice_die(arg: str) -> Optional[Tuple[ChoiceDie, str]]:
    test = _read_number(arg)
    if test:
        n0, arg = test
        n = n0.n
    else:
        n = 1
        arg = arg
    if not (_read_prefix(arg, 'd') or _read_prefix(arg, 'D')):
        return None
    if not (_read_prefix(arg[1:], '[')):
        return None
    arg = arg[2:]
    fst = _read_str(arg, lambda a: _read_none(a, ',]'))
    if not fst:
        return None
    t0, arg = fst
    arr: List[Union[int, str]] = [t0]
    while True:
        sgn = _read_prefix(arg, ',')
        if sgn:
            sgn1, arg = sgn
        else:
            break
        nxt = _read_str(arg, lambda a: _read_none(a, ',]'))
        if nxt:
            t1: Union[int, str]
            t1, arg = nxt
            if re.match(r'[-+]?\d+$', t1):
                t1 = int(t1)
            arr.append(t1)
        else:
            return None
    if not (_read_prefix(arg, ']')):
        return None
    return ChoiceDie(n, arr), arg[1:]

def _read_paren(arg: str) -> Optional[Tuple[AbstractDie[Union[int, str]], str]]:
    if not _read_prefix(arg, '('):
        return None
    arg = arg[1:]
    res = _read_datum(arg)
    if res:
        res0, arg = res
    else:
        return None
    if not _read_prefix(arg, ')'):
        return None
    return res0, arg[1:]

def _read_term(arg: str) -> Optional[Tuple[AbstractDie[Union[int, str]], str]]:
    return (_read_paren(arg) or
            _read_adv(arg) or
            _read_str_lit(arg) or
            _read_choice_die(arg) or
            _read_die(arg) or
            _read_number(arg))

def _read_adv(arg: str) -> Optional[Tuple[Oper[Union[int, str]], str]]:
    test0 = _read_number(arg)
    if test0:
        n0, arg1 = test0
        n = n0.n
    else:
        n = 2
        arg1 = arg
    if n <= 0:
        return None
    if _read_prefix(arg1, '!'):
        op = max
    elif _read_prefix(arg1, '?'):
        op = min
    else:
        return None
    arg1 = arg1[1:]
    test = _read_term(arg1)
    if test:
        inner, arg2 = test
        return Oper(zz.repeat(inner, n=n).list(), op), arg2
    else:
        return None

def _read_datum(arg: str) -> Optional[Tuple[Oper[Union[int, str]], str]]:
    return _read_seq(arg)

def _read_sign(arg: str) -> Optional[Tuple[int, str]]:
    if _read_prefix(arg, '+'):
        return 1, arg[1:]
    elif _read_prefix(arg, '-'):
        return -1, arg[1:]
    else:
        return None

def _read_seq(arg: str) -> Optional[Tuple[Oper[Union[int, str]], str]]:
    fst = _read_term(arg)
    if not fst:
        return None
    t0, arg = fst
    arr = [t0]
    while True:
        sgn = _read_sign(arg)
        if sgn:
            sgn1, arg = sgn
        else:
            break
        nxt = _read_term(arg)
        if nxt:
            t1, arg = nxt
            if sgn1 < 0:
                arr.append(Negate(t1))
            else:
                arr.append(t1)
        else:
            return None
    return Oper(arr, add_together), arg

def parse_dice(string: str) -> Optional[AbstractDie[Union[int, str]]]:
    string = re.subn(r'\s', '', string)[0]
    res = _read_datum(string)
    if not res:
        return None
    res0, string1 = res
    if string1 != "":
        return None
    return res0

def dice(string: str) -> Optional[Tuple[Union[int, str], List[Union[int, str]]]]:
    a = parse_dice(string)
    if a:
        if a.count() > MAXIMUM:
            raise TooManyDice()
        x: List[Union[int, str]] = []
        return a.eval(x), x
    else:
        return None
