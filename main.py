# TODO add logging to channel for critical errors

import logging
import sys
import time

import discord
import requests
from discord.ext import commands

import classes
import config
import secrets
import tools

bot = commands.Bot(command_prefix=f"{config.prefix}", activity=discord.Game(name=f'{config.prefix} help'),
                   intents=discord.Intents.all())

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] : %(message)s  ||[LOGGER:%(name)s] [FUNC:%(funcName)s] [FILE:%(filename)s]',
    datefmt='%H:%M:%S:%MS',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('main-log', mode='w', encoding='utf-8', )
    ]
)


@bot.command(name="show")
async def watchlist(ctx):
    entities_of_types = []
    records_by_types = tools.get_records_by_types()
    for records_by_type in records_by_types:
        entities_of_type = [
            classes.type_to_list_entity[record.type].entity_from_record(record) for record in records_by_type]

        entities_of_types.append(entities_of_type)

    embed = tools.entities_to_embed(entities_of_types)

    await ctx.send(embed=embed)


@bot.command(name="add")
async def watchlist_add(ctx, type=None, info_link=None, *note):
    if (not info_link) or (not type):
        raise Exception("Missing link or type")

    class_list_entity = classes.type_to_list_entity.get(type)
    if not class_list_entity:
        raise Exception("Unsupported type")

    if requests.get(info_link).status_code != 200:
        raise Exception("Not a valid link")

    list_entity = class_list_entity(info_link, time.time(), ctx.author.name, " ".join(note))
    list_entity.validate()
    list_entity.add_to_watchlist()

    embed = tools.success_embed("Added to watchlist")
    await ctx.send(embed=embed)


@bot.command(name="watched")
async def watched(ctx, ):
    pass


@bot.command()
# @has_role(roles_for_clean)
async def clean(ctx, limit):
    limit = int(limit)
    await ctx.channel.purge(limit=int(limit) + 1)


# @bot.event
# async def on_command_error(ctx, error):
#     logging.error(f"{error} - {ctx.author}")
#     embed = tools.error_embed(error.original)
#     await ctx.send(embed=embed)


if __name__ == '__main__':
    bot.run(secrets.BOT_TOKEN, log_handler=None, root_logger=True)
