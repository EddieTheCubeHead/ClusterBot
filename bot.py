import json
import os

import discord
from discord import Client, Intents, Interaction
from discord.app_commands import CommandTree


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


if __name__ == '__main__':
    bot.run(get_secret("BOT_TOKEN"))
