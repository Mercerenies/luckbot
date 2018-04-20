
import re
import random
from numbers import Number
import alakazam as zz
from alakazam import _1, _2, _3, _4, _5

MAXIMUM = 40

class Die:
    def __init__(self, n, x, y):
        self.n = n
        self.x = x
        self.y = y
    def count(self):
        return self.n
    def eval(self, arr):
        m = 0
        for i in range(self.n):
            j = random.randint(self.x, self.y)
            m += j
            arr.append(j)
        return m
    def __repr__(self):
        return "Die({!r}, {!r}, {!r})".format(self.n, self.x, self.y)

class ChoiceDie:
    def __init__(self, n, choices):
        self.n = n
        self.choices = choices
    def count(self):
        return self.n
    def eval(self, arr):
        m = ''
        for i in range(self.n):
            j = random.choice(self.choices)
            m = add_together(m, j)
            arr.append(j)
        return m
    def __repr__(self):
        return "ChoiceDie({!r}, {!r})".format(self.n, self.choices)

class Negate:
    def __init__(self, expr):
        self.expr = expr
    def count(self):
        return self.expr.count()
    def eval(self, arr):
        return neg(self.expr.eval(arr))
    def __repr__(self):
        return "Negate({!r})".format(self.expr)

class Lit:
    def __init__(self, n):
        self.n = n
    def count(self):
        return 0
    def eval(self, arr):
        return self.n
    def __repr__(self):
        return "Lit({!r})".format(self.n)

class Oper:
    def __init__(self, data, oper):
        self.data = data
        self.oper = oper
    def count(self):
        return zz.of(self.data).map(lambda x: x.count()).sum()
    def eval(self, arr):
        return zz.of(self.data).map(lambda x: x.eval(arr)).reduce(self.oper)
    def __repr__(self):
        return "Oper({!r}, {!r})".format(self.data, self.oper)

def neg(x):
    if isinstance(x, Number):
        return - x
    else:
        return x # ???

def add_together(x, y):
    if isinstance(x, Number) and isinstance(y, Number):
        return x + y
    else:
        return str(x) + str(y)

def _read_prefix(arg, value):
    if arg.startswith(value):
        return (), arg[len(value):]
    return None

def _read_none(arg, value):
    for s in value:
        if arg.startswith(s):
            return None
    return arg[:1], arg[1:]

def _read_number(arg):
    match = re.match(r'\d+', arg)
    if match:
        return Lit(int(match.group(0))), arg[match.span()[1]:]
    return None

def _read_die(arg):
    test = _read_number(arg)
    if test:
        n, arg1 = test
        n = n.n
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
        y, arg3 = test1
        y = y.n
    else:
        x = 1
        y = 6
        arg3 = arg2
    if y < x:
        return None
    return Die(n=n, x=x, y=y), arg3

def _read_str(arg, chars):
    m = ""
    while True:
        curr = chars(arg)
        if not curr:
            break
        x, arg = curr
        m += x
    return m, arg

def _read_str_lit(arg):
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

def _read_choice_die(arg):
    test = _read_number(arg)
    if test:
        n, arg = test
        n = n.n
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
    arr = [t0]
    while True:
        sgn = _read_prefix(arg, ',')
        if sgn:
            sgn1, arg = sgn
        else:
            break
        nxt = _read_str(arg, lambda a: _read_none(a, ',]'))
        if nxt:
            t1, arg = nxt
            if re.match(r'[-+]?\d+$', t1):
                t1 = int(t1)
            arr.append(t1)
        else:
            return None
    if not (_read_prefix(arg, ']')):
        return None
    return ChoiceDie(n, arr), arg[1:]

def _read_paren(arg):
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

def _read_term(arg):
    return (_read_paren(arg) or
            _read_adv(arg) or
            _read_str_lit(arg) or
            _read_choice_die(arg) or
            _read_die(arg) or
            _read_number(arg))

def _read_adv(arg):
    test = _read_number(arg)
    if test:
        n, arg1 = test
        n = n.n
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

def _read_datum(arg):
    return _read_seq(arg)

def _read_sign(arg):
    if _read_prefix(arg, '+'):
        return 1, arg[1:]
    elif _read_prefix(arg, '-'):
        return -1, arg[1:]

def _read_seq(arg):
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

def parse_dice(string):
    string = re.subn(r'\s', '', string)[0]
    res = _read_datum(string)
    if not res:
        return None
    res0, string1 = res
    if string1 != "":
        return None
    return res0

def dice(string):
    a = parse_dice(string)
    if a:
        if a.count() > MAXIMUM:
            return -1
        x = []
        return a.eval(x), x
    else:
        return None
