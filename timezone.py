
import re

from typing import Dict, NewType, Tuple, Optional

_TIMEZONES: Dict[str, 'Timezone'] = {}
_PTN = re.compile(r'^UTC([-+]\d+)(?::(\d+))?$')

Time = NewType('Time', float)

def time(hrs: int, mins: int) -> Time:
    return Time(hrs + mins / 60)

class Timezone:
    abbr: str
    name: str
    offset: Time

    def __init__(self, abbr: str, name: str, offset: Time) -> None:
        self.abbr = abbr
        self.name = name
        self.offset = offset

    def to_gmt(self, time: Time) -> Time:
        return Time(time - self.offset)

    def from_gmt(self, time: Time) -> Time:
        return Time(time + self.offset)

def convert(hrs: int, mins: int, frm: str, to: str) -> Tuple[int, int]:
    t = time(hrs, mins)
    gmt = _TIMEZONES[frm.upper()].to_gmt(t)
    res = _TIMEZONES[to.upper()].from_gmt(gmt)
    return (int(res // 1), int((res % 1) * 60))

def convert_formatted(time: str, frm: str, to: str) -> Optional[Tuple[int, int]]:
    match = re.match(r'^(\d+)(?::(\d+))? ?(am|pm|AM|PM)?$', time)
    if not match:
        return None
    grp = match.groups()
    hrs = int(grp[0])
    mins = int(grp[1] or 0)
    ampm = grp[-1] or ''
    if ampm.upper() == 'AM' or ampm.upper() == 'PM':
        if ampm.upper() == 'AM':
            pass
        elif ampm.upper() == 'PM':
            hrs += 12
    return convert(hrs, mins, frm, to)

def is_timezone(tz: str) -> bool:
    return tz.upper() in _TIMEZONES

def timezone_name(tz: str) -> Optional[str]:
    if not is_timezone(tz):
        return None
    return _TIMEZONES[tz.upper()].name

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
