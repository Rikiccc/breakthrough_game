class Node(object):
    def __init__(self,element,next=None,prev=None):
        self.element = element
        self.next = next
        self.prev = prev
class DoubleList(object):
    def __init__(self):
        self.head = self.tail = None
    def add(self,v):
        newest = Node(v)
        if not self.head:
            self.head = self.tail = newest
        else:
            self.tail.next = newest
            newest.prev = self.tail
            self.tail = newest
    def remove(self,v):
        current = self.head
        while current:
            if current.element == v:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                return True
            current = current.next
        return False
    def __iter__(self):
        current = self.head
        while current:
            yield current.element
            current = current.next
    def to_list(self):
        return [v for v in self]