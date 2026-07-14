from typing import Tuple
import yaml


# snippet used to generate the character mappings in the spec
def generate_spec_mappings(char_height, char_width):

    row1 = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ"@')
    row2 = list("0123456789") + ["..."] + list(".=()-'!_+\\/[]^&%,=$#")
    row3 = list("äöa?* ")

    posdict = {}

    # I know this is stupid. Just allow it, ok?
    for char_idx in range(0, len(row1)):
        posdict[row1[char_idx]] = [
            char_idx * char_width,
            0,
            # (char_idx + 1) * char_width - 1,
            # char_height - 1,
        ]
    for char_idx in range(0, len(row2)):
        posdict[row2[char_idx]] = [
            char_idx * char_width,
            char_height,
        ]
    for char_idx in range(0, len(row3)):
        posdict[row3[char_idx]] = [
            char_idx * char_width,
            char_height * 2,
        ]

    return posdict


myd = generate_spec_mappings(6, 5)
for key, value in myd.items():
    print(f"{key}: {value}")


# add a new region to the list and make sure it is ordered by size and
# region name length
def add_to_region_list(rl: list, new_region):
    assert type(new_region) is tuple and len(new_region) == 5
    if len(rl) == 0:
        rl.append(new_region)
        return
    position = 0
    for region in rl:
        # bigger elements come before smaller elements in the region list
        # in case of a tie, the element with the shorter name wins earlier placement
        if new_region[2] > region[2] or (
            new_region[2] == region[2] and len(new_region[4]) < len(region[4])
        ):
            break
        position += 1
    rl.insert(position, new_region)


# find all the overlapping elements that exist at a given pixel position
def layers_at(x_pos: int, y_pos: int):

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
                    target_regions, (region[0], region[1], area, file_key, element)
                )

    for idx in range(0, len(target_regions)):
        print(f"{idx}:", target_regions[idx])
