from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
from pathlib import Path

TXT_FOLDER_PATH = 'data\\raw\\corpus\\txt'
EPUB_FOLDER_PATH = 'data\\raw\\corpus\\epub'

def epub_to_txt(epub_path: str, txt_path: str):
    book = epub.read_epub(epub_path)
    parts = []
    # Grab every document (XHTML) part
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        content = item.get_content()
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        if text:
            parts.append(text)

    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(parts))


p = Path(EPUB_FOLDER_PATH)

files = list(p.glob('*.epub'))
for epub_file in files:
     print("processing file: ", str(epub_file))
     epub_to_txt(str(epub_file), str(epub_file).replace("epub", "txt"))


