import logging

import discord
import requests

import models


def is_valid_url(url):
    try:
        requests.get(url)
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


def add_to_watchlist(**information):
    try:
        models.WatchListRecord.create(**information)
    except Exception as e:
        logging.critical(f"Error during saving to DB : {e}")
        raise Exception(f"Could not save to DB for some reason.\n\nTechnical error : {e}")


def get_db_record_by_id(id):
    record = models.WatchListRecord.get_or_none(models.WatchListRecord.id == id)
    if not record:
        raise Exception(f"Record with id {id} does not exists")

    return record
