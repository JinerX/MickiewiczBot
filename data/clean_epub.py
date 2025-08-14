from pathlib import Path
import re

from constants import CLEAN_TXT_FOLDER_PATH, RAW_TXT_FOLDER_PATH


def process(input: str, output: str):
    print(input)
    with open(input, "r", encoding='utf-8') as raw_file:
        text = raw_file.read()
        footnote_pattern = re.compile(r"\s*Przypisy:[\s\S]*")
        text = footnote_pattern.sub("", text)
        start_pattern = re.compile(r"[\s\S]*Strona redakcyjna\s*?")
        text = start_pattern.sub("", text)
        pattern = re.compile(r'\n^\d+?\n', flags=re.MULTILINE)

        text = pattern.sub(" ", text)
        with open(output, "w", encoding='utf-8') as processed_file:
            processed_file.write(text)


p = Path(RAW_TXT_FOLDER_PATH)

files = list(p.glob("*.txt"))
for file in files:
    print("processing: ", file.name)
    process(str(file), CLEAN_TXT_FOLDER_PATH + "\\cleaned-" + file.name)