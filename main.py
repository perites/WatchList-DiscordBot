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

taem = classes.TypesAndRecordsManagers()
taem.set_types({
    classes.AnimeWatchListRecord.type: classes.AnimeWatchListRecord,
    classes.FilmWatchListRecord.type: classes.FilmWatchListRecord,
    classes.TvShowWatchListRecord.type: classes.TvShowWatchListRecord
})


@bot.command(name="show")
async def show(ctx):
    embed = discord.Embed(
        title='Watchlist',
        color=discord.Color.blue(),
    )

    for type, index_to_db_record in taem.indexes_to_db_records().items():
        record_type_class = taem.get_type(type)

        value = ""
        for index, db_record in index_to_db_record.items():
            value += f"{index}. {str(record_type_class(db_record))}"

        embed.add_field(name=f"{type}(s)", value=value, inline=False)

    await ctx.send(embed=embed)


@bot.command(name="add")
async def watchlist_add(ctx, type, information_url, *note):
    if requests.get(information_url).status_code != 200:
        raise Exception("Not a valid link")

    class_list_entity = taem.get_type(type)
    if not class_list_entity:
        raise Exception("Unsupported type")

    class_list_entity.validate_link(information_url)

    tools.add_to_watchlist(type=type, information_url=information_url, creator=ctx.author.name,
                           note=" ".join(note),
                           status="added", created_at=time.time())

    embed = tools.success_embed("Added to watchlist")
    await ctx.send(embed=embed)


@bot.command(name="watched")
async def watched(ctx, type, index):
    type_records = taem.indexes_to_db_records().get(type)
    if not type_records:
        raise Exception("No records with this type were found")

    db_record = type_records[int(index)]

    if not ctx.author.name == db_record.creator:
        raise Exception("Only creator can mark as watched")

    db_record.status = "watched"
    db_record.watched_at = time.time()
    db_record.save()

    embed = tools.success_embed("Marked as watched")
    await ctx.send(embed=embed)


#
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
