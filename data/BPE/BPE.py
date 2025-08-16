import typing
from collections import Counter, defaultdict
import heapq
from pathlib import Path
from ..constants import REMOVED, SKIP
from ..helpers.DoublyLinkedList import Node, DoublyLinkedList
import json

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
        '''
        pricate function for pushing a pair of token ids onto the heap, if the pair is already on the heap then the previous entry is marked as removed and should be ignored later. (lazy deletion)

        :param tokens: tuple[int,int] - pair of token ids to add to the heap
        :param priority: int - priority of the token pair (we use a min heap for max heap behaviour negative priority values should be passed)
        '''
        if tokens in self.entry_finder:
            self._remove_pair(tokens)
        entry = [priority, self.counter, tokens]
        self.entry_finder[tokens] = entry
        heapq.heappush(self.merge_heap, entry)
        self.counter += 1

    def _remove_pair(self, tokens: tuple[int, int]):
        '''
        private function for marking a pair of tokens as removed

        :param tokens: tuple[int, int] - pair of token ids to be marked as removed
        :raise: raises ValueError if tokens passed as arguments are not on the heap
        '''
        if tokens not in self.entry_finder:
            raise ValueError("attempted removing tokens which are not in the entry_finder")
        entry = self.entry_finder.pop(tokens)
        entry[-1] = REMOVED
    
    def _pop_pair(self):
        '''
        private function for poping a top entry from the heap

        :raise: raises KeyError if the heap hasn't been initialized or if it's empty
        :return: pair, priority: tuple[int,int], int - top entry of the heap (skipping tiebreaker)
        '''
        if not self.merge_heap:
            raise KeyError("heap doesn't exist or is empty")
        priority, counter, pair = heapq.heappop(self.merge_heap)
        while pair == REMOVED:
            priority, counter, pair = heapq.heappop(self.merge_heap)
        self.entry_finder.pop(pair)
        return pair, priority

    def fit(self, corpus_path: str, t=10, verbose=0):
        '''
        learning part of the byte-pair encoding here the model learns the 
        encoding convention which will later be used by the segmenter

        :param corpus_path: str - a path to a folder containing .txt files which will be used as corpus
        :param t: int - how many times do we want to merge adjacent tokens in the end the number of tokens will be k + number of distinct characters used in corpus 
        :param verbose=0 : int - level of information printed in stdout
        '''
        self.merge_heap = []
        self.occurences = defaultdict(lambda: None, {})
        p = Path(corpus_path)
        files = list(p.glob("*.txt"))
        raw_texts = []
        text_num = 0
        for file in files:
            with open(str(file), "r", encoding="utf-8") as curr_file:
                text = curr_file.read()
                raw_texts.append(text)
                # self._add_pairs(text, text_num) #  updates occurences list
                self.vocabulary = self.vocabulary | set(text)
            text_num += 1
        self.token_encoding = dict((j,i) for (i,j) in enumerate(self.vocabulary))
        self.token_decoding = dict((self.token_encoding[i],i) for i in self.token_encoding)

        encoded_texts = []
        for i in range(len(raw_texts)):
            curr_text = DoublyLinkedList()
            for c in range(len(raw_texts[i])):
                curr_text.add(self.token_encoding[raw_texts[i][c]])
            self._update_occurences_dict(curr_text, i)
            encoded_texts.append(curr_text)
        if verbose > 0:
            print(self.token_encoding)
            for text in encoded_texts:
                print(text)
            for k,v in self.occurences.items():
                print(f"k:{k},v:{v}")
        
        if verbose > 0:
            print("Number of token pairs: ", len(self.occurences))
            print("number of occurences of each token pair")
            for k,v in sorted(self.occurences.items(), key=lambda x: len(x[1]), reverse=True):
                print(f"k={k},len={len(v)}")
        
        for k in self.occurences.keys():
            self._push_pair(tokens=k, priority=-len(self.occurences[k]))
        
        new_id = max(self.token_encoding.values()) + 1
        to_add = set()
        if verbose > 0:
            print("========TRAINING LOOP=================")
        for i in range(t):
            if verbose > 0:
                print(f"\n\n\nITERATION NUMBER:{i}\n\n\n")
            # print("number of occurences of each token pair")
            # for (k1,k2),v in sorted(self.occurences.items(), key=lambda x: len(x[1]), reverse=True):
            #     print(f"k=({self.token_decoding[k1], self.token_decoding[k2]}),len={len(v)}")
            # print(self.token_encoding)
            # for i in range(len(encoded_texts)):
            #     print(f"{i}th text")
            #     print("========RAW TEXT=============")
            #     print(raw_texts[i])
            #     print("========ENCODED TEXT=============")
            #     print(encoded_texts[i])
            to_add.clear()
            (t1,t2),_ = self._pop_pair()
            # print(f"TOKENS TO MERGE: {t1},{t2}: \'{self.token_decoding[t1]}\',\'{self.token_decoding[t2]}\'")
            new_token = self.token_decoding[t1] + self.token_decoding[t2]
            self.token_encoding[new_token] = new_id
            self.token_decoding[new_id] = new_token
            self.merges[(t1,t2)] = new_id
            self.vocabulary.add(new_token)
            new_id += 1
            for occurence in self.occurences[(t1,t2)]:
                doc_idx, curr_node = occurence
                # print(f"OCCURENCE: {occurence}")
                # 1. look right
                # 1.1. add new pairs
                # 1.2. remove old pairs
                # 2. look left
                # 2.1. add new pairs
                # 2.2. remove old pairs
                # 3. update heap
                # 4. update encoded_texts
                
                # look right
                if curr_node.next.next is not None:
                    if self.occurences[(new_id-1, curr_node.next.next.value)] is None:
                        self.occurences[(new_id-1, curr_node.next.next.value)] = [(doc_idx, curr_node)]
                    else:
                        self.occurences[(new_id-1, curr_node.next.next.value)].append((doc_idx, curr_node))
                    to_add.add((new_id-1, curr_node.next.next.value))
                    self.occurences[(curr_node.next.value, curr_node.next.next.value)].remove((doc_idx, curr_node.next))
                    to_add.add((curr_node.next.value, curr_node.next.next.value))
                
                # look left
                if curr_node.prev is not None:
                    if self.occurences[(curr_node.prev.value, new_id-1)] is None:
                        self.occurences[(curr_node.prev.value, new_id-1)] = [(doc_idx, curr_node.prev)]
                    else:
                        self.occurences[(curr_node.prev.value, new_id-1)].append((doc_idx, curr_node.prev))
                    to_add.add((curr_node.prev.value, new_id-1))
                    self.occurences[(curr_node.prev.value, curr_node.value)].remove((doc_idx, curr_node.prev))
                    to_add.add((curr_node.prev.value, curr_node.value))
                # to do add updating encoded texts
                curr_node.value = new_id - 1
                encoded_texts[doc_idx].remove(curr_node.next)
            self.occurences.pop((t1,t2))
            for pair in to_add:
                self._push_pair(pair, -len(self.occurences[pair]))
        # print("number of occurences of each token pair")
        # for (k1,k2),v in sorted(self.occurences.items(), key=lambda x: len(x[1]), reverse=True):
        #     print(f"k=({self.token_decoding[k1], self.token_decoding[k2]}),len={len(v)}")
        if verbose > 0:
            print(self.token_encoding)
            for i in range(len(encoded_texts)):
                print(f"{i}th text")
                print("========RAW TEXT=============")
                print(raw_texts[i])
                print("========ENCODED TEXT=============")
                print(encoded_texts[i])
            for k,v in self.merges.items():
                print(f"k:{k}-->v:{v}")
            for k,v in self.merges.items():
                print(f"k:(\'{self.token_decoding[k[0]]}\', \'{self.token_decoding[k[1]]}\')-->v:\'{self.token_decoding[v]}\'")
    
    def _update_occurences_dict(self, encoded_text: DoublyLinkedList, text_number: int):
        '''
        takes encoded text as input and updates the occurences dictionary

        :param encoded_text: DoublyLinkedList - encoded text
        :param text_number - which document is it

        '''
        curr = encoded_text.root
        while curr != encoded_text.tail:
            if self.occurences[(curr.value, curr.next.value)] is None:
                self.occurences[(curr.value, curr.next.value)] = [(text_number, curr)]
            else:
                self.occurences[(curr.value, curr.next.value)].append((text_number, curr))
            curr = curr.next


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
    
    def save_dicts_as_JSON(self, json_path: str):
        '''
        saves the following dictionaries as a json file in the specified location
        dictionaries saved:
        - merges - which tokens merge with which and what tokens result from that
        - token_encoding - mappings from str to token ids
        - token_decoding - mappings from token ids to str

        :param json_path: str - location where to save the json file (relative path)
        '''
        save_dict = {
            "merges" : list(dict(self.merges).items()),
            "token_encoding" : list(dict(self.token_encoding).items()),
            "token_decoding" : list(dict(self.token_decoding).items())
        }
        with open(json_path, "w") as json_f:
            json.dump(save_dict, json_f)
    
    def load_dicts_as_JSON(self, json_path: str):
        '''
        loads dictionaries previously saved with save_dicts_as_JSON
        dictionaries loaded:
        - merges - which tokens merge with which and what tokens result from that
        - token_encoding - mappings from str to token ids
        - token_decoding - mappings from token ids to str

        :param json_path : str - location where the json file is saved (relative path)
        '''
        with open(json_path, "r") as json_f:
            dicts = json.load(json_f)
        merges_tmp = {tuple(k): v for k, v in dicts["merges"]}
        self.token_decoding = {int(k): v for k, v in dicts["token_decoding"]}
        self.token_encoding = {k: int(v) for k, v in dicts["token_encoding"]}
        self.merges = defaultdict(lambda: None, merges_tmp)
        self.vocabulary = {k for k in self.token_encoding.keys()}
    
    def transform(self, text: str) -> list[int]:
        '''
        Transforms input data using saved dictionaries from the .fit()

        :param text : str - text to be transformed
        :return encoded_text : list[int] - list of token ids
        '''
        encoded_text = []
        encoded_text.append(self.token_encoding[text[0]])
        for c in text[1:]:
            c_id = self.token_encoding[c]
            i = len(encoded_text)
            while i > 0 and (encoded_text[i-1], c_id) in self.merges.keys():
                t = encoded_text.pop()
                c_id = self.merges[(t, c_id)]
                i -= 1
            encoded_text.append(c_id)
        return encoded_text