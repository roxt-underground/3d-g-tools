from lib.commands import Beep, command_from_string, generic_pause, Pause


gg = [
    command_from_string('G1 X11.43 Y0.17 Z0.16 F1500 E12'),
    command_from_string('G0 X11.43 Y0.17 F1500 ;kek lol'),
    command_from_string('G1 F1500 E12'),
    Pause(comment='pause'),
    command_from_string('G4 P4000'),
    Beep(),
    generic_pause,
]

print('\n'.join(list(map(str, gg))))
