import json


def get_unique_type_from_devices(input_circuit_devices):
    unique_types = set()

    # 遍历字典，提取每个设备的type并添加到集合中
    for device in input_circuit_devices.values():
        device_type = device.get("type")
        if device_type:
            unique_types.add(device_type)

    # 打印所有独立的type
    for device_type in unique_types:
        print(device_type)


if __name__ == "__main__":
    with open("matcher_subcircuit.json", "r", encoding="utf-8") as f:
        circuit_devices = json.load(f)["devices"]
    print(get_unique_type_from_devices(circuit_devices))
