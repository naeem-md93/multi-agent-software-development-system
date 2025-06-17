

def read_text_file(file_path: str) -> str:
    with open(file_path, 'r', encoding="utf-8") as stream:
        content = stream.read()
    return content