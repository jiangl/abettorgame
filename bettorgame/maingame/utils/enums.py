from enum import Enum


class StatusType(Enum):
    PENDING = 'PENDING'
    INITIATED = 'INITIATED'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

class EventType(Enum):
    STANDARD = 'STANDARD'

class UserRoles(Enum):
    BASIC = 'BASIC'
    ADMIN = 'ADMIN'