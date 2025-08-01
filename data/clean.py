from pathlib import Path
import re
from constants import RAW_TXT_FOLDER_PATH, CLEAN_TXT_FOLDER_PATH

p = Path(RAW_TXT_FOLDER_PATH)


        # footnote_pattern = re.compile(
        #     r'[¹²³⁴⁵⁶⁷⁸⁹⁰]+[.\n]*\[[.\n]+\]\s*',
        #     flags=re.MULTILINE
        # )


def process(input_path, output_path):
    with open(input_path, "r", encoding='utf-8') as out_file:
        data = out_file.read()
        data = data.replace("గ","j")
        data = data.replace("ǳ", "dz")

        footnote_pattern = re.compile(
            r'[¹²³⁴⁵⁶⁷⁸⁹⁰]+[\s\S]*?\[[\s\S]*?\]',
            flags=re.MULTILINE
        )

        data = footnote_pattern.sub("", data)
        print(data)



files = list(p.glob('*.txt'))
# for file in files:
    # print(str(file))

process(RAW_TXT_FOLDER_PATH + "\\renegat.txt", "")