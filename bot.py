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
from storage import json_data, JSONData, RoleData
from permission import is_admin, must_be_admin
from util import find_member, OptionalChecked, Context
import dice
import cog
import error
import error_handler
import timezone as tz
import alakazam as zz
from alakazam import _1, _2, _3, _4, _5

from typing import Dict, Any, cast, List, Optional, Tuple, Union

description = '''Hi, I'm Luckbot! I provide several useful utilities to the Discord
Games server.'''

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', description=description, intents=intents)
cog.add_cogs(bot)

@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user:
        return
    await bot.process_commands(message)

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

try:
    while True:
        try:
            with open('data.json') as f:
                json_data.data = json.load(f)
            bot.run(json_data.key)
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
