from typing import Protocol

from ..models import TurnJob, TurnResponse


class Adapter(Protocol):
    def run_turn(self, job: TurnJob) -> TurnResponse: ...
