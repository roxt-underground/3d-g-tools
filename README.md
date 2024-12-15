# 3D g-tools
## Сниппеты для редактирования g-code для принтеров

### Cмена филамента
```python
import re

from scripts.change_filament import FilamentChange


class MyFilamentChange(FilamentChange):

    re_group = re.compile(r';LAYER:(\d+)')

    def detect_layer(self, row, command):
        found: list[str] = self.re_group.findall(row)
        if found and int(found[0]) == self.layer_number:
            return True


if __name__ == "__main__":
    
    # Замена филамента на 9 слое
    LAYER_NUMBER = 9
    filament_change = MyFilamentChange('./input.gcode', LAYER_NUMBER)
    filament_change.process()
    filament_change.buffer.seek(0)
    with open('result.gcode', 'w') as output_file:
        output_file.write(filament_change.buffer.read())
```
