import datetime
import time

from discord import Embed

from db.repositories.ballot_repository import Ballot


_CLUSTER_RED = 0xd52020
_UTC = datetime.timezone.utc


def _cluster_embed(**kwargs) -> Embed:
    return Embed(colour=_CLUSTER_RED, **kwargs)


def from_ballot(ballot: Ballot) -> Embed:
    embed = _cluster_embed(title=ballot.name,
                           description=ballot.description)
    embed.set_footer(text=f"Ballot {ballot.ballot_id}")
    embed.add_field(name="Status", value=_get_closed_status(ballot), inline=False)
    for option_number, option in enumerate(ballot.options, 1):
        amount_text = "??" if ballot.is_closed else option.votes
        embed.add_field(name=f"Option {option_number}: {option.name}", value=amount_text, inline=False)
    return embed


def creating_ballot() -> Embed:
    return _cluster_embed(title="Creating ballot...", description="This shouldn't take long.")


def _get_closed_status(ballot: Ballot) -> str:
    if ballot.is_closed:
        return f"Closes at <t:{int(ballot.closes_at.timestamp())}:F>"
    return f"Closed"
