import datetime

from discord import Interaction, Guild, TextChannel

from db.repositories import user_repository, role_repository
from db.repositories.ballot_repository import create_ballot, fetch_ballots_to_close, mark_as_closed
from discord_helpers.embeds import from_ballot, creating_ballot
from discord_helpers.views import BallotView


async def kick_unregistered(guild: Guild):
    async for member in guild.fetch_members():
        if (not user_repository.is_verified(member.id)
                and not member.bot
                and member.joined_at + datetime.timedelta(days=1) < datetime.datetime.now(datetime.timezone.utc)):
            await member.kick(reason="Not registered as a guild member")
            print(f"Kicked {member.name}")
        else:
            print(f"Did not kick {member.name}")


async def register_user(interaction: Interaction, email: str):
    user_repository.add_registered(interaction.user.id, email)
    role = interaction.guild.get_role(role_repository.get_role_id("Jäsen"))
    await interaction.user.add_roles(role)
    await interaction.response.send_message("Registration successful", ephemeral=True)


async def create_ballot_message(interaction: Interaction, name: str, description: str, closes_at: datetime.datetime,
                                options: list[str]):
    await interaction.response.send_message(embed=creating_ballot())
    ballot_message = (await interaction.original_response())
    ballot = create_ballot(ballot_message, interaction.user.id, name, description, closes_at, options)
    await ballot_message.edit(embed=from_ballot(ballot), view=BallotView(ballot))


async def close_ballots(guild: Guild):
    channels: dict[int, TextChannel] = {}
    closed_ballots: list[int] = []
    for ballot in fetch_ballots_to_close():
        if ballot.channel_id not in channels:
            channels[ballot.channel_id] = await guild.fetch_channel(ballot.channel_id)
        message = await channels[ballot.channel_id].fetch_message(ballot.ballot_id)
        await message.edit(embed=from_ballot(ballot), view=None)
        closed_ballots.append(ballot.ballot_id)
    mark_as_closed(*closed_ballots)
