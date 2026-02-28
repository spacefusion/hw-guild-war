from dataclasses import dataclass, asdict
from typing import List


@dataclass
class TrainingDataEntry:
    player: str
    ownTeam: List[str]
    ownStrength: int
    wins: int
    losses: int
    enemyTeam: List[str]
    enemyStrength: int

    def to_dict(self):
        return asdict(self)

    # helpful repr/str for debugging and logging
    def __repr__(self):
        # keep same format as dataclass but shorter fields if necessary
        return (
            f"TrainingDataEntry(player={self.player!r}, ownTeam={self.ownTeam!r}, "
            f"ownStrength={self.ownStrength!r}, wins={self.wins!r}, losses={self.losses!r}, "
            f"enemyTeam={self.enemyTeam!r}, enemyStrength={self.enemyStrength!r})"
        )

    # alias for __repr__ when str() is called
    def __str__(self):
        return self.__repr__()
