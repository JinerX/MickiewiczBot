from .BPE import BPE
from ..constants import CLEAN_TXT_FOLDER_PATH, TEST_FOLDER_PATH

bpe = BPE()

bpe.fit(TEST_FOLDER_PATH)