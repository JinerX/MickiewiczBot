from pathlib import Path
import re
from data.constants import RAW_TXT_FOLDER_PATH, CLEAN_TXT_FOLDER_PATH

p = Path(RAW_TXT_FOLDER_PATH)


        # footnote_pattern = re.compile(
        #     r'[¹²³⁴⁵⁶⁷⁸⁹⁰]+[.\n]*\[[.\n]+\]\s*',
        #     flags=re.MULTILINE
        # )


def process(input_path, output_path):
    with open(input_path, "r", encoding='utf-8') as out_file:
        
        file_name = " ".join(input_path.split("\\")[-1].split(".")[0].split("-"))
        print(file_name)

        data = out_file.read()
        data = data.replace("(cid:3095)","j")
        data = data.replace("ǳ", "dz")
        data = data.replace("ǲ", "Dz")
    

        # starting_whitespace = re.compile(r"^\s+", flags=re.MULTILINE)
        # data = starting_whitespace.sub("", data)


        cleaned_lines = [ line.lstrip().rstrip() for line in data.splitlines() ]
        data = "\n".join(cleaned_lines)


        multiple_newlines = re.compile(r'\n\n+', flags=re.MULTILINE)
        data = multiple_newlines.sub("\n", data)

        # removing footnotes start of a line with small number then some sort of description with different characters including newlines, then the ending in square brackets written either as
        # [przypis edytorski] or [przypis autorski] however it could be split across different lines like
        # [przyp-
        #-is eydtorski] and such with trailing whitespace



        footnote_pattern = re.compile(
            r'^[¹²³⁴⁵⁶⁷⁸⁹⁰]+[\s\S]*?\[[\s\S]+?\]\s*',
            flags=re.MULTILINE
        )

        data = footnote_pattern.sub("", data)
        tiny_digit_pattern = re.compile(r'[¹²³⁴⁵⁶⁷⁸⁹⁰]+',
                                        flags=re.MULTILINE)
        data = tiny_digit_pattern.sub("", data)

        # unknown_pattern = re.compile(r'\s*[]+\s*',
        #                              flags=re.MULTILINE)



        pua_pattern = re.compile(r'[\uE000-\uF8FF]+', flags=re.UNICODE)
        data = pua_pattern.sub("", data)

        ending_pattern = re.compile(r"Wszystkie zasoby Wolnych Lektur możesz swobodnie[\s\S]*")
        data = ending_pattern.sub("", data)
        starting_pattern = re.compile(r"Ta lektura, podobnie jak tysiące innych,[\s\S]+Wolne Lektury.")
        data = starting_pattern.sub("", data)


        data = re.sub(r'[ \t]*\(cid:\d+\)[ \t]*', '', data)

        with open(output_path, "w", encoding="utf-8") as txt:
            if data:
                txt.write(data)
            else:
                pass



files = list(p.glob('*.txt'))
for file in files:
    print("processing: ", str(file))
    process(str(file), CLEAN_TXT_FOLDER_PATH + "\\" + str(file.name))

