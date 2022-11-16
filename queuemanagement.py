"""Functions that handle the queue managment"""

import time

import users
import constants

RS_more_role = "RS_more"
RS_role = "RS"

__QUEUES = {} # Dict of [RS_level][List of QueuedUser in the queue]
roles_id = {RS_more_role:{}, RS_role:{}} # Dict of dict of roles id
valid_channels_id = [] # List of monitored channels
rs_channels = {} # all rs channels

async def check_timeout(bot):
    '''Check if any user queue has timed out'''
    now = time.time()
    for rs_level in range(1, constants.MAX_RS):
        global __QUEUES
        current_queue = __QUEUES.get(rs_level, [])

        for user in current_queue[:]:
            if now >= user.queue_time + user.timeout:
                channel = bot.get_channel(rs_channels[rs_level])
                await channel.send(f'{user.user_name} removed from queue')
                current_queue.remove(user)

        __QUEUES[rs_level] = current_queue


async def parse_RS(message):
    '''Parse rs command message and call the corresponding function'''
    RS_level = _ParseRSLevel(message.content)
    if RS_level > 0 and RS_level <= constants.MAX_RS:
        await _add_user_to_queue(message, RS_level)
    else:
        return


async def parse_clear(message):
    '''Parse clear command message and call the corresponding function'''
    RS_level = _ParseRSLevel(message.content)
    if RS_level > 0 and RS_level <= constants.MAX_RS:
        await _ClearQueue(message, RS_level)
    else:
        return


async def parse_check(message):
    '''Parse check command message and call the corresponding function'''
    RS_level = _ParseRSLevel(message.content)
    if RS_level > 0 and RS_level <= constants.MAX_RS:
        await _CheckQueue(message, RS_level, False)
    else:
        return


async def remove_user(ctx):
    '''Remove user from all queues'''
    for rs_level in range(1, constants.MAX_RS):
        global __QUEUES
        current_queue = __QUEUES.get(rs_level, [])
        for user in current_queue[:]:
            if user.id == ctx.message.author.id:
                current_queue.remove(user)
                __QUEUES[rs_level] = current_queue
                await ctx.message.channel.send(
                    f'{ctx.message.author.name} removed from RS{rs_level} queue'
                )
    return

async def update_user_timeout(ctx, timeout: float):
    '''Update timeout for user in all queues'''
    anything_updated = False
    for rs_level in range(1, constants.MAX_RS):
        global __QUEUES
        current_queue = __QUEUES.get(rs_level, [])
        for user in current_queue:
            if user.id == ctx.message.author.id:
                user.timeout = timeout*60*60
                anything_updated = True
                __QUEUES[rs_level] = current_queue

    if anything_updated:
        await ctx.message.channel.send(f"Timeout updated to {timeout} hours in all queues")
    else:
        await ctx.message.channel.send("You are not in a queue")

QueueFunctions = {
    f'{constants.PREFIX}rs': parse_RS,
    f'{constants.PREFIX}clear': parse_clear,
    f'{constants.PREFIX}check': parse_check
}

async def _add_user_to_queue(message, rs_level: int):
    '''Add author of message to queue'''
    global __QUEUES
    current_queue = __QUEUES.get(rs_level, [])

    #Check if the user is in the queue
    for i in range(len(current_queue)):
        if current_queue[i].id == message.author.id:
            current_queue[i].queue_time = time.time()
            current_queue[i].timeout = constants.TIMEOUT
            await message.channel.send(f"Timer refreshed for RS{rs_level} for {message.author.name}")
            __QUEUES[rs_level] = current_queue
            await _CheckQueue(message, rs_level)
            return

    #User not in queue, just add it
    current_queue.append(users.QueuedUser(user_name=message.author.name, id=message.author.id, timeout=constants.TIMEOUT,  queue_time=time.time()))
    __QUEUES[rs_level] = current_queue

    if len(current_queue) < 3:
        await _CheckQueue(message, rs_level)
    elif len(current_queue) == 3:
        await message.channel.send(f'<@&{roles_id[RS_more_role][rs_level]}> 3/4 for RS{rs_level} queue')
    elif len(current_queue) == 4:
        message_to_send = f'Full team found for RS{rs_level} :'
        for user in current_queue:
            message_to_send += f' <@{user.id}>'
        __QUEUES.pop(rs_level, None)
        await message.channel.send(message_to_send)


async def _ClearQueue(message, rs_level: int):
    '''Clear a queue'''
    global __QUEUES
    __QUEUES.pop(rs_level, None)
    await message.channel.send(f'RS{rs_level} Queue cleared')


def _ParseRSLevel(content: str):
    '''Parse RS level from input string'''
    for command in QueueFunctions.keys():
        if content.startswith(command):
            RS_string = content[len(command):]
            if RS_string.isnumeric():
                return int(RS_string)
    return 0


async def _CheckQueue(message, RS_level: int, ping: bool = True):
    global __QUEUES
    current_queue = __QUEUES.get(RS_level, [])
    message_to_send = ""
    now = time.time()
    count = 0
    for user in current_queue:
        last_activity = int((now - user.queue_time) / 60)
        message_to_send += f" **{str(user.user_name)}** (*{last_activity} minutes*)"
        count += 1
    if len(message_to_send) == 0:
        message_to_send = "No user"
    await message.channel.send(message_to_send + ' in queue')
    if ping:
        await message.channel.send(f'<@&{roles_id[RS_role][RS_level]}> - {count}/4')
