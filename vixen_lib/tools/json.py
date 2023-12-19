import json

def write(path: str, data: dict) -> bool:
    try:
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except IOError as e: print(e)
    
    return False

def read(path: str) -> dict|None:
    data = None

    try:
        with open(path, 'r') as fichier:
            data = json.load(fichier)
    except FileNotFoundError as e: print(e)
    except json.JSONDecodeError as e: print(e)

    return data

create = write

def update(path: str, data: dict) -> bool:
    file_data = read(path)

    if file_data:
        file_data.update(data)
        if write(path, file_data): return True

    return False