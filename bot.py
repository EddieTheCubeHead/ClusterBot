import json
import os

import discord
from discord import Client, Intents, Interaction
from discord.app_commands import CommandTree

from migration_engine import on_deploy, get_latest_migrated


def get_secret(secret_name: str) -> str | int:
    secret = os.getenv(secret_name, None)
    if secret is None:
        with open("dev_secrets.json", "r", encoding="utf-8") as secret_file:
            secret = json.loads(secret_file.read())[secret_name]
    return secret


class Bot(Client):
    def __init__(self, description: str, intents: Intents, guild: discord.Object):
        super().__init__(description=description, intents=intents)
        self.tree = CommandTree(self)
        self._guild = guild

    async def setup_hook(self):
        self.tree.copy_global_to(guild=self._guild)
        await self.tree.sync(guild=self._guild)


def setup_bot() -> Bot:
    guild = discord.Object(id=get_secret("GUILD_ID"))
    intents = discord.Intents.default()
    return Bot("Add description", intents, guild)


bot = setup_bot()


@bot.tree.command(name="ping")
async def ping(interaction: Interaction):
    await interaction.response.send_message("pong", ephemeral=True)


@bot.tree.command(name="test")
async def test(interaction: Interaction):
    await interaction.response.send_message(f"Latest migrated is {get_latest_migrated()}", ephemeral=True)


if __name__ == '__main__':
    on_deploy()
    bot.run(get_secret("BOT_TOKEN"))
