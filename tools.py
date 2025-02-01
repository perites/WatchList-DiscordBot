import logging

import discord

import models


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


def add_to_watchlist(**information):
    try:
        models.WatchListRecord.create(**information)
    except Exception as e:
        logging.critical(f"Error during saving to DB : {e}")
        raise Exception(f"Could not save to DB for some reason.\n\nTechnical error : {e}")
