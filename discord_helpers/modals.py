import discord.ui
from discord import Interaction

from discord_helpers import procedures
from services import authorization_code_service


class RegistrationModal(discord.ui.Modal, title="Registration codes"):

    guild_code = discord.ui.TextInput(label="Give the code from guild",
                                      placeholder="code")

    user_code = discord.ui.TextInput(label="Give the code from email.",
                                     placeholder="code")

    async def on_submit(self, interaction: Interaction):
        try:
            authorization_code_service.validate_codes(self.guild_code.value, self.user_code.value, interaction.user.id)
        except authorization_code_service.InvalidCode as exception:
            await interaction.response.send_message(f"Error occurred while validating codes: {exception}",
                                                    ephemeral=True)
            return
        await procedures.register_user(interaction)
