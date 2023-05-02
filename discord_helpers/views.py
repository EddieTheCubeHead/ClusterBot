import discord
from discord import Interaction

from configuration.configuration_service import get_secret
from db.repositories.ballot_repository import add_vote, Ballot, fetch_ballot, verify_vote
from db.repositories.user_repository import get_user, is_verified
from discord_helpers.exception_handling import UserException, ExceptionCatcherView
from discord_helpers.embeds import from_ballot
from services.email_service import EmailService
from services.vote_hasher import create_hash


class BallotOptionButton(discord.ui.Button):

    def __init__(self, ballot_id: int, name: str, option_id: int, email_service: EmailService):
        super().__init__()
        self.label = name
        self._ballot_id = ballot_id
        self._option_id = option_id
        self._email_service = email_service

    async def callback(self, interaction: Interaction):
        _verify_voter(interaction)
        verify_vote(self._ballot_id, interaction.user.id)
        ballot = fetch_ballot(self._ballot_id)
        hashed_vote = create_hash(self.label)
        self._send_salt_email(interaction, ballot, hashed_vote.salt)
        add_vote(self._ballot_id, interaction.user.id, self._option_id, hashed_vote.hash)
        await interaction.response.edit_message(embed=from_ballot(ballot), view=BallotView(ballot))

    def _send_salt_email(self, interaction: Interaction, ballot: Ballot, salt: str):
        subject = f"Ballot '{ballot.name}' vote saved"
        content = f"Your vote on the ballot '{ballot.name}' was saved by ClusterBot. The ballot ID is " \
                  f"{ballot.ballot_id}. The vote is hashed with the salt '{salt}'. Please use the command " \
                  f"/check-vote [ballot_id] to get the saved hash and /try-hash [option-name] [salt] to compare " \
                  f"your hash to the saved hash if you want to verify your vote later."
        self._email_service.send_email(get_user(interaction.user.id).email, f"Subject: {subject}\n\n{content}")


def _verify_voter(interaction: Interaction):
    if not is_verified(interaction.user.id):
        raise UserException("Unverified user.")


class BallotView(ExceptionCatcherView):

    def __init__(self, ballot: Ballot):
        super().__init__()
        self._email_service = EmailService(get_secret("EMAIL_PASSWORD"))
        for option in ballot.options:
            self.add_item(BallotOptionButton(ballot.ballot_id, option.name, option.option_id, self._email_service))
