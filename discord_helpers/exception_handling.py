from logging import getLogger

from discord import Interaction
from discord.app_commands import CommandTree, AppCommandError
from discord.ui import Modal, Button, View, Item

from discord_helpers.embeds import from_exception_message

_logger = getLogger("bot.exception")


class BotException(AppCommandError):

    async def handle(self, interaction: Interaction):
        pass



class UserException(BotException):

    async def handle(self, interaction: Interaction):
        _logger.error(str(self))
        embed = from_exception_message(str(self))
        await interaction.response.send_message(embed=embed, ephemeral=True)


class InternalException(BotException):

    async def handle(self, interaction: Interaction):
        _logger.error(str(self))
        embed = from_exception_message("Something went wrong internally. Exception has been logged.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ExceptionCatcherCommandTree(CommandTree):

    async def on_error(self, interaction: Interaction, error: AppCommandError):
        if isinstance(error, BotException):
            await error.handle(interaction)
        else:
            await super().on_error(interaction, error)


class ExceptionCatcherModal(Modal):

    async def on_error(self, interaction: Interaction, error: AppCommandError):
        if isinstance(error, BotException):
            await error.handle(interaction)
        else:
            await super().on_error(interaction, error)


class ExceptionCatcherView(View):

    async def on_error(self, interaction: Interaction, error: AppCommandError, item: Item):
        if isinstance(error, BotException):
            await error.handle(interaction)
        else:
            await super().on_error(interaction, error)
