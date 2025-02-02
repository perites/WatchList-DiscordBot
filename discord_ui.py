import time

import discord
from discord.ui import View, Select

import tools


class RecordsOfTypeSelector(Select):
    def __init__(self, type_class, records):
        options = [discord.SelectOption(label=record.get_info().title, description=str(record).split(" - ")[1],
                                        value=record.db_id)
                   for record in records]

        super().__init__(placeholder=f"Choose a {type_class.name} to set status watched", min_values=1, max_values=1,
                         options=options)

        self.type_class = type_class

    async def callback(self, interaction: discord.Interaction):
        db_record_id = int(self.values[0])

        db_record = tools.get_db_record_by_id(db_record_id)
        if not interaction.user.name == db_record.creator:
            raise Exception("Only creator can mark as watched")

        db_record.status = "watched"
        db_record.watched_at = time.time()
        db_record.save()

        embed = tools.success_embed("Marked as watched")
        await interaction.response.send_message(embed=embed)


class MyView(View):
    def __init__(self, type_class, records_info):
        super().__init__()
        self.add_item(RecordsOfTypeSelector(type_class, records_info))
