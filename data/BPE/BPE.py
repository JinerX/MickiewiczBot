import typing
from collections import Counter, defaultdict
import heapq
from pathlib import Path
from ..constants import REMOVED


class BPE:
    '''
    BPE: byte-pair encoder class
    '''
    def __init__(self):
        self.merges = defaultdict(lambda: None, {})
        self.vocabulary = set()
        self.merge_heap = None
        self.counter = 0
        self.entry_finder = dict()
    
    def _push_pair(self, tokens: tuple[int,int], priority: int):
        if tokens in self.entry_finder:
            self._remove_pair(tokens)
        entry = [priority, self.counter, tokens]
        self.entry_finder[tokens] = entry
        heapq.heappush(self.merge_heap, entry)
        self.counter += 1

    def _remove_pair(self, tokens: tuple[int, int]):
        if tokens not in self.entry_finder:
            raise ValueError("attempted removing tokens which are not in the entry_finder")
        entry = self.entry_finder.pop(tokens)
        entry[-1] = REMOVED
    
    def _pop_pair(self):
        if not self.merge_heap:
            raise KeyError("heap doesn't exist or is empty")
        priority, counter, pair = heapq.heappop(self.merge_heap)
        while pair == REMOVED:
            priority, counter, pair = heapq.heappop(self.merge_heap)
        self.entry_finder.pop(pair)
        return pair, priority

    def fit(self, corpus_path: str, k=1000):
        '''
        learning part of the byte-pair encoding here the model learns the 
        encoding convention which will later be used by the segmenter

        :param corpus_path: str - a path to a folder containing .txt files which will be used as corpus
        :param k: int - how many times do we want to merge adjacent tokens in the end the number of tokens will be k + number of distinct characters used in corpus 
        '''
        self.merge_heap = []
        self.occurences = defaultdict(lambda: None, {})
        p = Path(corpus_path)
        files = list(p.glob("*.txt"))
        text_num = 0
        for file in files:
            with open(str(file), "r", encoding="utf-8") as curr_file:
                text = curr_file.read()
                self._add_pairs(text, text_num)
                self.vocabulary = self.vocabulary | set(text)
            text_num += 1
        self.token_encoding = dict((j,i) for (i,j) in enumerate(self.vocabulary))

        print(self.token_encoding)

        print("Number of token pairs: ", len(self.occurences))
        print("number of occurences of each token pair")
        for k,v in self.occurences.items():
            print(f"k={k},len={len(v)}")
        print("Actual occurences counted")
        print(self.occurences)
        tmp_occ = dict()

        c = 0
        for k in self.occurences.keys():
            c += 1
            t1,t2 = k
            tmp_occ[(self.token_encoding[t1], self.token_encoding[t2])] = self.occurences[k]
        self.occurences = tmp_occ
        print("Number of token pairs: ", len(self.occurences))
        print("number of occurences of each token pair")
        for k,v in self.occurences.items():
            print(f"k={k},len={len(v)}")
        print("Actual occurences counted")
        print(self.occurences)

        for k in self.occurences.keys():
            self._push_pair(tokens=k, priority=-len(self.occurences[k]))
            if (k==(17,8) or k==(5,9) or k==(2,9)):
                self._push_pair(tokens=k, priority=-20)
        while self.merge_heap:
            tokens, priority = self._pop_pair()
            print(f"priority:{-priority}, tokens:{tokens}")

        

    def _add_pairs(self, text: str, text_number: int):
        '''
        takes text as input and updates the occurences dictionary

        :param text: str - text to be parsed
        :param text_number - which document it is
        '''
        for i in range(len(text)-1):
            if self.occurences[(text[i],text[i+1])] is None:
                self.occurences[(text[i],text[i+1])] = [(text_number, i)]
            else:
                self.occurences[text[i], text[i+1]].append((text_number,i))

