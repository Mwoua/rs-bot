import discord
from discord.ext import commands, tasks

import os
import re

import constants
import queuemanagement

# dotenv
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Init intents with minimal needs
required_intents = intents = discord.Intents.none()
required_intents.messages = True
required_intents.message_content = True
required_intents.guilds = True

bot = commands.Bot(command_prefix=constants.PREFIX, intents=required_intents, help_command=None)

import sys # TODO use logging instead of writing to stderr

# on bot connection - build role id list
@bot.event
async def on_ready():
    '''Bot started up - Fetch usefull data and start task loop'''
    guild_id = int(os.getenv('ServerId'))
    guild = bot.get_guild(guild_id)

    roles = guild.roles
    for role in roles:
        match_result_more = re.match("^RS(\d+)\s+-\s+Need", role.name)
        if (match_result_more) and int(match_result_more.group(1)) > 0 and int(match_result_more.group(1)) < constants.MAX_RS:
            queuemanagement.roles_id[queuemanagement.RS_more_role][int(match_result_more.group(1))] = role.id

        match_result_RS = re.match("^RS(\d+)$", role.name)
        if (match_result_RS) and int(match_result_RS.group(1)) > 0 and int(match_result_RS.group(1)) < constants.MAX_RS:
            queuemanagement.roles_id[queuemanagement.RS_role][int(match_result_RS.group(1))] = role.id

    for channel in guild.channels:
        match_rs_chan = re.match("^rs(\d+)$", channel.name)
        if channel.name.startswith('bot') or match_rs_chan:
            queuemanagement.valid_channels_id.append(channel.id)

        if match_rs_chan:
            queuemanagement.rs_channels[int(match_rs_chan.group(1))] = channel.id

    sys.stderr.write('Bot started on server: ' + guild.name + '\n')
    task_loop.start()


# To avoid repetition of command for all rs level, we do a first check here,
#  and forward to bot command if necessary
@bot.event
async def on_message(message):
    '''Parse received message'''
    if message.author == bot.user or not message.content.startswith(constants.PREFIX) or not message.channel.id in queuemanagement.valid_channels_id:
        return

    for command, function in queuemanagement.QueueFunctions.items():
        if message.content.startswith(command):
            await function(message)
            return

    await bot.process_commands(message)


# commands that dont depends on rs level
@bot.command()
async def out(ctx):
    '''out command'''
    await queuemanagement.remove_user(ctx)


@bot.command()
async def timeout(ctx, timeout: float):
    '''timeout command'''
    await queuemanagement.update_user_timeout(ctx, timeout)


@bot.command()
async def help(ctx):
    '''help command'''
    message = 'Red star bot commands:\n'
    message += 'help: display this message\n'
    message += 'clearx: empty the queue for red star level x\n'
    message += 'rsx: queue user for red star level x queue\n'
    message += 'out: remove user from all queues\n'
    message += 'timeout X: change all your queues timeout, with X a time in hour\n'
    await ctx.message.channel.send(message)

@bot.event
async def on_command_error(ctx, command):
    pass

# Loop to check timeout
@tasks.loop(seconds=300)
async def task_loop():
    '''loop to check user timeout'''
    await queuemanagement.check_timeout(bot)


bot.run(os.getenv('TOKEN'))
