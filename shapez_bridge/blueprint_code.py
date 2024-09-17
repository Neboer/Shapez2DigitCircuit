import base64
import gzip
import json
from io import BytesIO


def decode_blueprint_content(encoded_str):
    # Base64解码
    compressed_data = base64.b64decode(encoded_str)

    # Gzip解压
    with gzip.GzipFile(fileobj=BytesIO(compressed_data), mode="rb") as f:
        json_data = f.read().decode("utf-8")

    # JSON解码
    return json.loads(json_data)


def encode_blueprint_content(data):
    # JSON编码
    json_str = json.dumps(data)

    # Gzip压缩
    with BytesIO() as compressed_buffer:
        with gzip.GzipFile(fileobj=compressed_buffer, mode="wb") as f:
            f.write(json_str.encode("utf-8"))
        compressed_data = compressed_buffer.getvalue()

    # Base64编码
    return base64.b64encode(compressed_data).decode("utf-8")


def complete_blueprint_entries(input_blueprint_entries):
    for entry in input_blueprint_entries:
        if "R" not in entry:
            entry["R"] = 0
        if "X" not in entry:
            entry["X"] = 0
        if "Y" not in entry:
            entry["Y"] = 0

def decode_entries_numbers(input_blueprint_entries):
    for entry in input_blueprint_entries:
        if "C" in entry:
            entry["C"] = int.from_bytes(base64.b64decode(entry["C"]), byteorder="big")

def encode_entries_numbers(input_blueprint_entries):
    for entry in input_blueprint_entries:
        if "C" in entry:
            entry["C"] = base64.b64encode(entry["C"].to_bytes(8, byteorder="big")).decode("utf-8")


def decode_blueprint(shapez_str):
    return decode_blueprint_content(shapez_str[len("SHAPEZ2-1-") : -1])


def encode_blueprint(input_content):
    return f"SHAPEZ2-1-{encode_blueprint_content(input_content)}$"


def get_blueprint_entries_from_shapez_code(input_string):
    decoded_entries = decode_blueprint(input_string)["BP"]["Entries"]
    complete_blueprint_entries(decoded_entries)
    decode_entries_numbers(decoded_entries)
    return decoded_entries

shapez_data = {
    "V": 1095,
    "BP": {
        "$type": "Building",
        "Icon": {
            "Data": [
                "icon:Buildings",
                None,
                None,
                "shape:CuCuCuCu"
            ]
        },
        "Entries": [],
        "BinaryVersion": 1095
    }
}

def get_shapez_code_from_blueprint_entries(input_entries):
    shapez_data["BP"]["Entries"] = input_entries
    return encode_blueprint(shapez_data)

if __name__ == "__main__":
    import pyperclip

    with open("../samples/blueprint.json", "w") as f:
        json.dump(decode_blueprint(pyperclip.paste()), f)
