from blueprint_code import get_blueprint_entries_from_shapez_code
from tabulate import tabulate


def print_blueprint(blueprint_code):
    entries = get_blueprint_entries_from_shapez_code(blueprint_code)

    minimum_x = min([t["X"] for t in entries])
    maximum_x = max([t["X"] for t in entries])
    minimum_y = min([t["Y"] for t in entries])
    maximum_y = max([t["Y"] for t in entries])

    block_list = {}
    block_map = [
        [" "] * (maximum_x - minimum_x + 1) for i in range((maximum_y - minimum_y + 1))
    ]

    for entry in entries:
        x = entry["X"] - minimum_x
        y = entry["Y"] - minimum_y
        if entry["T"] not in block_list:
            block_list[entry["T"]] = len(block_list) + 1
        entry_id = block_list[entry["T"]]
        block_map[y][x] = f"{entry_id},{entry['R']}"

    print(tabulate(block_map, tablefmt="plain"))
    print(tabulate(zip(block_list.keys(), block_list.values()), tablefmt="plain"))


if __name__ == "__main__":
    import pyperclip

    blueprint_code = pyperclip.paste()
    print_blueprint(blueprint_code)
