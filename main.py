# TODO add logging to channel for critical errors
# TODO add dropdown type_name menu
# TODO add ability to schedule using discrod events

import logging
import sys
import time

import discord
from discord.ext import commands

import classes
import config
import discord_ui
import my_secrets
import tools

bot = commands.Bot(command_prefix=f"{config.prefix}", activity=discord.Game(name=f'{config.prefix} help'),
                   intents=discord.Intents.all())
bot.remove_command('help')
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


@bot.command(name="help")
@commands.cooldown(1, 60, commands.BucketType.user)
async def help(ctx):
    msg = '''Користування вотчлістом відбувається через команду !wl

type_name : film / anime / tv-show 

Команди бота:
- !wl add <type_name> <link> | додає запис в вотчліст
Для кожного type_name в команді add потрібно своє посилання:
film - посилання на вікіпедію з фільмом
anime - посилання на myanimelist з аніме
tv-show - посилання на вікіпедію з серіалом

- !wl show | показує наявні записи в вотчлісті

- !wl watched <type_name> | відмічає запис як продивлений і видаляє з вотчліста

- !wl random | видає випадковий запис з усіх наявних записів

- !wl random <type_name> | видає випадковий запис певного типу


Вотчліст знаходиться в тестувальному режимі, тому якщо викникнуть якісь ідеї попіпшення / знайдете якісь баги пишіть мені (@perite)
І нагадую що користування всіма ботами відбувається в каналі #бот для зручності 
'''
    embed = discord.Embed(
        title='Watchlist Help',
        color=discord.Color.dark_grey(),
        description=msg
    )
    await ctx.send(embed=embed)


@bot.command(name="show")
@commands.cooldown(6, 60, commands.BucketType.user)
async def show(ctx):
    embed = discord.Embed(
        title='Watchlist',
        color=discord.Color.blue(),
    )

    for type_class in taem.types:
        db_records_of_type = taem.get_db_records_of_type(type_class.type_name)
        if not db_records_of_type:
            continue

        value = ""
        for index, db_record in enumerate(db_records_of_type):

            record = taem.db_record_to_record(type_class, db_record)
            if not record:
                continue

            value += f"{index}. {str(record)}"

        embed.add_field(name=f"{type_class.type_name}(s)", value=value, inline=False)

    await ctx.send(embed=embed)


@bot.command(name="random")
@commands.cooldown(10, 60, commands.BucketType.user)
async def random(ctx, type_name=None):
    db_record = taem.get_random_db_record(type_name)
    record = taem.db_record_to_record(taem.get_type(db_record.type_name), db_record)

    embed = discord.Embed(
        title=f'Random {record.type_name}',
        color=discord.Color.blue(),
        description=str(record)
    )

    await ctx.send(embed=embed)


@bot.command(name="add")
@commands.cooldown(2, 60, commands.BucketType.user)
async def watchlist_add(ctx, type, information_url, *note):
    tools.is_valid_url(information_url)

    class_list_entity = taem.get_type(type)

    information_url = class_list_entity.validate_link(information_url)

    taem.add_to_watchlist(type_name=type, information_url=information_url, creator=ctx.author.name,
                          note=" ".join(note),
                          status="added", created_at=time.time())

    embed = tools.success_embed("Added to watchlist")
    await ctx.send(embed=embed)


@bot.command(name="watched")
@commands.cooldown(2, 60, commands.BucketType.user)
async def watched(ctx, type_name):
    type_class = taem.get_type(type_name)
    records = []
    for db_record in taem.get_db_records_of_type(type_name):
        record = taem.db_record_to_record(type_class, db_record)
        if not record:
            continue
        records.append(record)

    await ctx.send(f"Choose a {type_name} to set status watched:", view=discord_ui.RecordsOfTypeSelectorView(records))


@bot.command()
async def clean(ctx, limit):
    if str(ctx.author.id) != "513071445790949386":
        await ctx.send(embed=tools.error_embed("Not allowed"))
        return
    limit = int(limit)
    await ctx.channel.purge(limit=int(limit) + 1)


@bot.event
async def on_command_error(ctx, error):
    embed = tools.process_error(ctx.author.name, error)
    if not embed:
        return
    await ctx.send(embed=embed)


if __name__ == '__main__':
    bot.run(my_secrets.BOT_TOKEN, log_handler=None, root_logger=True)
