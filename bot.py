#!/usr/bin/python3.9

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
import traceback

from grid import CodenameManager, GridConfig, WordList, DefaultWordList, CustomWordList
from storage import JSONData
import dice
import error
import error_handler
import timezone as tz
import alakazam as zz
from alakazam import _1, _2, _3, _4, _5

from typing import Dict, Any, cast, List, Optional, Tuple, Union

Context = discord.ext.commands.Context

description = '''Hi, I'm Luckbot! I provide several useful utilities to the Discord
Games server.'''
bot = commands.Bot(command_prefix='!', description=description)

async def good_bot(message: discord.Message) -> None:
    json_data.good += 1
    await message.channel.send("You have voted this bot as a good bot. :robot:")

async def bad_bot(message: discord.Message) -> None:
    json_data.bad += 1
    await message.channel.send("You have voted this bot as a bad bot. :frowning2:")

def name_to_role(name: str) -> discord.Role:
    return zz.of(bot.guilds).map(_1.roles).flatten().find(_1.name == name)

# TODO Type this
def role_data() -> Any:
    return json_data['roles']

def is_admin(member: discord.abc.User) -> bool:
    if not isinstance(member, discord.Member):
        return False
    return member.guild_permissions.administrator

def must_be_admin(member: discord.abc.User) -> None:
    if not is_admin(member):
        raise error.PermissionsException()

def is_owner_of_role(member: Union[discord.Member, discord.User], role: discord.Role) -> bool:
    if role.id not in role_data():
        return False
    data = role_data()[role.id]
    if 'owners' not in data:
        return False
    return member.id in data['owners']

def is_voluntary_role(role: discord.Role) -> bool:
    if role.id not in role_data():
        return False
    data = role_data()[role.id]
    if 'voluntary' not in data:
        return False
    return data['voluntary']

def owner_list(server: discord.Guild, role: discord.Role) -> List[discord.Member]:
    if role.id not in role_data():
        return []
    data = role_data()[role.id]
    if 'owners' not in data:
        return []
    return zz.of(data['owners']).map(server.get_member).filter(_1).list()

def find_member(server: discord.Guild, name: str) -> Optional[discord.Member]:
    name = name.lower()
    def match(person: discord.Member) -> bool:
        return (person.name.lower() == name or person.display_name.lower() == name)
    return zz.of(server.members).find(match)

autoreplies = [
    (r"\bgood bot\b", good_bot),
    (r"\bgood morning\b", "Good morning! :sunrise:"),
    (r"\bgood afternoon\b", "Good afternoon! :sunny:"),
    (r"\bgood night\b", "Good night! :city_sunset:"),
    (r"\bbad bot\b", bad_bot)
]
# Note: This will be initialized before any code needs to access it,
# so assume it's not None anywhere that matters.
json_data: JSONData = cast(JSONData, None)

LINK_RE = re.compile("https?://|discord.gg/|discordapp.com/")

def contains_link(text: str) -> bool:
    return bool(re.search(LINK_RE, text))

async def log_message(text: str) -> None:
    channel = zz.of(bot.get_all_channels()).find(_1.name == "bot-logs")
    if channel:
        await channel.send(text)

async def spam_check(message: discord.Message) -> None:
    if message.author == bot.user:
        return
    if json_data.linky and contains_link(message.content):
        role = json_data.linky
        if isinstance(message.author, discord.Member):
            if role not in zz.of(message.author.roles).map(_1.id):
                await message.delete()
                await message.author.send("You don't have permission to post links. Feel free to ask an admin for this permission :)")
                await log_message("{} (in channel #{}) just tried to post the link: {}".format(message.author, message.channel, message.content))

@bot.event
async def on_message(message: discord.Message) -> None:
    if (message.author == bot.user):
        return
    # Spam checking for links
    await spam_check(message)
    # Autoreplies :)
    if (str(message.channel) == "general") or (str(message.channel) == "bot_testing-grounds"):
        for ptn, reply in autoreplies:
            if re.search(ptn, message.content, re.I):
                if callable(reply):
                    await reply(message)
                else:
                    await message.channel.send(reply)
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message) -> None:
    await spam_check(after)

@bot.event
async def on_command_error(ctx: Context, error: discord.ext.commands.CommandError) -> None:
    response = error_handler.appropriate_response(ctx, error)
    await response.perform(ctx)

@bot.event
async def on_ready() -> None:
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def playing(ctx: Context, *, mygame: str = ''):
    """Sets my presence tagline"""
    must_be_admin(ctx.author)
    game = discord.Game(name=mygame) if mygame != '' else None
    await bot.change_presence(activity=game)

'''
@bot.command()
async def genitem(ctx, *, item_name: str):
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
        await ctx.send(str(item_name) + "\n" + stat + ": " + str(stat_range))
        
    if (stat_range > 0):
        await ctx.send(str(item_name) + "\n" + stat + ": +" + str(stat_range))
        

@bot.command()
async def genchar(ctx, minlevel : int, maxlevel : int, pokemon : str):
    """Generates a character"""

    randlevel = random.randint(minlevel, maxlevel)
    dex = random.randint(-5, 5)
    itl = random.randint(-5, 5)
    sre = random.randint(-5, 5)
    con = random.randint(-5, 5)
    wis = random.randint(-5, 5)
    cha = random.randint(-5, 5)

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

    rarr = random.randint(randlevel, 100)
    if (rarr >= 80):
        cha += randlevel

    hlt = (4*randlevel) + con
    xpr = hlt - (randlevel * 3)

    await ctx.send(pokemon + "'s Stats\nLevel: " + str(randlevel) + "\nHP: " + str(hlt) + "\nDexterity: " + str(dex) + "\nIntelligence: " + str(itl) + "\nStrength: " + str(sre) + "\nConstitution: " + str(con) + "\nWisdom: " + str(wis) + "\nCharisma: " + str(cha))
'''

@bot.command()
async def timezone(ctx: Context, time: str, frm: str, keyword: str, to: str) -> None:
    """Converts between timezones
    !timezone <time> <from-zone> to <to-zone>"""
    if not tz.is_timezone(frm) or not tz.is_timezone(to):
        await ctx.send("I don't know that timezone... sorry...")
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
        await ctx.send("In {}, that's {}:{:-02}{}!".format(tzname, int(hr), int(min), cap))
    else:
        await ctx.send("Sorry... I didn't understand the time format...")

@bot.command()
async def roll(ctx: Context, die: str = None, name: Optional[discord.Member] = None) -> None:
    """Rolls one or more dice"""

    target_name: object = name or ctx.message.author

    if die is None:
        die = "d6"
    try:
        try:
            res = dice.dice(die)
            if res is None:
                await ctx.send("Sorry, I don't understand that.")
                print(("{} made invalid command {}").format(name, die))
            else:
                final, data = res
                await ctx.send("{} got {} (individual results: {})".format(name, final, data))
                #print("{} got {} (individual results: {})".format(name, final, data))
        except dice.TooManyDice:
            await ctx.send("Stahp!")
            print("{} exceeded the limit".format(name))
    except TypeError:
        await ctx.send("I'm afraid that doesn't make sense...")
        traceback.print_exc()

@bot.command()
async def votes(ctx: Context) -> None:
    """How good of a bot am I?"""
    if json_data['good'] > json_data['bad']:
        await ctx.send("This bot is a good bot. Voted {} to {}.".format(json_data['good'], json_data['bad']))
    elif json_data['bad'] > json_data['good']:
        await ctx.send("This bot is a bad bot. Voted {} to {}.".format(json_data['bad'], json_data['good']))
    else:
        await ctx.send("This bot is an okay bot. Voted {} to {}.".format(json_data['good'], json_data['bad']))

'''
@bot.command()
async def volunteer(ctx, role=None):
    """Randomly selects a player"""
    if role is not None:
        role = name_to_role(role)
    choices = zz.of(bot.get_all_members())
    if role:
        choices = choices.filter(lambda x: zz.of(x.roles).find(_1.id == role.id))
    choices = choices.list()
    member = random.choice(choices)
    await ctx.send("I choose {}!".format(member.name))
'''

@bot.command()
async def choose(ctx: Context, vals: str, n: int = 1) -> None:
    """Chooses from a collection of elements.
    The values should be separated by a semicolon."""
    vals1 = vals.split(';')
    results = random.sample(vals1, n)
    await ctx.send("Drawing {} items: {}.".format(n, ', '.join(results)))

@bot.command()
async def ducksay(ctx: Context, message: str) -> None:
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
    await ctx.send(final)

async def role_manage(ctx: Context, role_name: str) -> None:
    # !role manage <rolename>
    author = ctx.message.author
    if not isinstance(author, discord.Member):
        return
    must_be_admin(author)
    role = name_to_role(role_name)
    if role:
        if role.id in role_data():
            await ctx.send("I'm already managing that role.")
        else:
            role_data()[role.id] = {}
            role_data()[role.id]['name'] = role.name
            await ctx.send("Okay, I'll manage {} now".format(role.name))
    else:
        await ctx.send("I don't know of any role by that name.")

async def role_unmanage(ctx: Context, role_name: str) -> None:
    # !role unmanage <rolename>
    author = ctx.message.author
    if not isinstance(author, discord.Member):
        return
    must_be_admin(author)
    role = name_to_role(role_name)
    if role and role.id in role_data():
        del role_data()[role.id]
        await ctx.send("Okay, I'll forget about {}".format(role.name))
    else:
        await ctx.send("I'm not managing any role by that name.")

async def role_owner(ctx: Context, cmd: str, role_name: str, *args: str):
    # !role owner list <rolename>
    # !role owner add <rolename> <members>...
    # !role owner remove <rolename> <members>...
    author = ctx.message.author
    role = name_to_role(role_name)
    if (not role) or (role.id not in role_data()):
        await ctx.send("I'm not managing any role by that name.")
        return
    # Anyone can use list
    if cmd == 'list':
        if ctx.message.guild:
            result = zz.of(owner_list(ctx.message.guild, role)).map(_1.display_name).list()
        else:
            result = []
        await ctx.send("Members who own the role {}: {}".format(role.name, ', '.join(result)))
        return
    # Perms
    if (not is_owner_of_role(author, role)) and (not is_admin(author)):
        await ctx.send("You don't have control over that role.")
        return
    # Make sure the owner list exists
    data = role_data()[role.id]
    if 'owners' not in data:
        data['owners'] = []
    # Add
    if cmd == "add":
        for arg in args:
            member = ctx.message.guild and find_member(ctx.message.guild, arg)
            if not member:
                await ctx.send("I don't know a {}".format(arg))
            elif member.id in data['owners']:
                await ctx.send("{} already owns {}".format(member.display_name, role.name))
            else:
                data['owners'].append(member.id)
                await ctx.send("{} is now an owner of {}".format(member.display_name, role.name))
    elif cmd == "remove":
        for arg in args:
            member = ctx.message.guild and find_member(ctx.message.guild, arg)
            if not member:
                await ctx.send("I don't know a {}".format(arg))
            elif member.id in data['owners']:
                data['owners'].remove(member.id)
                await ctx.send("{} no longer owns {}".format(member.display_name, role.name))
            else:
                await ctx.send("{} doesn't own {}".format(member.display_name, role.name))

async def role_voluntary(ctx: Context, role_name: str) -> None:
    # !role voluntary <rolename>
    author = ctx.message.author
    role = name_to_role(role_name)
    if (not role) or (role.id not in role_data()):
        await ctx.send("I'm not managing any role by that name.")
        return
    # Perms
    if (not is_owner_of_role(author, role)) and (not is_admin(author)):
        await ctx.send("You don't have control over that role.")
        return
    if is_voluntary_role(role):
        await ctx.send("{} is no longer a voluntary role".format(role.name))
        role_data()[role.id]['voluntary'] = False
    else:
        await ctx.send("Members can now join and leave {} freely".format(role.name))
        role_data()[role.id]['voluntary'] = True

async def role_volunteer(ctx: Context, role_name: str) -> None:
    # !role volunteer <rolename>
    author = ctx.message.author
    role = name_to_role(role_name)
    if (not role) or (role.id not in role_data()):
        await ctx.send("I'm not managing any role by that name.")
        return
    if not is_voluntary_role(role):
        await ctx.send("You can't volunteer for that role")
    elif not isinstance(author, discord.Member):
        await ctx.send("Cannot manage roles in this channel")
    elif role in author.roles:
        await ctx.send("You already belong to that role")
    else:
        await author.add_roles(role)
        await ctx.send("You are now in {}, {}".format(role.name, author.display_name))

async def role_unvolunteer(ctx: Context, role_name: str) -> None:
    # !role unvolunteer <rolename>
    author = ctx.message.author
    role = name_to_role(role_name)
    if (not role) or (role.id not in role_data()):
        await ctx.send("I'm not managing any role by that name.")
        return
    if not is_voluntary_role(role):
        await ctx.send("You can't unvolunteer for that role")
    elif not isinstance(author, discord.Member):
        await ctx.send("Cannot manage roles in this channel")
    elif role in author.roles:
        await author.remove_roles(role)
        await ctx.send("You are no longer {}, {}".format(role.name, author.display_name))
    else:
        await ctx.send("You don't have that role")

async def role_add(ctx: Context, role_name: str, *args: str) -> None:
    # !role add <rolename> <members>...
    author = ctx.message.author
    role = name_to_role(role_name)
    if (not role) or (role.id not in role_data()):
        await ctx.send("I'm not managing any role by that name.")
        return
    # Perms
    if (not is_owner_of_role(author, role)) and (not is_admin(author)):
        await ctx.send("You don't have control over that role.")
        return
    for arg in args:
        member = ctx.message.guild and find_member(ctx.message.guild, arg)
        if not member:
            await ctx.send("I don't know a {}".format(arg))
        elif role in member.roles:
            await ctx.send("{} already has {}".format(member.display_name, role.name))
        else:
            await member.add_roles(role)
            await ctx.send("{} now has {}".format(member.display_name, role.name))

async def role_remove(ctx: Context, role_name: str, *args: str) -> None:
    # !role remove <rolename> <members>...
    author = ctx.message.author
    role = name_to_role(role_name)
    if (not role) or (role.id not in role_data()):
        await ctx.send("I'm not managing any role by that name.")
        return
    # Perms
    if (not is_owner_of_role(author, role)) and (not is_admin(author)):
        await ctx.send("You don't have control over that role.")
        return
    for arg in args:
        member = ctx.message.guild and find_member(ctx.message.guild, arg)
        if not member:
            await ctx.send("I don't know a {}".format(arg))
        elif role in member.roles:
            await member.remove_roles(role)
            await ctx.send("{} no longer has {}".format(member.display_name, role.name))
        else:
            await ctx.send("{} doesn't have {}".format(member.display_name, role.name))

'''
@bot.group(invoke_without_command=True)
async def example(ctx):
    await ctx.send_help(example)

@example.command()
async def foobar(ctx):
    await ctx.send("FOOBAR")
'''

@bot.command()
async def role(ctx: Context, cmd: str, *args: str) -> None:
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
        await role_manage(ctx, *args)
    elif cmd == "unmanage":
        await role_unmanage(ctx, *args)
    elif cmd == "owner":
        await role_owner(ctx, *args)
    elif cmd == "voluntary":
        await role_voluntary(ctx, *args)
    elif cmd == "volunteer":
        await role_volunteer(ctx, *args)
    elif cmd == "unvolunteer":
        await role_unvolunteer(ctx, *args)
    elif cmd == "add":
        await role_add(ctx, *args)
    elif cmd == "remove":
        await role_remove(ctx, *args)

async def send_image_of_grid(ctx: Context, cfg: GridConfig, filename: str = "image.png") -> None:
    image = cfg.make_grid()
    with BytesIO() as buffer:
        image.save(buffer, 'PNG')
        buffer.seek(0)
        f = discord.File(buffer, filename)
        await ctx.send(file=f)

@bot.command()
async def grid(ctx: Context, dims: str = "3x3") -> None:
    """Generates a grid.

    !grid NxM

    """
    n, m = map(int, re.findall(r"[0-9]+", dims))
    cfg = GridConfig(rows=n, cols=m)
    await send_image_of_grid(ctx, cfg)

@bot.command()
async def codenames(ctx: Context, words: Optional[str] = None) -> None:
    """Generates a Codenames board.

    !codenames <words>

    If provided, the word list should be a semicolon-separated list of
    words to include. The list must contain at least 25 elements but
    can contain more.

    """

    wordlist: WordList
    if words is None:
        wordlist = DefaultWordList()
    else:
        words1 = words.split(';')
        if len(words1) < 25:
            await ctx.send("Not enough words.")
            return
        wordlist = CustomWordList(words1)

    manager = CodenameManager(rows=5, cols=5, words=wordlist)
    cfg  = GridConfig(rows=5, cols=5, cells=manager)
    cfg1 = GridConfig(rows=5, cols=5, cells=manager.hidden())
    await send_image_of_grid(ctx, cfg )
    await send_image_of_grid(ctx, cfg1)

'''
@bot.command()
async def whois(ctx, name):
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
        await ctx.send(embed=embed)
    else:
        await ctx.send("I don't know a {}".format(name))
'''

'''
@bot.command()
async def assignlinkrole(ctx, role_name):
    """Determines the role used for spam-checking against links.

    !assignlinkrole <role_name>

    (admin only)

    """
    role = name_to_role(role_name)
    if not ctx.message.author.server_permissions.administrator:
        await ctx.send("You don't have permission to do that")
    elif role_name == "":
        await ctx.send("I'll no longer mess with links")
        del json_data['linky']
    elif not role:
        await ctx.send("I don't know that role")
    else:
        await ctx.send("I'll make sure this server stays spam-free!")
        json_data['linky'] = role.id
'''

try:
    while True:
        try:
            with open('data.json') as f:
                json_data = JSONData(json.load(f))
            bot.run(json_data['key'])
        except (aiohttp.ClientError,
                aiohttp.ClientOSError,
                TimeoutError,
                asyncio.TimeoutError) as e:
            print("Network failure:", type(e), e)
            time.sleep(1)
        finally:
           if json_data:
               with open('data.json', 'w') as f:
                   json.dump(json_data.data, f)
except Exception as e:
    print("Failure:", type(e), e)
    traceback.print_exc()
