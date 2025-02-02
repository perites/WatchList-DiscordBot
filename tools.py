import logging

import discord
import requests
from discord.ext import commands


def is_valid_url(url):
    try:
        if not requests.get(url).status_code == 200:
            raise Exception()

    except Exception as e:
        raise Exception("Not a valid link")


def success_embed(msg):
    embed = discord.Embed(
        title="Success",
        color=discord.Color.green(),
        description=msg,
    )
    return embed


def error_embed(msg):
    embed = discord.Embed(
        title="Error",
        color=discord.Color.red(),
        description=msg,
    )
    return embed


def process_error(author, error):
    logging.error(f"{error} - {author}")
    if isinstance(error, commands.CommandInvokeError):
        error_msg = error.original
    elif isinstance(error, commands.CommandNotFound) or isinstance(error, commands.CommandOnCooldown):
        return
    else:
        error_msg = error

    embed = error_embed(error_msg)

    return embed
