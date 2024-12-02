import utils.node_utils as nu
import os
import csv

MEMORY_SIZE = 3

class Node:
    def __init__(self, file_path, block_id=None):
        self.file_path = file_path
        self.block_id = block_id

    def load(self, block_id):
        pass
    
    def save(self):
        pass

class HeaderNode(Node):
    def __init__(self, file_path, root=None, next_node=None):
        super().__init__(file_path, 0)
        self.root = root
        self.next_node = next_node
    
    def load(self):
        data = nu.read_node(self.file_path, 0)
        self.root = data['root']
        self.next_node = data['next_node']

    def save(self):
        nu.adjust_header(self.file_path, self.root, self.next_node)

class BTreeNode(Node):
    def __init__(self, file_path, block_id=None, leaf=False):
        super().__init__(file_path)
        if block_id is not None:
            self.load(block_id)
        else:
            self.leaf = leaf
            self.parent_id = None
            self.num_keys = 0
            self.keys = []
            self.values = []
            self.children = []

    def load(self, block_id):
        data = nu.read_node(self.file_path, block_id)
        self.leaf = True if data['children'] == [] else False
        self.block_id = data['block_id']
        self.parent_id = data['parent_id']
        self.num_keys = data['num_keys']
        self.keys = data['keys']
        self.values = data['values']
        self.children = data['children']
    
    def save(self):
        if self.block_id is None:
            self.block_id = nu.get_next_node_id(self.file_path)
            nu.init_node(self.file_path, self.block_id, self.parent_id, self.num_keys, self.keys, self.values, self.children)
        else:
            nu.adjust_node(self.file_path, self.block_id, self.parent_id, self.num_keys, self.keys, self.values, self.children)
    
class BTree:
    def __init__(self, file_name, degree):
        self.file_name = file_name
        self.file_path = os.path.join(os.path.dirname(__file__), 'indexes', self.file_name)
        self.degree = degree
        self.memory = [None] * MEMORY_SIZE
        self.clock = 0
        self.use_bit = [0] * MEMORY_SIZE
        self._init_header()
    
    def _clock_policy(self):
        while True:
            if self.use_bit[self.clock] == 0:
                return self.clock
            self.use_bit[self.clock] = 0
            self.clock = (self.clock + 1) % MEMORY_SIZE
    
    def _in_memory(self, block_id):
        for i in range(MEMORY_SIZE):
            if self.memory[i] is not None and self.memory[i].block_id == block_id:
                self.use_bit[i] = 1
                return i
        return -1
    
    def _attain_all_memory(self, *block_ids):
        if len(block_ids) > MEMORY_SIZE:
            raise ValueError("Too many block ids")
        
        for i in range(MEMORY_SIZE):
            if self.memory[i] is not None:
                self._write_to_file(self.memory[i])
                self.memory[i] = None
                self.use_bit[i] = 0
        
        self.clock = 0
        for block_id in block_ids:
            if self.memory[self.clock] is not None:
                self._write_to_file(self.memory[self.clock])
            if block_id == 0:
                self.memory[self.clock] = self._load_header_from_file()
            else:
                self.memory[self.clock] = self._load_from_file(block_id)
            self.use_bit[self.clock] = 1
            self.clock = (self.clock + 1) % MEMORY_SIZE

    def _write_to_file(self, node):
        node.save()
    
    def _load_from_file(self, block_id):
        file = BTreeNode(self.file_path, block_id)
        return file
    
    def _load_header_from_file(self):
        file = HeaderNode(self.file_path)
        file.load()
        return file

    def _init_header(self):
        if nu.has_header(self.file_path):
            self._clock_policy()
            self.memory[self.clock] = HeaderNode(self.file_path)
            self.memory[self.clock].load()
        else:
            nu.init_header(self.file_path)
            self._clock_policy()
            self.memory[self.clock] = HeaderNode(self.file_path)
            self.memory[self.clock].load()
    
    def get_header(self):
        index = self._in_memory(0)
        if index != -1:
            return self.memory[index]
        
        index = self._clock_policy()

        if self.memory[index] is not None:
            self._write_to_file(self.memory[index])
        
        self.memory[index] = HeaderNode(self.file_path)
        self.memory[index].load()
        self.use_bit[index] = 1
        return self.memory[index]
    
    def get_node(self, block_id):
        index = self._in_memory(block_id)
        if index != -1:
            return self.memory[index]
        
        index = self._clock_policy()

        if self.memory[index] is not None:
            self._write_to_file(self.memory[index])

        self.memory[index] = self._load_from_file(block_id)
        self.use_bit[index] = 1
        return self.memory[index]
    
    def add_node(self, parent_id, keys, values, children):
        header = self.get_header()
        next_node_id = header.next_node

        index = self._clock_policy()

        if self.memory[index] is not None:
            self._write_to_file(self.memory[index])
        
        leaf = True if children == [] else False
        
        self.memory[index] = BTreeNode(self.file_path, leaf=leaf)
        self.memory[index].parent_id = parent_id
        self.memory[index].num_keys = len(keys)
        self.memory[index].keys = keys
        self.memory[index].values = values
        self.memory[index].children = children
        self.memory[index].save()
        self.use_bit[index] = 1
        new_next_node = next_node_id + 1
        header = self.get_header()
        header.next_node = new_next_node
        nu.adjust_header(self.file_path, next_node_id=new_next_node)
        return next_node_id
    
    def adjust_node(self, block_id, parent_id=None, num_keys=None, keys=None, values=None, children=None):
        node = self.get_node(block_id)
        if parent_id is not None:
            node.parent_id = parent_id
        if num_keys is not None:
            node.num_keys = num_keys
        if keys is not None:
            node.keys = keys
        if values is not None:
            node.values = values
        if children is not None:
            node.children = children
            node.leaf = True if children == [] else False
        node.save()
        return
    
    def get_root(self):
        return self.get_node(self.get_header().root)
    
    def set_root(self, root):
        header = self.get_header()
        header.root = root
        header.save()

    def load(self, file_path):
        with open(file_path, 'r') as file:
            csv_file = csv.reader(file)
            for row in csv_file:
                if not row or len(row) <2:
                    continue
                try:
                    search = self.search_key(int(row[0]))
                    if search is None:
                        self.insert(int(row[0]), int(row[1]))
                        print(f"{row[0]}:{row[1]} inserted.")
                    else:
                        print(f"Key {row[0]} already exists.")
                except ValueError:
                    continue
    
    def _extract_helper(self, node, csv_file):
        node_id = node.block_id
        node = self.get_node(node.block_id)
        if node.leaf:
            for i in range(node.num_keys):
                csv_file.writerow([node.keys[i], node.values[i]])
        else:
            i = 0
            while i < node.num_keys:
                self._extract_helper(self.get_node(node.children[i]), csv_file)
                node = self.get_node(node_id)
                csv_file.writerow([node.keys[i], node.values[i]])
                i += 1
            if i < len(node.children):
                self._extract_helper(self.get_node(node.children[i]), csv_file)

    def extract(self, file_path):
        with open(file_path, 'w') as file:
            csv_file = csv.writer(file)
            root = self.get_root()
            self._extract_helper(root, csv_file)    
    
    def split_child(self, parent_id, child_index):
        degree = self.degree
        child_id = self.get_node(parent_id).children[child_index]
        child2_id = self.add_node(parent_id, [], [], [])
        self._attain_all_memory(parent_id, child_id, child2_id)

        parent = self.memory[0]
        child1 = self.memory[1]
        child2 = self.memory[2]

        parent.children.insert(child_index + 1, child2_id)
        parent.keys.insert(child_index, child1.keys[degree - 1])
        parent.values.insert(child_index, child1.values[degree - 1])
        child2.keys = child1.keys[degree:]
        child2.values = child1.values[degree:]
        child1.keys = child1.keys[:degree - 1]
        child1.values = child1.values[:degree - 1]
        parent.num_keys = len(parent.keys)
        child1.num_keys = len(child1.keys)
        child2.num_keys = len(child2.keys)
        if not child1.leaf:
            child2.children = child1.children[degree:]
            child1.children = child1.children[:degree]
            child2.leaf = False
        child1.save()
        child2.save()
        parent.save()
    
    def insert_non_full(self, block_id, key, value):
        node = self.get_node(block_id)
        i = node.num_keys - 1
        if node.leaf:
            node.keys.append(None)
            node.values.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            node.keys[i + 1] = key
            node.values[i + 1] = value
            node.num_keys += 1
            node.save()
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            child = self.get_node(node.children[i])
            if child.num_keys == 2 * self.degree - 1:
                self.split_child(block_id, i)
                node = self.get_node(block_id)
                if key > node.keys[i]:
                    i += 1
            node.save()
            self.insert_non_full(node.children[i], key, value)
    
    def insert(self, key, value):
        header = self.get_header()
        if header.root == 0:
            root = self.add_node(0, [key], [value], [])
            self.set_root(root)
        else:
            root = self.get_root()
            root_id = root.block_id
            if root.num_keys == 2 * self.degree - 1:
                new_root = self.add_node(0, [], [], [root.block_id])
                self.adjust_node(root_id, parent_id=new_root)
                self.set_root(new_root)
                self.split_child(new_root, 0)
                self.get_root()
                self.insert_non_full(new_root, key, value)
            else:
                self.insert_non_full(root_id, key, value)
    
    def search_key(self, key, block_id=None):
        if block_id is None:
            block_id = self.get_header().root
        if block_id == 0:
            return None
        node = self.get_node(block_id)
        i = 0
        while i < node.num_keys and key > node.keys[i]:
            i += 1
        if i < node.num_keys and key == node.keys[i]:
            return node.values[i]
        if node.leaf:
            return None
        return self.search_key(key, node.children[i])
        
    
    def _print_tree(self, block_id, level):
        if block_id == 0:
            print("Empty tree...")
            return
        node = self.get_node(block_id)
        print("Block", block_id, " ||  Level", level, ":", node.keys, node.values, " ||  Children:", node.children)
        if not node.leaf:
            for child in node.children:
                self._print_tree(child, level + 1)

    def print_tree(self):
        self._print_tree(self.get_root().block_id, 0)

    def close(self):
        for i in range(MEMORY_SIZE):
            if self.memory[i] is not None:
                self._write_to_file(self.memory[i])
        return