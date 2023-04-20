from discord import Interaction
from discord.app_commands import Choice

from db.repositories.ballot_repository import get_user_ballot_ids


async def autocomplete_student_email(interaction: Interaction, current_input: str):
    return [Choice(name=f"{current_input.split('@')[0]}@student.lut.fi", value=f"{current_input}@student.lut.fi")]


async def autocomplete_ballot_id(interaction: Interaction, current_input: str) -> list[Choice[int]]:
    voted_in_ballots = get_user_ballot_ids(interaction.user.id)
    matches = [Choice(name=f"{ballot.name} ({ballot.ballot_id})", value=str(ballot.ballot_id)) for ballot in voted_in_ballots
               if str(ballot.ballot_id).startswith(current_input)]
    return matches[:25]
