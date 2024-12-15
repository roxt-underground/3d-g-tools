from lib.commands import BaseCommand, EmptyMove, Move


class MovementMonitor:
    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
        self.filament = None

    def register(self, command: BaseCommand):
        params = []
        if isinstance(command, Move):
            params = ['x', 'y', 'z', 'filament']
        if isinstance(command, EmptyMove):
            params = ['x', 'y', 'z']

        for param in params:
            if getattr(command, param) is not None:
                setattr(self, param, getattr(command, param))
