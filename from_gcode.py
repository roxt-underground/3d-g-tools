from lib.commands import Beep, command_from_string, EmptyMove, generic_pause, Move, Pause


gg = [
    command_from_string('G1 X11.43 Y0.17 Z0.16 F1500 E12'),
    command_from_string('G0 X12.43 Y0.17 F1500 ;kek lol'),
    command_from_string('G1 F1500 E12'),
    Pause(comment='pause'),
    command_from_string('G4 P4000'),
    EmptyMove(x=13.47, y=1.43),
    Move(x=16.0, filament=14, speed=100),
    Beep(),
    generic_pause,
]

print('\n'.join(list(map(str, gg))))
