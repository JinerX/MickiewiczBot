from PyPDF2 import PdfReader
import pathlib
from pathlib import Path


PDF_FOLDER_PATH = 'data\\raw\\corpus\\pdf'



def pdf_to_txt(input_path, output_path):
    reader = PdfReader(input_path)
    with open(output_path, 'w', encoding='utf-8') as out_file:
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                out_file.write(text)
            else:
                pass


p = Path(PDF_FOLDER_PATH)


files = list(p.glob('*.pdf'))
print("Loading files: ")
for file in files:
    if len(files) == 0:
        print("Nothing loaded, exiting...")
    else:
        print("Processing file: ", str(file))
        pdf_to_txt(str(file), str(file).replace('pdf', 'txt'))


print("files processed")


