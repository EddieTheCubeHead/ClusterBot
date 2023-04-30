import datetime
from logging import getLogger

import discord
from discord import Client, Intents, Permissions, Interaction, app_commands
from discord.app_commands import CommandTree, default_permissions, autocomplete, Range
from discord.ext import tasks

from configuration.configuration_service import get_secret
from db.repositories import user_repository
from db.repositories.ballot_repository import get_vote_hash, get_ballot_hashes
from discord_helpers import roles
from discord_helpers.autocompletes import autocomplete_student_email, autocomplete_ballot_id
from discord_helpers.embeds import from_ballot_hashes
from discord_helpers.modals import RegistrationModal, BallotAddOptionModal
from discord_helpers.procedures import kick_unregistered, close_ballots
from migration_engine import on_deploy
from services import authorization_code_service, email_service
from services.logging_service import setup_logging


_logger = None


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
    _logger.info("Connected")
    await roles.ensure_roles(await bot.fetch_guild(get_secret("GUILD_ID")))
    close_ballots_loop.start()


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
    await interaction.response.send_modal(RegistrationModal(email))


@bot.tree.command()
async def ballot(interaction: Interaction, name: str, description: str, hours: int, minutes: Range[int, 0, 60],
                 option_count: Range[int, 2, 25]):
    now_utc = datetime.datetime.now().astimezone(datetime.timezone.utc)
    end_timestamp = (now_utc + datetime.timedelta(hours=hours, minutes=minutes))
    await interaction.response.send_modal(BallotAddOptionModal(end_timestamp, name, description, option_count))


@bot.tree.command(name="check-vote")
@autocomplete(ballot_id=autocomplete_ballot_id)
async def check_vote(interaction: Interaction, ballot_id: str):
    ballot_id = int(ballot_id)
    vote_hash = get_vote_hash(ballot_id, interaction.user.id)
    if vote_hash:
        await interaction.response.send_message(f"The hash of your vote for this ballot is '{vote_hash}'.",
                                                ephemeral=True, delete_after=120)
    else:
        await interaction.response.send_message("It appears you haven't voted in this ballot.", ephemeral=True,
                                                delete_after=60)


@bot.tree.command(name="try-hash")
@autocomplete(ballot_id=autocomplete_ballot_id)
async def try_hash(interaction: Interaction, ballot_id: str, salt: str):
    ballot_id = int(ballot_id)
    ballot_hashes = get_ballot_hashes(ballot_id, salt)
    await interaction.response.send_message(embed=from_ballot_hashes(ballot_hashes), ephemeral=True, delete_after=120)


@default_permissions(administrator=True)
class AutoKick(discord.app_commands.Group):

    @app_commands.command()
    async def start(self, interaction: Interaction):
        kick_unregistered_task.start()
        await interaction.response.send_message("Now auto-kicking unregistered users", ephemeral=True)

    @app_commands.command()
    async def stop(self, interaction: Interaction):
        kick_unregistered_task.stop()
        await interaction.response.send_message("No longer auto-kicking unregistered users", ephemeral=True)

    @app_commands.command()
    async def restart(self, interaction: Interaction):
        kick_unregistered_task.restart()
        await interaction.response.send_message("Restarted the auto-kicking of unregistered users", ephemeral=True)


bot.tree.add_command(AutoKick())


@tasks.loop(minutes=10)
async def kick_unregistered_task():
    await kick_unregistered(bot.get_guild(get_secret("GUILD_ID")))


@tasks.loop(seconds=10)
async def close_ballots_loop():
    await close_ballots(bot.get_guild(get_secret("GUILD_ID")))


if __name__ == '__main__':
    setup_logging()
    _logger = getLogger("bot.main")
    on_deploy()
    bot.run(get_secret("BOT_TOKEN"), log_handler=None)
