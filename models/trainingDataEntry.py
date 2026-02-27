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
