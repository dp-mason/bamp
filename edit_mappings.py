import yaml

HANDLES_BUTTONS = {}
PRESSED_HANDLES_BUTTONS = {}

# Open and read the YAML file
with open("winamp_skin_specification.yaml", "r") as file:
    MAPPINGS: dict = yaml.safe_load(file)
    MAPPINGS.items

for file_key, elems_dict in MAPPINGS["blendamp"].items():
    for element, elemdata in elems_dict.items():
        # Skip processing if this is not a handle or a button
        if not ("handle" in element or "button" in element):
            continue

        MAPPINGS[file_key].pop(element)

        if "pressed" in element:
            PRESSED_HANDLES_BUTTONS[element] = elemdata
        else:
            HANDLES_BUTTONS[element] = elemdata

MAPPINGS["HANDLES_BUTTONS"] = HANDLES_BUTTONS
MAPPINGS["PRESSED_HANDLES_BUTTONS"] = PRESSED_HANDLES_BUTTONS

with open("NEW_winamp_skin_specification.yaml", "w") as newfile:
    yaml.dump(MAPPINGS, newfile)
