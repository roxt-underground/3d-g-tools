import logging
from decimal import Decimal
from io import StringIO
from typing import Optional, Union

from lib.commands import (
    ChangeCords, CodeBlock, command_from_string, Move, Parking, generic_pause, RelativeExtruder,
    AbsoluteExtruder, Sleep, EmptyMove,
)
from utils import MovementMonitor


logger = logging.getLogger(__name__)

AccurateNumber = Union[Decimal, int]

def change_filament_script_fabric(
        return_position: tuple[AccurateNumber, AccurateNumber, AccurateNumber], # x, y, z
        return_filament: AccurateNumber,
        unload_length: AccurateNumber,
        fasst_load_length: AccurateNumber,
        slow_load_length: AccurateNumber,
        retract_after_load: AccurateNumber,
        sleep_duration: int,
):
    x, y, z = return_position
    return CodeBlock('Change Filament',[
        Move(z=z+5, comment='raise Z up'),
        Parking(x=0, comment='parking extruder'),
        generic_pause,

        RelativeExtruder(),
        Move(filament=unload_length * -1, speed=700, comment='unload filament'),
        generic_pause,

        RelativeExtruder(),
        Move(filament=fasst_load_length, speed=400, comment='fasst load filament'),
        Sleep(time=sleep_duration),

        RelativeExtruder(),
        Move(filament=slow_load_length, speed=100, comment='slow load filament'),
        Move(filament=retract_after_load *- 1, speed=1500),
        generic_pause,

        # Reset to existing position
        AbsoluteExtruder(),
        ChangeCords(filament=return_filament, comment='restore filament position'),
        ChangeCords(filament=return_filament, comment='restore filament position'),
        EmptyMove(x=x, y=y, z=z, speed=3000, comment='restore extruder position'),
    ])


class FilamentChange:
    buffer: Optional[StringIO]
    monitor: Optional[MovementMonitor]

    unload_length = 70
    fasst_load_length = 30
    slow_load_length = 40
    retract_after_load = 5
    sleep_duration = 2000

    def __init__(self, file_path: str, layer_number: int):
        self.file_path = file_path
        self.buffer = None
        self.layer_number = layer_number

    def process(self):
        self.buffer = StringIO()
        self.monitor = MovementMonitor()

        with open(self.file_path, "r") as input_file:
            for i, row in enumerate(input_file):
                if row.strip():
                    command = command_from_string(row.strip('\n'))
                    self.monitor.register(command)
                    self.buffer.write(row)
                    if self.detect_layer(row, command):
                        logger.info(f'Found layer at {i} row. Inserting script.')
                        self.insert_change_script()
                else:
                    self.buffer.write(row)
        return self.buffer

    def detect_layer(self, row, command):
        """ redefine this function to find place right place """
        return False

    def insert_change_script(self):
        self.buffer.write(change_filament_script_fabric(
            return_position=(self.monitor.x, self.monitor.y, self.monitor.z),
            return_filament=self.monitor.filament,
            unload_length=self.unload_length,
            fasst_load_length=self.fasst_load_length,
            slow_load_length=self.slow_load_length,
            retract_after_load=self.retract_after_load,
            sleep_duration=self.sleep_duration,
        ).__str__())
        self.buffer.write('\n')
