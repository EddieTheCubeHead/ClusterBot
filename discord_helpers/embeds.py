import datetime
import time

from discord import Embed

from db.repositories.ballot_repository import Ballot, BallotHashes

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


def from_ballot_hashes(ballot_hashes: BallotHashes) -> Embed:
    embed = _cluster_embed(title=ballot_hashes.ballot_name,
                           description="Hashes for all options of the ballot with the given salt")
    for option_hash in ballot_hashes.option_hashes:
        embed.add_field(name=option_hash.option_name, value=option_hash.option_hash, inline=False)
    return embed


def _get_closed_status(ballot: Ballot) -> str:
    if ballot.is_closed:
        return f"Closes at <t:{int(ballot.closes_at.timestamp())}:F>"
    return f"Closed"


def from_exception_message(message: str) -> Embed:
    return _cluster_embed(title="An error occurred", description=message)
