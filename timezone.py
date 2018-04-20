
import re

_TIMEZONES = {}
_PTN = re.compile(r'^UTC([-+]\d+)(?::(\d+))?$')

def time(hrs, mins):
    return hrs + mins / 60

class Timezone:

    def __init__(self, abbr, name, offset):
        self.abbr = abbr
        self.name = name
        self.offset = offset

    def to_gmt(self, time):
        return time - self.offset

    def from_gmt(self, time):
        return time + self.offset

def convert(hrs, mins, frm, to):
    t = time(hrs, mins)
    gmt = _TIMEZONES[frm].to_gmt(t)
    res = _TIMEZONES[to].from_gmt(gmt)
    return (res // 1, (res % 1) * 60)

def convert_formatted(time, frm, to):
    match = re.match(r'^(\d+)(?::(\d+))? ?(am|pm|AM|PM)?', time)
    if not match:
        return None
    grp = list(match.groups())
    grp[0] = int(grp[0])
    grp[1] = int(grp[1] or 0)
    grp[-1] = grp[-1] or ''
    if grp[-1].upper() == 'AM' or grp[-1].upper() == 'PM':
        if grp[-1].upper() == 'AM':
            pass
        elif grp[-1].upper() == 'PM':
            grp[0] += 12
    return convert(grp[0], grp[1], frm, to)

def is_timezone(tz):
    return tz.upper() in _TIMEZONES

def timezone_name(tz):
    if not is_timezone(tz):
        return None
    return _TIMEZONES[tz].name

with open("timezone1.txt") as f:
    for line in f:
        curr = line.split("\t")
        if len(curr) != 3:
            print("Invalid Word Count Error on:", curr)
            exit(1)
        abbr, name, zone = curr
        match = re.match(_PTN, zone)
        if not match:
            print("Invalid Format Error on:", curr)
            exit(1)
        hrs = int(match.group(1))
        mins = int(match.group(2) or 0)
        if abbr in _TIMEZONES:
            print("Duplicate Error on:", curr)
            exit(1)
        _TIMEZONES[abbr] = Timezone(abbr, name, time(hrs, mins))
