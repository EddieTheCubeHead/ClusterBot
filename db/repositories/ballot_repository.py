import datetime
import hashlib
import secrets
from dataclasses import dataclass

from discord import Message

from discord_helpers.exception_handling import UserException
from migration_engine import con
from services.vote_hasher import create_from_salt

_UTC = datetime.timezone.utc


@dataclass
class BallotOption:
    option_id: int
    name: str
    votes: int = 0


@dataclass
class Ballot:
    ballot_id: int
    channel_id: int
    name: str
    description: str
    creator_id: int
    closes_at: datetime.datetime
    options: list[BallotOption]
    voter_ids: list[int]

    @property
    def is_closed(self) -> bool:
        return self.closes_at > datetime.datetime.now().astimezone(_UTC)


@dataclass
class OptionHash:
    option_name: str
    option_hash: str


@dataclass
class BallotHashes:
    ballot_name: str
    option_hashes: list[OptionHash]


def create_ballot(message: Message, creator_id: int, name: str, description: str, closes_at: datetime.datetime,
                  option_names: list[str]) -> Ballot:
    created_at = datetime.datetime.now().astimezone(_UTC)
    con.execute("INSERT INTO Ballots (ID, ChannelID,  CreatedBy, ClosesAt, CreatedAt, UpdatedAt, Name, Description) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (message.id, message.channel.id, creator_id, closes_at, created_at, created_at, name, description))
    options: list[BallotOption] = []
    for option_name in option_names:
        option_id = con.execute("INSERT INTO BallotOptions (BallotID, Name, CreatedAt) VALUES (?, ?, ?) RETURNING ID",
                                (message.id, option_name, created_at)).fetchone()[0]
        options.append(BallotOption(option_id, option_name))
    con.commit()
    return Ballot(message.id, message.channel.id, name, description, creator_id, closes_at, options,
                  [])


def fetch_ballot(ballot_id: int) -> Ballot:
    votes = _fetch_votes(ballot_id)
    options = _fetch_options(ballot_id)
    ballot_data = con.execute("SELECT ChannelID, Name, Description, CreatedBy, ClosesAt FROM Ballots WHERE ID = ?",
                              (ballot_id,)).fetchone()
    channel_id, name, description, creator_id, closes_at_raw = ballot_data
    closes_at = datetime.datetime.strptime(closes_at_raw, "%Y-%m-%d %H:%M:%S.%f%z")
    return Ballot(ballot_id, channel_id, name, description, creator_id, closes_at, options, votes)


def _fetch_votes(ballot_id: int) -> list[int]:
    votes = con.execute("SELECT UserID FROM BallotUserVotes WHERE BallotID = ?", (ballot_id,)).fetchall()
    return [vote[0] for vote in votes]


def _fetch_options(ballot_id: int) -> list[BallotOption]:
    options = con.execute("SELECT ID, Name, Votes FROM BallotOptions WHERE BallotID = ?", (ballot_id,)).fetchall()
    return [BallotOption(*option) for option in options]


def verify_vote(ballot_id: int, user_id: int):
    exists = con.execute("SELECT EXISTS(SELECT 1 FROM BallotUserVotes WHERE BallotID = ? AND UserID = ?)",
                         (ballot_id, user_id)).fetchone()[0]
    if exists:
        raise UserException("Already voted!")


def add_vote(ballot_id: int, user_id: int, option_id: int, vote_hash: str) -> str:
    created_at = datetime.datetime.now().astimezone(_UTC)
    con.execute("UPDATE BallotOptions SET Votes = Votes + 1 WHERE ID = ?", (option_id,))
    con.execute("INSERT INTO BallotUserVotes (UserID, BallotID, Hash, CreatedAt) VALUES (?, ?, ?, ?)",
                (user_id, ballot_id, vote_hash, created_at))
    con.commit()
    return vote_hash


def fetch_ballots_to_close() -> list[Ballot]:
    unclosed_ballots = con.execute("SELECT ID, ChannelID, Name, Description, CreatedBy, ClosesAt FROM Ballots WHERE "
                                   "ClosesAt < CURRENT_TIMESTAMP AND Closed = 0").fetchall()
    return create_ballots_from_data(unclosed_ballots)


def create_ballots_from_data(ballot_data: list[(int, int, str, str, int, str)]):
    ballots = []
    for ballot in ballot_data:
        ballot_id, channel_id, name, description, creator_id, closes_at_raw = ballot
        closes_at = datetime.datetime.strptime(closes_at_raw, "%Y-%m-%d %H:%M:%S.%f%z")
        votes = _fetch_votes(ballot_id)
        options = _fetch_options(ballot_id)
        ballots.append(Ballot(ballot_id, channel_id, name, description, creator_id, closes_at, options, votes))
    return ballots


def mark_as_closed(*ballot_ids: int):
    con.execute(f"UPDATE Ballots SET Closed = 1 WHERE ID in ({', '.join('?'*len(ballot_ids))})", ballot_ids)
    con.commit()


def get_vote_hash(ballot_id: int, user_id: int) -> str:
    vote_data = con.execute("SELECT Hash FROM BallotUserVotes WHERE BallotID = ? AND UserID = ?", (ballot_id, user_id))\
        .fetchone()
    if vote_data:
        return vote_data[0]


def get_user_ballot_ids(user_id: int) -> list[Ballot]:
    ballot_data = con.execute("SELECT B.ID, B.ChannelID, B.Name, B.Description, B.CreatedBy, B.ClosesAt "
                              "    FROM BallotUserVotes "
                              "        LEFT JOIN Ballots B on B.ID = BallotUserVotes.BallotID "
                              "        WHERE UserID = ?"
                              "        ORDER BY B.Closed DESC, B.ClosesAt DESC",
                              (user_id,)).fetchall()
    return create_ballots_from_data(ballot_data)


def get_ballot_hashes(ballot_id: int, salt: str) -> BallotHashes:
    ballot = fetch_ballot(ballot_id)
    option_hashes = [OptionHash(option.name, create_from_salt(option.name, salt)) for option in ballot.options]
    return BallotHashes(ballot.name, option_hashes)
