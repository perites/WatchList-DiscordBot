import time

import discord
from discord.ui import View, Select

import tools


class RecordsOfTypeSelector(Select):
    def __init__(self, records):
        options = [discord.SelectOption(label=record.get_info().title, description=str(record).split(" - ")[1],
                                        value=record.db_id)
                   for record in records]

        super().__init__(placeholder=f"Choose a {records[0].type_name} to set status watched", min_values=1,
                         max_values=1,
                         options=options)

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


class RecordsOfTypeSelectorView(View):
    def __init__(self, records_info):
        super().__init__()
        self.add_item(RecordsOfTypeSelector(records_info))

    async def on_error(self, interaction: discord.Interaction, error: Exception, item):
        embed = tools.process_error(interaction.user.name, error)
        if not embed:
            return
        await interaction.response.send_message(embed=embed)
