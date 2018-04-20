#!/usr/bin/python3

import discord
from discord.ext import commands
from io import StringIO
import random
import asyncio
import re
import json
import dice
import traceback
import timezone as tz

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='!', description=description)

def good_bot(message):
    json_data['good'] += 1
    yield from bot.send_message(message.channel, "You have voted this bot as a good bot. :robot:")

def bad_bot(message):
    json_data['bad'] += 1
    yield from bot.send_message(message.channel, "You have voted this bot as a bad bot. :frowning2:")

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
    if (str(message.channel) == "general") or (str(message.channel) == "bot-testing-grounds"):
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
    yield from bot.change_presence(game=discord.Game(name=str(mygame)))

@bot.command()
@asyncio.coroutine
def genitem(*, item_name: str):
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
    if json_data['good'] > json_data['bad']:
        yield from bot.say("This bot is a good bot. Voted {} to {}.".format(json_data['good'], json_data['bad']))
    elif json_data['bad'] > json_data['good']:
        yield from bot.say("This bot is a bad bot. Voted {} to {}.".format(json_data['bad'], json_data['good']))
    else:
        yield from bot.say("This bot is an okay bot. Voted {} to {}.".format(json_data['good'], json_data['bad']))

@bot.command()
@asyncio.coroutine
def volunteer():
    choices = list(bot.get_all_members())
    member = random.choice(choices)
    yield from bot.say("I choose {}!".format(member.name))

@bot.command()
@asyncio.coroutine
def choose(vals, n='1'):
    n = int(n)
    vals = vals.split(';')
    results = random.sample(vals, n)
    yield from bot.say("Drawing {} items: {}.".format(n, ', '.join(results)))

try:
    with open('data.json') as f:
        json_data = json.load(f)
    bot.run(json_data['key'])
except Exception as e:
    print("Failure:", e)
finally:
    if json_data:
        with open('data.json', 'w') as f:
            json.dump(json_data, f)