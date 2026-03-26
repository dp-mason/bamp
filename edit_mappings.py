from typing import Tuple
import yaml


def add_to_region_list(rl: list, new_region):
    assert type(new_region) is tuple and len(new_region) == 4
    if len(rl) == 0:
        rl.append(new_region)
        return
    position = 0
    for region in rl:
        if new_region[2] > region[2]:
            break
        position += 1
    rl.insert(position, new_region)


x_pos = int(input("X Position: "))
y_pos = int(input("Y Position: "))

# Open and read the YAML file
with open("winamp_skin_specification.yaml", "r") as yfile:
    MAPPINGS: dict = yaml.safe_load(yfile)

target_regions = []

for file_key, elems_dict in MAPPINGS["blendamp"].items():
    if file_key == "text.png":
        continue
    for element, elemdata in elems_dict.items():
        region: list = elemdata["region"]
        if (
            x_pos >= region[0]
            and x_pos <= region[2]
            and y_pos >= region[1]
            and y_pos <= region[3]
        ):
            area = (region[2] - region[0]) * (region[3] - region[1])
            add_to_region_list(
                target_regions, (region[0], region[1], area, f"{file_key} : {element}")
            )

for reg in target_regions:
    print(reg)

with open("NEW_winamp_skin_specification.yaml", "w") as newfile:
    yaml.dump(MAPPINGS, newfile, default_flow_style=False)
