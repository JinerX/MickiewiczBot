
class Node:
    def __init__(self, val):
        self.value = val
        self.prev = None
        self.next = None
    
    def __str__(self):
        ret_str = "Node(" + str(self.value) + ")"
        return ret_str
    __repr__ = __str__

class DoublyLinkedList:
    def __init__(self):
        self.root=None
        self.tail=None
        self.curr = self.root
    
    def reset_curr(self):
        self.curr = self.root
        return self.curr
    
    def next(self):
        if self.curr == self.tail:
            raise KeyError("Curr already points at the last value")
        self.curr = self.curr.next
        return self.curr
    
    def prev(self):
        if self.curr == self.head:
            raise KeyError("Curr already points at the first value")
        self.curr = self.curr.prev
        return self.curr
    
    def get_curr(self):
        return self.curr
    
    def add(self, value):
        if self.root == None:
            self.root = Node(value)
            self.tail = self.root
            return
        tmp = Node(value)
        self.tail.next = tmp
        tmp.prev = self.tail
        self.tail = tmp
    
    def pop(self):
        if self.tail == self.root:
            tmp = self.tail
            self.root = self.tail = None
            return tmp
        
        tmp = self.tail
        tmp.prev.next = None
        self.tail = tmp.prev
        return tmp
    
    def remove(self, node):
        tmp_p = node.prev
        tmp_n = node.next
        if tmp_p is not None:
            tmp_p.next = tmp_n
        else:
            if node != self.root:
                raise ValueError("Node passed has no prev and is not a root impossible")
            self.root = tmp_n
        if tmp_n is not None:
            tmp_n.prev = tmp_p
        else:
            if node != self.tail:
                raise ValueError("Node passed has no next and is not a tail impossible")
            self.tail = tmp_p
        del node
    
    def __str__(self):
        ret_str = "DoublyLinkedList("
        tmp = self.root
        while tmp is not None:
            ret_str = ret_str + str(tmp.value) + ", "
            tmp = tmp.next
        ret_str = ret_str + ")"
        return ret_str

