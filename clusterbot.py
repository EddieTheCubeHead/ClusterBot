import datetime
import json
import os
import time

import discord
from discord import Client, Intents, Permissions, Interaction, app_commands
from discord.app_commands import CommandTree, default_permissions, autocomplete
from discord.ext import tasks

from db.repositories import user_repository
from discord_helpers import modals, roles
from discord_helpers.autocompletes import autocomplete_student_email
from migration_engine import on_deploy
from services import authorization_code_service, email_service


def get_secret(secret_name: str) -> str | int:
    secret = os.getenv(secret_name, None)
    if secret is None:
        with open("dev_secrets.json", "r", encoding="utf-8") as secret_file:
            secret = json.loads(secret_file.read())[secret_name]
    return secret


class ClusterBot(Client):
    def __init__(self, description: str, intents: Intents, guild: discord.Object):
        super().__init__(description=description, intents=intents)
        self.tree = CommandTree(self)
        self._guild = guild

    async def setup_hook(self):
        self.tree.copy_global_to(guild=self._guild)
        await self.tree.sync(guild=self._guild)


def setup_bot() -> ClusterBot:
    guild = discord.Object(id=get_secret("GUILD_ID"))
    intents = discord.Intents.default()
    intents.members = True
    return ClusterBot("Add description", intents, guild)


bot = setup_bot()
email_client = email_service.EmailService(get_secret("EMAIL_PASSWORD"))

moderator_permissions = Permissions.none().moderate_members = True
admin_permissions = Permissions.all()


@bot.event
async def on_ready():
    print("Connected")
    await roles.ensure_roles(await bot.fetch_guild(get_secret("GUILD_ID")))


@bot.tree.command(name="ping")
async def ping(interaction: Interaction):
    await interaction.response.send_message("pong", ephemeral=True)


@bot.tree.command(name="generate-guild-code")
@default_permissions(moderate_members=True)
async def generate_guild_authorization_code(interaction: Interaction):
    user_repository.ensure_exists(interaction.user.id)
    code = authorization_code_service.generate_guild_code(interaction.user.id)
    await interaction.response.send_message(f"Code: `{code.code}`\n\nExpires at {code.expires_at}", ephemeral=True)


@bot.tree.command(name="register-as-member")
@autocomplete(email=autocomplete_student_email)
async def register_as_member(interaction: Interaction, email: str):
    if user_repository.is_verified(interaction.user.id, datetime.timedelta(days=200)):
        await interaction.response.send_message("Already verified", ephemeral=True)
        return
    if not email_service.validate_student_email(email):
        await interaction.response.send_message(f"Only '@student.lut.fi'-emails are supported.", ephemeral=True)
        return
    code = authorization_code_service.generate_user_code(interaction.user.id)
    email_client.send_email(email, f"Subject: Cluster discord registration code\n\n{code.code}")
    await interaction.response.send_modal(modals.RegistrationModal())


@default_permissions(administrator=True)
class AutoKick(discord.app_commands.Group):

    @app_commands.command()
    async def start(self, interaction: Interaction):
        kick_unregistered.start()
        await interaction.response.send_message("Now auto-kicking unregistered users", ephemeral=True)

    @app_commands.command()
    async def stop(self, interaction: Interaction):
        kick_unregistered.stop()
        await interaction.response.send_message("No longer auto-kicking unregistered users", ephemeral=True)

    @app_commands.command()
    async def restart(self, interaction: Interaction):
        kick_unregistered.restart()
        await interaction.response.send_message("Restarted the auto-kicking of unregistered users", ephemeral=True)


bot.tree.add_command(AutoKick())


@tasks.loop(minutes=10)
async def kick_unregistered():
    async for member in bot.get_guild(get_secret("GUILD_ID")).fetch_members():
        if (not user_repository.is_verified(member.id)
                and not member.bot
                and member.joined_at + datetime.timedelta(days=1) < datetime.datetime.now(datetime.timezone.utc)):
            await member.kick(reason="Not registered as a guild member")
            print(f"Kicked {member.name}")
        else:
            print(f"Did not kick {member.name}")


if __name__ == '__main__':
    on_deploy()
    bot.run(get_secret("BOT_TOKEN"))
