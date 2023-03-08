import json
import os

import discord
from discord import Client, Intents, Interaction
from discord.app_commands import CommandTree


class SecretManager:
    def __init__(self, file_name: str):
        with open(file_name, "r", encoding="utf-8") as secret_file:
            self._secrets: dict[str, str | int] = json.loads(secret_file.read())

    def get_secret(self, secret_name: str) -> str | int:
        secret = os.getenv(secret_name, None)
        if secret is None:
            secret = self._secrets[secret_name]
        return secret


secret_manager = SecretManager("dev_secrets.json")


class Bot(Client):
    def __init__(self, description: str, intents: Intents, guild: discord.Object):
        super().__init__(description=description, intents=intents)
        self.tree = CommandTree(self)
        self._guild = guild

    async def setup_hook(self):
        self.tree.copy_global_to(guild=self._guild)
        await self.tree.sync(guild=self._guild)


def setup_bot() -> Bot:
    guild = discord.Object(id=secret_manager.get_secret("GUILD_ID"))
    intents = discord.Intents.default()
    return Bot("Add description", intents, guild)


bot = setup_bot()


@bot.tree.command(name="ping")
async def ping(interaction: Interaction):
    await interaction.response.send_message("pong", ephemeral=True)


if __name__ == '__main__':
    bot.run(secret_manager.get_secret("BOT_TOKEN"))
