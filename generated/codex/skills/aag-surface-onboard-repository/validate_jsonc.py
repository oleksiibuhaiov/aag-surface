"""Read-only validation of editor JSON with comments and trailing commas."""
import json
import re
import sys
from pathlib import Path


def loads(text):
    # Consume strings before comments so URLs and escaped quotes remain intact.
    tokens = re.compile(r'"(?:[^"\\]|\\.)*"|//[^\n\r]*|/\*.*?\*/', re.S)
    def strip(match):
        value = match.group()
        return value if value.startswith('"') else re.sub(r'[^\r\n]', ' ', value)
    cleaned = tokens.sub(strip, text)
    tokens = re.compile(r'"(?:[^"\\]|\\.)*"|,(?=\s*[}\]])', re.S)
    cleaned = tokens.sub(lambda m: ' ' if m.group() == ',' else m.group(), cleaned)
    return json.loads(cleaned, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def main(paths):
    status = 0
    for path in paths:
        try:
            loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            print(f"{path}: {error}", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]) if len(sys.argv) > 1 else 2)
