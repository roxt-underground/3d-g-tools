import logging
from decimal import Decimal as _d
from typing import Optional, Type


logger = logging.getLogger(__name__)

__hide__ = type('HideType', (), {})()

_speed = {'speed': ('F', __hide__)}
_x = {'x': ('X', __hide__)}
_y = {'y': ('Y', __hide__)}
_z = {'z': ('Z', __hide__)}
_filament = {'filament': ('E', __hide__)}

commands_mapping = {}


class CommandMetaclass(type):
    def __new__(cls, name, bases, attrs):
        result: Type[BaseCommand] = type.__new__(cls, name, bases, attrs)  # type: ignore
        result._param_to_python = dict(result.params.values())
        if hasattr(result, 'command'):
            commands_mapping[result.command] = result
        return result


class BaseCommand(metaclass=CommandMetaclass):
    command: str
    params: dict = {}
    comment: Optional[str] = None

    def __init__(self, *, comment: Optional[str] = None, **kwargs):
        if comment is not None:
            self.comment = comment
        invalid_args = set(kwargs.keys()) - set(self.params.keys())
        if invalid_args:
            raise ValueError(f'Invalid arguments: {", ".join(list(invalid_args))}')

        for key, (_, default) in self.params.items():
            value = kwargs.get(key, default)
            if value is __hide__:
                setattr(self, key, None)
                continue
            setattr(self, key, value)

    def __str__(self):
        results = [self.command]
        for key, (param, default) in self.params.items():
            value = getattr(self, key, None)
            if value is None:
                if default is __hide__:
                    continue
                else:
                    raise ValueError(f"{key} attr is None")
            results.append(f"{param}{value}")
        if self.comment:
            results.append(f'; {self.comment}')
        return ' '.join(results)

    @classmethod
    def from_string(cls, command: str):
        param_to_attr = {param: key for key, (param, _) in cls.params.items()}
        kwargs = {}

        command_end = None

        comment_start = command.find(';')
        if comment_start > -1:
            kwargs['comment'] = command[comment_start+1:].strip()
            command_end = comment_start

        params = command[:command_end].strip().split(' ')[1:]
        for param in params:
            param_key = param[0]
            param_value = param[1:]

            kwargs[param_to_attr[param_key]] = _d(param_value)

        return cls(**kwargs)


class RawCommand(BaseCommand):
    def __init__(self, *, raw_command: str):
        self.raw_command = raw_command

    def __str__(self):
        return self.raw_command

    @classmethod
    def from_string(cls, command: str):
        return cls(raw_command=command)

class Comment(BaseCommand):
    def __init__(self, *, comment: str):
        self.comment = comment

    def __str__(self):
        return f'; {self.comment}'

    @classmethod
    def from_string(cls, command: str):
        return cls(comment=command[command.find(';')+1:].strip())

class CodeBlock:
    def __init__(self, comment: str, commands: list[BaseCommand]):
        self.comment = comment
        self.commands = commands

    def __str__(self):
        results = [f'; --[[ {self.comment}']
        results.extend(map(str, self.commands))
        results.append(f'; {self.comment} ]]--')

        return '\n'.join(results)

class Move(BaseCommand):
    command = 'G1'
    params = {
        **_x,
        **_y,
        **_z,
        **_speed,
        **_filament,
    }


class EmptyMove(Move):
    command = 'G0'
    params = {
        **_x,
        **_y,
        **_z,
        **_speed,
    }


class Parking(BaseCommand):
    command = 'G28'
    params = {
        **_x,
        **_y,
        **_z,
    }

class ChangeCords(BaseCommand):
    command = 'G92'
    params = {
        **_x,
        **_y,
        **_z,
        **_filament,
    }

class Beep(BaseCommand):
    command = 'M300'
    params = {
        'time': ('P', 300),
        'freq': ('S', 4000),
    }


class Pause(BaseCommand):
    command = 'M25'


class Sleep(BaseCommand):
    command = 'G4'
    params = {
        'time': ('P', 1000),
    }



class AbsoluteExtruder(BaseCommand):
    command = 'M82'
    comment = 'absolute extrusion'


class RelativeExtruder(BaseCommand):
    command = 'M83'
    comment = 'relative extrusion'

generic_pause = CodeBlock(
    'pause',
    [
        Beep(),
        Pause(),
        Sleep(time=200),
    ]
)


def command_from_string(command: str, strict=False) -> BaseCommand:
    g_command = command.split(' ')[0]
    if g_command.strip().startswith(';'):
        return Comment.from_string(g_command)
    command_class = commands_mapping.get(g_command)
    if not command_class:
        msg = f'Unknown command: {command}'
        if strict:
            raise RuntimeError(msg)
        logger.warning(msg)
        return RawCommand(raw_command=command)

    return command_class.from_string(command)
