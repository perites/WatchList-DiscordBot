# TODO add logging to channel for critical errors
# TODO add dropdown type menu
# TODO add ability to schedule using discrod events
# TODO add command for random record, random record of type
# todo add caching fot mal and wikipage objects

import logging
import sys
import time

import discord
from discord.ext import commands

import classes
import config
import discord_ui
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

taem = classes.TypesAndRecordsManagers()
taem.set_types([classes.AnimeWatchListRecord, classes.FilmWatchListRecord, classes.TvShowWatchListRecord])


@bot.command(name="show")
async def show(ctx):
    embed = discord.Embed(
        title='Watchlist',
        color=discord.Color.blue(),
    )

    for type_class in taem.types:
        db_records_of_type = taem.get_db_records_of_type(type_class.name)
        if not db_records_of_type:
            continue

        value = ""
        for index, db_record in enumerate(db_records_of_type):
            value += f"{index}. {str(taem.db_record_to_record(type_class, db_record))}"

        embed.add_field(name=f"{type_class.name}(s)", value=value, inline=False)

    await ctx.send(embed=embed)


@bot.command(name="add")
async def watchlist_add(ctx, type, information_url, *note):
    tools.is_valid_url(information_url)

    class_list_entity = taem.get_type(type)

    information_url = class_list_entity.validate_link(information_url)

    tools.add_to_watchlist(type=type, information_url=information_url, creator=ctx.author.name,
                           note=" ".join(note),
                           status="added", created_at=time.time())

    embed = tools.success_embed("Added to watchlist")
    await ctx.send(embed=embed)


@bot.command(name="watched")
async def watched(ctx, type_name):
    type_class = taem.get_type(type_name)
    records = []
    for db_record in taem.get_db_records_of_type(type_name):
        records.append(taem.db_record_to_record(type_class, db_record))

    await ctx.send(f"Choose a {type_name} to set status watched:", view=discord_ui.MyView(type_class, records))


# @bot.command()
# # @has_role(roles_for_clean)
# async def clean(ctx, limit):
#     limit = int(limit)
#     await ctx.channel.purge(limit=int(limit) + 1)


# @bot.event
# async def on_command_error(ctx, error):
#     logging.error(f"{error} - {ctx.author}")
#     if isinstance(error, commands.CommandInvokeError):
#         embed = tools.error_embed(error.original)
#     elif isinstance(error, commands.CommandNotFound):
#         return
#     else:
#         embed = tools.error_embed(error)
#
#     await ctx.send(embed=embed)


if __name__ == '__main__':
    bot.run(secrets.BOT_TOKEN, log_handler=None, root_logger=True)
