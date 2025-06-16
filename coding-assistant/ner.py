import re
from coding_assistant import utils


def extract_code_structures_for_spacy(code: str):
    entities = []
    lines = code.splitlines()
    inside_main = False
    inside_comment_block = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip inside multi-line comments (triple quotes)
        if re.match(r'^["\']{3}', stripped):
            inside_comment_block = not inside_comment_block
            continue

        if inside_comment_block or stripped.startswith("#"):
            continue

        # Check for __name__ guard
        if re.match(r'if __name__\s*==\s*["\']__main__["\']:', stripped):
            inside_main = True
            continue

        if inside_main:
            continue

        # Import statements
        if re.match(r'^(from\s+\S+\s+import|import\s+\S+)', stripped):
            start = code.find(line)
            end = start + len(line)
            entities.append((start, end, "IMPORT"))

        # Global variable (simple heuristic: assignment at top level without 'def' or 'class')
        elif re.match(r'^[A-Za-z_]\w*\s*=.*', stripped) and not line.startswith(" "):
            start = code.find(line)
            end = start + len(line)
            entities.append((start, end, "GLOBAL_VAR"))

        # Function definition
        elif re.match(r'^def\s+\w+\s*\(.*\):', stripped):
            start = code.find(line)
            end = start + len(line)
            entities.append((start, end, "FUNC_DEF"))

        # Method definition (function within class, identified by indent and def)
        elif re.match(r'^\s+def\s+\w+\s*\(.*\):', line):
            start = code.find(line)
            end = start + len(line)
            entities.append((start, end, "METHOD_DEF"))

    return [(code, {"entities": entities})]


# Example usage
if __name__ == "__main__":
    project_files = utils.get_project_files("./coding_assistant", (".py", ), (".venv", ))

    for fp in project_files:
        content = utils.read_text_file(fp)
        training_data = extract_code_structures_for_spacy(content)

        for text, ann in training_data:
            print(fp)
            print(text[:80].replace("\n", " ") + "...")
            print(ann)
            print("======================")
