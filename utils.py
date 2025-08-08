import os

SAVE_DIR = "temp_files"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def save_file(data: bytes, filename: str) -> str:
    path = os.path.join(SAVE_DIR, filename)
    with open(path, "wb") as f:
        f.write(data)
    return path

def delete_file(path: str):
    try:
        os.remove(path)
    except Exception as e:
        print(f"Ошибка при удалении файла {path}: {e}")
