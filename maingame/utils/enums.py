from enum import Enum


class StatusType(Enum):
    PENDING = 1
    INITIATED = 2
    COMPLETED = 3
    FAILED = 4

class EventType(Enum):
    STANDARD = 1

class UserRoles(Enum):
    BASIC = 1
    ADMIN = 2