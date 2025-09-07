import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class DecisionLog:
    content_name: str
    topic: str
    cohort: str
    ad_id: int
    placement_id: int
    reason: str
    safe_zone: Dict[str, int]
    clicked: int

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)