import discord

import classes
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


def entities_to_embed(entities_of_types):
    embed = discord.Embed(
        title='Watchlist',
        color=discord.Color.blue(),
    )

    for entities_of_type in entities_of_types:

        if not entities_of_type:
            continue

        value = ""
        for index, entity in enumerate(entities_of_type):
            entity_info = entity.get_info()

            value += f"{index + 1}. [{entity_info.title}]({entity_info.link}) - added by {entity_info.creator} on {entity_info.created_at:%B %#d}" + (
                f" with note: {entity_info.note}" if entity_info.note else "") + "\n"

        type = entities_of_type[0].type
        embed.add_field(name=f"{type}(s)", value=value, inline=False)

    return embed


def get_records_by_types():
    records_by_types = []
    for type in classes.type_to_list_entity.keys():
        records_by_types.append(
            list(models.WatchListEntity.select().where(models.WatchListEntity.type == type).order_by(
                models.WatchListEntity.created_at)))

    return records_by_types
