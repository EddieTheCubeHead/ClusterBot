from discord import Interaction

from db.repositories import user_repository, role_repository


async def register_user(interaction: Interaction):
    user_repository.add_registered(interaction.user.id)
    role = interaction.guild.get_role(role_repository.get_role_id("Jäsen"))
    await interaction.user.add_roles(role)
    await interaction.response.send_message("Registration successful", ephemeral=True)
