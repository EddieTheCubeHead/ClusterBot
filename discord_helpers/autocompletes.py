from discord import Interaction
from discord.app_commands import Choice


async def autocomplete_student_email(interaction: Interaction, current_input: str):
    return [Choice(name=f"{current_input.split('@')[0]}@student.lut.fi", value=f"{current_input}@student.lut.fi")]
