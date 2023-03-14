from discord import Guild

from db.repositories import role_repository


async def ensure_roles(guild: Guild):
    role_data = role_repository.get_uninitialized_roles()
    for name, colour in role_data:
        await _ensure_role(guild, name, colour)


async def _ensure_role(guild: Guild, name: str, colour: int | None):
    role = next((role for role in guild.roles if role.name == name), None)
    if role is None:
        role = await guild.create_role(name=name, colour=colour)
    elif colour and colour != role.colour:
        await role.edit(colour=colour)
    role_repository.mark_as_initialized(role.name, role.id)
