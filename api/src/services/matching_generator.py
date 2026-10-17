import secrets
from collections.abc import Sequence

from api.src.models import Participant


class MatchingGenerator:
    """Generate valid Secret Santa assignments."""

    def generate(
        self,
        participants: Sequence[Participant],
    ) -> list[tuple[Participant, Participant]]:
        if len(participants) < 2:
            raise ValueError(
                "At least two participants are required."
            )

        shuffled = list(participants)
        secrets.SystemRandom().shuffle(shuffled)

        return [
            (giver, shuffled[(index + 1) % len(shuffled)])
            for index, giver in enumerate(shuffled)
        ]