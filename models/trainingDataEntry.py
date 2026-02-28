from dataclasses import dataclass, asdict, field
from typing import List, Optional
from datetime import datetime


@dataclass
class TrainingDataEntry:
    """Represents a single training data record.
    The :attr:`timestamp` field is automatically set when new entries are
    created
    """
    player: str
    ownTeam: List[str]
    ownStrength: int
    wins: int
    losses: int
    enemyTeam: List[str]
    enemyStrength: int
    timestamp: Optional[datetime] = field(
        default_factory=datetime.now()
    )  # when the entry was created (auto-set on insert)

    def to_dict(self):
        # asdict handles datetime objects which pymongo will store as BSON datetimes
        return asdict(self)

    # helpful repr/str for debugging and logging
    def __repr__(self):
        # keep same format as dataclass but shorter fields if necessary
        return (
            f"TrainingDataEntry(player={self.player!r}, ownTeam={self.ownTeam!r}, "
            f"ownStrength={self.ownStrength!r}, wins={self.wins!r}, losses={self.losses!r}, "
            f"enemyTeam={self.enemyTeam!r}, enemyStrength={self.enemyStrength!r},"
            f"timestamp={self.timestamp!r})"
        )

    # alias for __repr__ when str() is called
    def __str__(self):
        return self.__repr__()
