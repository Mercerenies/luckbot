#!/usr/bin/python3.5

#import sys

#sys.path.insert(0, './vendor/discord.py')
#sys.path.insert(0, './vendor/aiohttp')
#sys.path.insert(0, './vendor/attrs/src')
#sys.path.insert(0, './vendor/websockets/src')
#sys.path.insert(0, './vendor/yarl')

import discord
from discord.ext import commands
from io import StringIO, BytesIO
import random
import asyncio
import re
import json
import traceback
import time
import aiohttp
import asyncio

from grid import CodenameManager, GridConfig, DefaultWordList, CustomWordList
import dice
import timezone as tz
import alakazam as zz
from alakazam import _1, _2, _3, _4, _5

class PermissionsException(Exception):
    pass

description = '''Hi, I'm Luckbot! I provide several useful utilities to the Discord
Games server.'''
bot = commands.Bot(command_prefix='!', description=description)

def good_bot(message):
    json_data['good'] += 1
    yield from bot.send_message(message.channel, "You have voted this bot as a good bot. :robot:")

def bad_bot(message):
    json_data['bad'] += 1
    yield from bot.send_message(message.channel, "You have voted this bot as a bad bot. :frowning2:")

def name_to_role(name):
    return zz.of(bot.servers).map(_1.roles).flatten().find(_1.name == name)

def role_data():
    return json_data['roles']

def must_be_admin(member):
    if not isinstance(member, discord.Member):
        raise PermissionsException()
    if not member.server_permissions.administrator:
        raise PermissionsException()

def is_owner_of_role(member, role):
    if role.id not in role_data():
        return False
    data = role_data()[role.id]
    if 'owners' not in data:
        return False
    return member.id in data['owners']

def is_voluntary_role(role):
    if role.id not in role_data():
        return False
    data = role_data()[role.id]
    if 'voluntary' not in data:
        return False
    return data['voluntary']

def owner_list(server, role):
    if role.id not in role_data():
        return []
    data = role_data()[role.id]
    if 'owners' not in data:
        return []
    return zz.of(data['owners']).map(server.get_member).filter(_1).list()

def find_member(server, name):
    name = name.lower()
    def match(person):
        return (person.name.lower() == name or person.display_name.lower() == name)
    return zz.of(server.members).find(match)

autoreplies = [
    (r"\bgood bot\b", good_bot),
    (r"\bgood morning\b", "Good morning! :sunrise:"),
    (r"\bgood afternoon\b", "Good afternoon! :sunny:"),
    (r"\bgood night\b", "Good night! :city_sunset:"),
    (r"\bbad bot\b", bad_bot)
]
json_data = None

@bot.event
@asyncio.coroutine
def on_message(message):
    if (message.author == bot.user):
        return
    if (str(message.channel) == "general") or (str(message.channel) == "bot_testing-grounds"):
        for ptn, reply in autoreplies:
            if re.search(ptn, message.content, re.I):
                if callable(reply):
                    yield from reply(message)
                else:
                    yield from bot.send_message(message.channel, reply)
    yield from bot.process_commands(message)

@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
@asyncio.coroutine
def playing(*, mygame : str):
    """Sets my presence tagline"""
    yield from bot.change_presence(game=discord.Game(name=str(mygame)))

@bot.command()
@asyncio.coroutine
def genitem(*, item_name: str):
    """Generates an item"""
    #0 = Dex, 1 = Intr, 2 = Str, 3 = Cont, 4 = Wis
    stat_int = random.randint(0, 4)
    stat_range = random.randint(-3, 10)
    
    if ('dumb' in item_name):
        stat_int = 1
        stat_range = random.randint(-5, -1)
    
    if ('intelligence' in item_name):
        stat_int = 1
        stat_range = random.randint(1, 10)
        
    if ('weakness' in item_name):
        stat_int = 2
        stat_range = random.randint(-5, -1)
    
    if ('strength' in item_name):
        stat_int = 2
        stat_range = random.randint(1, 10)
        
    if ('slow' in item_name):
        stat_int = 0
        stat_range = random.randint(-5, -1)
    
    if ('speed' in item_name):
        stat_int = 0
        stat_range = random.randint(1, 10)
    
    if ('swiftness' in item_name):
        stat_int = 0
        stat_range = random.randint(1, 10)
    
    if ('drain' in item_name):
        stat_int = 3
        stat_range = random.randint(-5, -1)
    
    if ('protection' in item_name):
        stat_int = 3
        stat_range = random.randint(1, 10)
        
    if ('ignorance' in item_name):
        stat_int = 4
        stat_range = random.randint(-5, -1)
    
    if ('wisdom' in item_name):
        stat_int = 4
        stat_range = random.randint(1, 10)
    
    if (stat_range == 0):
        stat_range = 1
    stat = ""
    if (stat_int == 0):
        stat = "Dexterity"
        
    if (stat_int == 1):
        stat = "Intelligence"
    
    if (stat_int == 2):
        stat = "Strength"
    
    if (stat_int == 3):
        stat = "Constitution"
        
    if (stat_int == 4):
        stat = "Wisdom"
        
    if (stat_range < 0):
        yield from bot.say(str(item_name) + "\n" + stat + ": " + str(stat_range))
        
    if (stat_range > 0):
        yield from bot.say(str(item_name) + "\n" + stat + ": +" + str(stat_range))
        

@bot.command()
@asyncio.coroutine
def genchar(minlevel : int, maxlevel : int, pokemon : str):
    """Generates a character"""

    randlevel = random.randint(minlevel, maxlevel)
    dex = random.randint(-5, 5)
    itl = random.randint(-5, 5)
    sre = random.randint(-5, 5)
    con = random.randint(-5, 5)
    wis = random.randint(-5, 5)

    rarr = random.randint(randlevel, 100)
    if (rarr >= 80):
        dex += randlevel

    rarr = random.randint(randlevel, 100)
    if (rarr >= 80):
        itl += randlevel

    rarr = random.randint(randlevel, 100)
    if (rarr >= 80):
        sre += randlevel

    rarr = random.randint(randlevel, 100)
    if (rarr >= 80):
        con += randlevel

    rarr = random.randint(randlevel, 100)
    if (rarr >= 80):
        wis += randlevel

    hlt = (4*randlevel) + con
    xpr = hlt - (randlevel * 3)

    yield from bot.say(pokemon + "'s Stats\nLevel: " + str(randlevel) + "\nHP: " + str(hlt) + "\nDexterity: " + str(dex) + "\nIntelligence: " + str(itl) + "\nStrength: " + str(sre) + "\nConstitution: " + str(con) + "\nWisdom: " + str(wis))
    #print(pokemon + "'s Stats\nLevel: " + str(randlevel) + "\nHP: " + str(hlt) + "\nDexterity: " + str(dex) + "\nIntelligence: " + str(itl) + "\nStrength: " + str(sre) + "\nConstitution: " + str(con) + "\nWisdom: " + str(wis) + "\nXP Earned: " + str(xpr) + "\n----------")

@bot.command()
@asyncio.coroutine
def timezone(time, frm, keyword, to):
    """Converts between timezones
    !timezone <time> <from-zone> to <to-zone>"""
    if not tz.is_timezone(frm) or not tz.is_timezone(to):
        yield from bot.say("I don't know that timezone... sorry...")
        return None
    res = tz.convert_formatted(time, frm, to)
    if res:
        hr, min = res
        cap = ''
        if hr < 0:
            cap = " on the previous day"
            hr += 24
        if hr > 24:
            cap = " on the following day"
            hr -= 24
        tzname = tz.timezone_name(to)
        yield from bot.say("In {}, that's {}:{:-02}{}!".format(tzname, int(hr), int(min), cap))
    else:
        yield from bot.say("Sorry... I didn't understand the time format...")

@bot.command(pass_context=True)
@asyncio.coroutine
def roll(ctx, die : str = None, name : discord.Member = None):
    """Rolls one or more dice"""

    if name==None:
        name = str(ctx.message.author.display_name)

    if die is None:
        die = "d6"
    try:
        res = dice.dice(die)
        if res == -1:
            yield from bot.say("Stahp!")
            print("{} exceeded the limit".format(name))
        elif res is None:
            yield from bot.say("Sorry, I don't understand that.")
            print(("{} made invalid command {}").format(name, die))
        else:
            final, data = res
            yield from bot.say("{} got {} (individual results: {})".format(name, final, data))
            #print("{} got {} (individual results: {})".format(name, final, data))
    except TypeError:
        yield from bot.say("I'm afraid that doesn't make sense...")
        traceback.print_exc()

"""
    if die is None:
        die = '6'

    if name==None:
        name = str(ctx.message.author.nick)

    if (name=="None"):
        name = '{0.name}'.format(ctx.message.author)

    dice = die.replace("d", "")
    rolldie = int(dice)

    rand = random.randint(1,rolldie)
    yield from bot.say(name + " rolled a D" + dice + "!\nIt's a " + str(rand))
    print(name + " rolled a D" + dice + "!\nIt's a " + str(rand) + "\n----------")
"""

@bot.command()
@asyncio.coroutine
def votes():
    """How good of a bot am I?"""
    if json_data['good'] > json_data['bad']:
        yield from bot.say("This bot is a good bot. Voted {} to {}.".format(json_data['good'], json_data['bad']))
    elif json_data['bad'] > json_data['good']:
        yield from bot.say("This bot is a bad bot. Voted {} to {}.".format(json_data['bad'], json_data['good']))
    else:
        yield from bot.say("This bot is an okay bot. Voted {} to {}.".format(json_data['good'], json_data['bad']))

@bot.command()
@asyncio.coroutine
def volunteer(role=None):
    """Randomly selects a player"""
    if role is not None:
        role = name_to_role(role)
    choices = zz.of(bot.get_all_members())
    if role:
        choices = choices.filter(lambda x: zz.of(x.roles).find(_1.id == role.id))
    choices = choices.list()
    member = random.choice(choices)
    yield from bot.say("I choose {}!".format(member.name))

@bot.command()
@asyncio.coroutine
def choose(vals, n='1'):
    """Chooses from a collection of elements.
    The values should be separated by a semicolon."""
    n = int(n)
    vals = vals.split(';')
    results = random.sample(vals, n)
    yield from bot.say("Drawing {} items: {}.".format(n, ', '.join(results)))

@bot.command()
@asyncio.coroutine
def ducksay(message):
    """Duck says what?"""
    MAX_LEN = 50
    data = message.split(' ')
    res = []
    curr = ""
    for val in data:
        new = curr + ' ' + val if curr else curr + val
        if len(new) >= MAX_LEN:
            res.append(curr)
            curr = ""
            new = curr + val
        curr = new
    if curr:
        res.append(curr)
    max_len = len(zz.of(res).max(len))
    if len(res) > 1:
        delim = zz.empty().chain(
            zz.of(["/\\"]),
            zz.repeat("||", n = len(res) - 2),
            zz.of(["\\/"])
        )
    else:
        delim = zz.repeat("<>")
    final = ''
    final += "```\n"
    final += " " + "_" * (max_len + 2) + " \n"
    for d, elem in zip(delim, res):
        elem += " " * (max_len - len(elem))
        final += d[0] + " " + elem + " " + d[1] + "\n"
    final += " " + "-" * (max_len + 2) + " \n"
    final += "  \\\n"
    final += "   \\\n"
    final += "    \\ >()_\n"
    final += "       (__)__ _\n"
    final += "```"
    yield from bot.say(final)

@asyncio.coroutine
def role_manage(ctx, role_name):
    # !role manage <rolename>
    author = ctx.message.author
    if not isinstance(author, discord.Member):
        return
    must_be_admin(author)
    role = name_to_role(role_name)
    if role:
        if role.id in role_data():
            yield from bot.say("I'm already managing that role.")
        else:
            role_data()[role.id] = {}
            role_data()[role.id]['name'] = role.name
            yield from bot.say("Okay, I'll manage {} now".format(role.name))
    else:
        yield from bot.say("I don't know of any role by that name.")

@asyncio.coroutine
def role_unmanage(ctx, role_name):
    # !role unmanage <rolename>
    author = ctx.message.author
    if not isinstance(author, discord.Member):
        return
    must_be_admin(author)
    role = name_to_role(role_name)
    if role and role.id in role_data():
        del role_data()[role.id]
        yield from bot.say("Okay, I'll forget about {}".format(role.name))
    else:
        yield from bot.say("I'm not managing any role by that name.")

@asyncio.coroutine
def role_owner(ctx, cmd, role_name, *args):
    # !role owner list <rolename>
    # !role owner add <rolename> <members>...
    # !role owner remove <rolename> <members>...
    author = ctx.message.author
    role = name_to_role(role_name)
    if (not role) or (role.id not in role_data()):
        yield from bot.say("I'm not managing any role by that name.")
        return
    # Anyone can use list
    if cmd == 'list':
        result = zz.of(owner_list(ctx.message.server, role)).map(_1.display_name).list()
        yield from bot.say("Members who own the role {}: {}".format(role.name, ', '.join(result)))
        return
    # Perms
    if (not is_owner_of_role(author, role)) and (not author.server_permissions.administrator):
        yield from bot.say("You don't have control over that role.")
        return
    # Make sure the owner list exists
    data = role_data()[role.id]
    if 'owners' not in data:
        data['owners'] = []
    # Add
    if cmd == "add":
        for arg in args:
            member = find_member(ctx.message.server, arg)
            if not member:
                yield from bot.say("I don't know a {}".format(arg))
            elif member.id in data['owners']:
                yield from bot.say("{} already owns {}".format(member.display_name, role.name))
            else:
                data['owners'].append(member.id)
                yield from bot.say("{} is now an owner of {}".format(member.display_name, role.name))
    elif cmd == "remove":
        for arg in args:
            member = find_member(ctx.message.server, arg)
            if not member:
                yield from bot.say("I don't know a {}".format(arg))
            elif member.id in data['owners']:
                data['owners'].remove(member.id)
                yield from bot.say("{} no longer owns {}".format(member.display_name, role.name))
            else:
                yield from bot.say("{} doesn't own {}".format(member.display_name, role.name))

@asyncio.coroutine
def role_voluntary(ctx, role_name):
    # !role voluntary <rolename>
    author = ctx.message.author
    role = name_to_role(role_name)
    if (not role) or (role.id not in role_data()):
        yield from bot.say("I'm not managing any role by that name.")
        return
    # Perms
    if (not is_owner_of_role(author, role)) and (not author.server_permissions.administrator):
        yield from bot.say("You don't have control over that role.")
        return
    if is_voluntary_role(role):
        yield from bot.say("{} is no longer a voluntary role".format(role.name))
        role_data()[role.id]['voluntary'] = False
    else:
        yield from bot.say("Members can now join and leave {} freely".format(role.name))
        role_data()[role.id]['voluntary'] = True

@asyncio.coroutine
def role_volunteer(ctx, role_name):
    # !role volunteer <rolename>
    author = ctx.message.author
    role = name_to_role(role_name)
    if (not role) or (role.id not in role_data()):
        yield from bot.say("I'm not managing any role by that name.")
        return
    if not is_voluntary_role(role):
        yield from bot.say("You can't volunteer for that role")
    elif role in author.roles:
        yield from bot.say("You already belong to that role")
    else:
        yield from bot.add_roles(author, role)
        yield from bot.say("You are now in {}, {}".format(role.name, author.display_name))

@asyncio.coroutine
def role_unvolunteer(ctx, role_name):
    # !role unvolunteer <rolename>
    author = ctx.message.author
    role = name_to_role(role_name)
    if (not role) or (role.id not in role_data()):
        yield from bot.say("I'm not managing any role by that name.")
        return
    if not is_voluntary_role(role):
        yield from bot.say("You can't unvolunteer for that role")
    elif role in author.roles:
        yield from bot.remove_roles(author, role)
        yield from bot.say("You are no longer {}, {}".format(role.name, author.display_name))
    else:
        yield from bot.say("You don't have that role")

@asyncio.coroutine
def role_add(ctx, role_name, *args):
    # !role add <rolename> <members>...
    author = ctx.message.author
    role = name_to_role(role_name)
    if (not role) or (role.id not in role_data()):
        yield from bot.say("I'm not managing any role by that name.")
        return
    # Perms
    if (not is_owner_of_role(author, role)) and (not author.server_permissions.administrator):
        yield from bot.say("You don't have control over that role.")
        return
    for arg in args:
        member = find_member(ctx.message.server, arg)
        if not member:
            yield from bot.say("I don't know a {}".format(arg))
        elif role in member.roles:
            yield from bot.say("{} already has {}".format(member.display_name, role.name))
        else:
            yield from bot.add_roles(member, role)
            yield from bot.say("{} now has {}".format(member.display_name, role.name))

@asyncio.coroutine
def role_remove(ctx, role_name, *args):
    # !role remove <rolename> <members>...
    author = ctx.message.author
    role = name_to_role(role_name)
    if (not role) or (role.id not in role_data()):
        yield from bot.say("I'm not managing any role by that name.")
        return
    # Perms
    if (not is_owner_of_role(author, role)) and (not author.server_permissions.administrator):
        yield from bot.say("You don't have control over that role.")
        return
    for arg in args:
        member = find_member(ctx.message.server, arg)
        if not member:
            yield from bot.say("I don't know a {}".format(arg))
        elif role in member.roles:
            yield from bot.remove_roles(member, role)
            yield from bot.say("{} no longer has {}".format(member.display_name, role.name))
        else:
            yield from bot.say("{} doesn't have {}".format(member.display_name, role.name))

@bot.command(pass_context=True)
@asyncio.coroutine
def role(ctx, cmd, *args):
    """Manages roles

    Anyone can use
    !role owner list <rolename>
    !role volunteer <rolename>
    !role unvolunteer <rolename>

    Admin / role owner only
    !role owner add <rolename> <members>...
    !role owner remove <rolename> <members>...
    !role voluntary <rolename>
    !role add <rolename> <members>...
    !role remove <rolename> <members>...

    Admin only
    !role manage <rolename>
    !role unmanage <rolename>"""
    if cmd == "manage":
        yield from role_manage(ctx, *args)
    elif cmd == "unmanage":
        yield from role_unmanage(ctx, *args)
    elif cmd == "owner":
        yield from role_owner(ctx, *args)
    elif cmd == "voluntary":
        yield from role_voluntary(ctx, *args)
    elif cmd == "volunteer":
        yield from role_volunteer(ctx, *args)
    elif cmd == "unvolunteer":
        yield from role_unvolunteer(ctx, *args)
    elif cmd == "add":
        yield from role_add(ctx, *args)
    elif cmd == "remove":
        yield from role_remove(ctx, *args)

@asyncio.coroutine
def send_image_of_grid(cfg, channel, filename="image.png"):
    image = cfg.make_grid()
    with BytesIO() as buffer:
        image.save(buffer, 'PNG')
        buffer.seek(0)
        yield from bot.send_file(channel, buffer, filename=filename)

@bot.command(pass_context=True)
@asyncio.coroutine
def grid(ctx, dims="3x3"):
    """Generates a grid.

    !grid NxM

    """
    n, m = map(int, re.findall(r"[0-9]+", dims))
    cfg = GridConfig(rows=n, cols=m)
    yield from send_image_of_grid(cfg, ctx.message.channel)

@bot.command(pass_context=True)
@asyncio.coroutine
def codenames(ctx, wordlist=None):
    """Generates a Codenames board.

    !codenames <wordlist>

    If provided, the wordlist should be a semicolon-separated list of
    words to include. The list must contain at least 25 elements but
    can contain more.

    """

    if wordlist is None:
        wordlist = DefaultWordList()
    else:
        wordlist = wordlist.split(';')
        if len(wordlist) < 25:
            yield from bot.say("Not enough words.")
            return
        wordlist = CustomWordList(wordlist)

    manager = CodenameManager(rows=5, cols=5, words=wordlist)
    cfg  = GridConfig(rows=5, cols=5, cells=manager)
    cfg1 = GridConfig(rows=5, cols=5, cells=manager.hidden())
    yield from send_image_of_grid(cfg , ctx.message.channel)
    yield from send_image_of_grid(cfg1, ctx.message.channel)

@bot.command(pass_context=True)
@asyncio.coroutine
def whois(ctx, name):
    """Identifies a member of this server.

    !whois <name>

    If I recognize the name of that person, I'll tell you who it
    is.

    """

    member = find_member(ctx.message.server, name)
    if member:
        embed = discord.Embed(title="", description="", color=0x000000)
        embed.add_field(name="Name", value=str(member), inline=True)
        embed.add_field(name="Display Name", value=member.display_name, inline=True)
        embed.add_field(name="Bot?", value=str(member.bot), inline=True)
        embed.set_thumbnail(url=member.avatar_url or member.default_avatar_url)
        yield from bot.say(embed=embed)
    else:
        yield from bot.say("I don't know a {}".format(name))

try:
    while True:
        try:
            with open('data.json') as f:
                json_data = json.load(f)
            bot.run(json_data['key'])
        except (aiohttp.errors.ClientResponseError,
                aiohttp.errors.ClientRequestError,
                aiohttp.errors.ClientOSError,
                aiohttp.errors.ClientDisconnectedError,
                aiohttp.errors.ClientTimeoutError,
                asyncio.TimeoutError,
                aiohttp.errors.HttpProcessingError) as e:
            print("Network failure:", type(e), e)
            time.sleep(1)
        finally:
           if json_data:
               with open('data.json', 'w') as f:
                   json.dump(json_data, f)
except Exception as e:
    print("Failure:", type(e), e)
