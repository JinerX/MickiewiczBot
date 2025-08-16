from .BPE import BPE
from ..constants import CLEAN_TXT_FOLDER_PATH, TEST_FOLDER_PATH

bpe = BPE()

bpe.load_dicts_as_JSON("bpe_dicts.json")


with open(TEST_FOLDER_PATH + r"\\bpe_test.txt") as f:
    text = f.read()
print(text)

encoded_text = bpe.transform(text=text)
print(encoded_text)