from PyPDF2 import PdfReader
from pathlib import Path
import pdfplumber


PDF_FOLDER_PATH = 'data\\raw\\corpus\\pdf'
TXT_FOLDER_PATH = 'data\\raw\\corpus\\txt'

def pdf_to_txt(input_path, output_path):
    reader = PdfReader(input_path)
    with open(output_path, 'w', encoding='utf-8') as out_file:
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                out_file.write(text)
            else:
                pass


def pdf_to_txt_left_column(input_pdf: str, output_txt: str, frac_width=0.7, x_tol=1, y_tol=1):
    input_pdf = Path(input_pdf)
    output_txt = Path(output_txt)
    with pdfplumber.open(input_pdf) as pdf, output_txt.open('w', encoding='utf-8') as out:
        for page in pdf.pages:
            page_width = page.width
            cutoff_x = page_width * frac_width

            left_crop = page.within_bbox((0, 0, cutoff_x, page.height))
            text = left_crop.extract_text(layout=True,
                                          x_tolerance=x_tol,
                                          y_tolerance=y_tol)

            if text:
                out.write(text + "\n\n")



p = Path(PDF_FOLDER_PATH)


files = list(p.glob('*.pdf'))
for pdf_file in files:
    if len(files) == 0:
        print("Nothing loaded")
    else:
        print("Processing file:", str(pdf_file))
        pdf_to_txt_left_column(str(pdf_file), str(pdf_file).replace('pdf', 'txt'))


print("files processed")


