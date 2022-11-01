import time
from dataclasses import dataclass


@dataclass
class QueuedUser:
    """
    Structure that contains user info
    """
    user_name: str
    id: int
    queue_time: float = time.time()
