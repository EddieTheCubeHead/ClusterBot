from discord import Interaction

from db.repositories import user_repository


async def register_user(interaction: Interaction):
    user_repository.add_registered(interaction.user.id)
    await interaction.response.send_message("Registration successful", ephemeral=True)
