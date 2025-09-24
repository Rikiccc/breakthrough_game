class TreeNode(object):
    def __init__(self, element = None, parent = None):
        self.element = element
        self.parent = parent
        self.children = []
        self.ocena = None   
    def is_root(self):
        return self.parent == None
    def is_leaf(self):
        return len(self.children) == 0

class Tree(object):
    def __init__(self):
        self.root = None
    def depth(self,node):
        if node.parent is None:
            return 0
        else:
            return 1 + self.depth(node.parent)
    def preorder(self,node,func):
        func(node)
        for child in node.children:
            self.preorder(child,func)
    def postorder(self,node,func):
        for child in node.children:
            self.postorder(child,func)
        func(node)