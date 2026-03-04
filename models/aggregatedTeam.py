from dataclasses import dataclass
from typing import List


@dataclass
class AggregatedTeam:
    ownTeam: List[str]
    maxOwnStrength: int