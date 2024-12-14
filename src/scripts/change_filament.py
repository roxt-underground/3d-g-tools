from decimal import Decimal
from typing import Union

from lib.commands import (
    ChangeCords, CodeBlock, Move, Parking, generic_pause, RelativeExtruder,
    AbsoluteExtruder, Sleep, EmptyMove
)


AccurateNumber = Union[Decimal, int]

def change_filament(
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
