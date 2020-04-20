from enum import Enum

class RunConditions(Enum):
    TIME = 'TIME'
    MANUAL = 'MANUAL'

class Stage:
    def __init__(self, name, condition):
        self.name = name
        self.condition = condition

class EventStages:
    def __init__(self, name, stages = []):
        self.name = name
        self.stages = stages

    def add_stage(self, stage):
        self.stages.append(stage)