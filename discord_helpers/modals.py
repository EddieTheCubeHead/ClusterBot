import datetime

import discord.ui
from discord import Interaction

from db.repositories.ballot_repository import add_vote, Ballot
from discord_helpers import procedures
from services import authorization_code_service


class RegistrationModal(discord.ui.Modal, title="Registration codes"):

    def __init__(self, email: str):
        super().__init__()
        self._email = email

    guild_code = discord.ui.TextInput(label="Give the code from guild", placeholder="code")

    user_code = discord.ui.TextInput(label="Give the code from email.", placeholder="code")

    async def on_submit(self, interaction: Interaction):
        try:
            authorization_code_service.validate_codes(self.guild_code.value, self.user_code.value, interaction.user.id)
        except authorization_code_service.InvalidCode as exception:
            await interaction.response.send_message(f"Error occurred while validating codes: {exception}",
                                                    ephemeral=True)
            return
        await procedures.register_user(interaction, self._email)


class BallotAddOptionModal(discord.ui.Modal, title="Add ballot options"):

    def __init__(self, closes_at: datetime.datetime, name: str, description: str, options: int = 2):
        super().__init__()
        self._closes_at = closes_at
        self._name = name
        self._description = description
        for option_num in range(1, options + 1):
            self.add_item(discord.ui.TextInput(label=f"Option #{option_num}", placeholder="option"))

    async def on_submit(self, interaction: Interaction):
        options = [item.value for item in self.children]
        _validate_options(options)
        await procedures.create_ballot_message(interaction, self._name, self._description, self._closes_at, options)


def _validate_options(options: list[str]):
    if len(options) != len(set(options)):
        # TODO: replace with proper error handling as a part of issue #9
        raise Exception("Cannot give multiple identical options!")
