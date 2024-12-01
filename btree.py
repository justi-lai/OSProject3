import utils.node_utils as nu
import os

MEMORY_SIZE = 3

class BTreeNode:
    def __init__(self, btree, block_id, degree, is_leaf=True):
        """
        Represents a single node in the B-tree.
        """
        self.btree = btree  # Reference to the parent BTree
        self.block_id = block_id  # Block ID of this node
        self.degree = degree  # Minimum degree
        self.is_leaf = is_leaf
        self.num_keys = 0
        self.keys = []
        self.values = []
        self.children = []
        self.parent_id = 0

    def load_from_file(self):
        """
        Loads node data from file into memory.
        """
        data = nu.read_node(self.btree.file_name, self.block_id)
        self.num_keys = data['num_keys']
        self.keys = data['keys']
        self.values = data['values']
        self.children = data['children']
        self.parent_id = data['parent_id']
        self.is_leaf = self.children == []

    def save_to_file(self):
        """
        Saves node data to file.
        """
        node_data = {
            'block_id': self.block_id,
            'parent_id': self.parent_id,
            'num_keys': self.num_keys,
            'keys': self.keys,
            'values': self.values,
            'children': self.children,
        }
        self.btree.save_node(node_data)

    def is_full(self):
        """
        Checks if the node is full.
        """
        return self.num_keys == 2 * self.degree - 1

    def split(self, parent, index):
        """
        Splits the node and updates the parent without exceeding the memory limit.
        """
        degree = self.degree
        btree = self.btree

        # Get a new block ID for the split node
        new_child_id = btree.get_next_block_id()

        # Create and write the new child directly to the file
        new_keys = self.keys[degree:]  # Right half of keys
        new_values = self.values[degree:]
        new_children = self.children[degree:] if not self.is_leaf else []

        # Save the new child node directly to file
        new_child_data = {
            'block_id': new_child_id,
            'parent_id': parent.block_id,
            'num_keys': len(new_keys),
            'keys': new_keys,
            'values': new_values,
            'children': new_children
        }
        btree.save_node(new_child_data)

        # Update the current node (left half of keys and children)
        self.keys = self.keys[:degree - 1]
        self.values = self.values[:degree - 1]
        self.children = self.children[:degree] if not self.is_leaf else []
        self.num_keys = len(self.keys)

        # Update the parent node
        parent.children.insert(index + 1, new_child_id)
        parent.keys.insert(index, new_keys[0])  # Middle key is promoted
        parent.values.insert(index, new_values[0])
        parent.num_keys += 1

        # Save the updated nodes
        self.save_to_file()
        parent.save_to_file()

    def insert_non_full(self, key, value):
        """
        Inserts a key into a non-full node.
        """
        i = self.num_keys - 1

        if self.is_leaf:
            # Shift keys to insert the new key
            self.keys.append(0)  # Expand keys list
            self.values.append(0)  # Expand values list
            while i >= 0 and key < self.keys[i]:
                self.keys[i + 1] = self.keys[i]
                self.values[i + 1] = self.values[i]
                i -= 1
            self.keys[i + 1] = key
            self.values[i + 1] = value
            self.num_keys += 1
            self.save_to_file()
        else:
            # Find child to insert into
            while i >= 0 and key < self.keys[i]:
                i -= 1
            i += 1

            # Load child and check if it needs splitting
            child = self.btree.load_node(self.children[i])
            if child.is_full():
                self.split(self, i)
                if key > self.keys[i]:
                    i += 1

            child = self.btree.load_node(self.children[i])
            child.insert_non_full(key)

class BTree:
    def __init__(self, degree, file_name):
        """
        Represents the B-tree itself.
        """
        self.degree = degree  # Minimum degree
        self.file_name = os.path.join(os.path.dirname(__file__), 'indexes', file_name)  # File path for storing nodes
        self.root_id = 0  # Root block ID
        self.memory = [None, None, None]  # In-memory nodes (including header)
        self.use_bits = [0, 0, 0]  # Clock replacement use bits
        self.clock_pointer = 0

        # Initialize header in file if it doesn't exist
        if not os.path.exists(self.file_name):
            self.header = nu.init_header(file_name)
        else:
            self.header = None  # Header will be loaded when accessed

    def _load_header(self):
        """
        Ensure the header is in memory and return it.
        """
        if self.header:
            return self.header

        # Check if the header is already in memory
        for i, node in enumerate(self.memory):
            if node and node.get('header', False):
                self.use_bits[i] = 1
                self.header = node
                return node

        # Load header using the clock replacement policy
        header = self.load_node(0)  # Assuming block_id=0 is the header
        self.header = header
        return header

    def load_node(self, block_id):
        """
        Ensures a node is in memory using the clock replacement policy.
        """
        # Check if the node is already in memory
        for i, node in enumerate(self.memory):
            if node and node.get('block_id') == block_id:
                self.use_bits[i] = 1
                return node

        # Apply clock replacement policy to evict a node
        while True:
            if self.use_bits[self.clock_pointer] == 0:
                # Write the evicted node to file if necessary
                if self.memory[self.clock_pointer]:
                    nu.overwrite_node(self.file_name, self.memory[self.clock_pointer])

                # Load the new node into the memory slot
                node = BTreeNode(self, block_id, self.degree).load_from_file()
                self.memory[self.clock_pointer] = node
                self.use_bits[self.clock_pointer] = 1  # Mark as recently used
                return self.memory[self.clock_pointer]

            # Advance the clock pointer
            self.use_bits[self.clock_pointer] = 0
            self.clock_pointer = (self.clock_pointer + 1) % MEMORY_SIZE

    def save_node(self, node_data):
        """
        Saves a node to the file.
        """
        block_id = node_data['block_id']
        nu.overwrite_node(self.file_name, node_data)

        # Update the node in memory if it's already loaded
        for i, node in enumerate(self.memory):
            if node and node.get('block_id') == block_id:
                self.memory[i] = node_data
                return

    def get_next_block_id(self):
        """
        Get the next block ID and update the header.
        """
        header = self._load_header()
        next_id = header['next_node']
        header['next_node'] += 1
        nu.adjust_header(self.file_name, next_node_id=header['next_node'])
        return next_id

    def get_root_id(self):
        """
        Get the root ID from the header.
        """
        return self._load_header()['root']

    def update_root(self, root_id):
        """
        Update the root ID in the header.
        """
        header = self._load_header()
        header['root'] = root_id
        nu.adjust_header(self.file_name, root=root_id)

    def insert(self, key, value):
        """
        Insert a key-value pair into the B-tree.
        """
        try:
            root = self.load_node(self.get_root_id())
        except FileNotFoundError:
            # Create a new root node if it doesn't exist
            root_id = self.get_next_block_id()
            root = BTreeNode(self, root_id, self.degree, is_leaf=True)
            root.keys.append(key)
            root.values.append(value)
            root.num_keys = 1
            root.save_to_file()
            self.update_root(root_id)
            return

        if root.num_keys == 2 * self.degree - 1:  # If root is full
            new_root_id = self.get_next_block_id()
            new_root = BTreeNode(self, new_root_id, self.degree, is_leaf=False)
            new_root.children.append(self.root_id)

            # Split the old root and make the new root the parent
            root.split(new_root, 0)

            self.update_root(new_root_id)
            root = new_root

        root.insert_non_full(key, value)

    def split(self, parent, index):
        """
        Split the node and update the parent, handling keys and values together.
        """
        degree = self.degree
        btree = self.btree

        new_child_id = btree.get_next_block_id()

        new_keys = self.keys[degree:]
        new_values = self.values[degree:]
        new_children = self.children[degree:] if not self.is_leaf else []

        new_child_data = {
            'block_id': new_child_id,
            'num_keys': len(new_keys),
            'keys': new_keys,
            'values': new_values,
            'children': new_children,
            'parent_id': parent.block_id,
            'is_leaf': self.is_leaf,
        }
        btree.save_node(new_child_data)

        self.keys = self.keys[:degree - 1]
        self.values = self.values[:degree - 1]
        self.children = self.children[:degree] if not self.is_leaf else []
        self.num_keys = len(self.keys)

        parent.children.insert(index + 1, new_child_id)
        parent.keys.insert(index, new_keys[0])
        parent.values.insert(index, new_values[0])
        parent.num_keys += 1

        self.save_to_file()
        parent.save_to_file()

    def insert_non_full(self, key, value):
        """
        Insert a key-value pair into a non-full node.
        """
        i = self.num_keys - 1  # Start from the last key

        if self.is_leaf:
            # Insert key and value into the correct position in the leaf node
            self.keys.append(0)  # Expand the keys list
            self.values.append(0)  # Expand the values list

            while i >= 0 and key < self.keys[i]:
                self.keys[i + 1] = self.keys[i]
                self.values[i + 1] = self.values[i]
                i -= 1

            self.keys[i + 1] = key
            self.values[i + 1] = value
            self.num_keys += 1
            self.save_to_file()
        else:
            while i >= 0 and key < self.keys[i]:
                i -= 1
            i += 1

            child = self.btree.load_node_in_memory(self.children[i])

            if child.num_keys == 2 * self.degree - 1:
                self.split(self, i)
                if key > self.keys[i]:
                    i += 1

            child = self.btree.load_node_in_memory(self.children[i])
            child.insert_non_full(key, value)

def main():
    # Create a B-tree with degree 2 (minimum degree)
    degree = 2
    file_name = "btree_data.dat"
    
    # Initialize the B-tree
    btree = BTree(degree, file_name)
    
    # Insert key-value pairs
    print("Inserting key-value pairs into the B-tree:")
    key_value_pairs = [
        (10, 100),
        (20, 200),
        (5, 50),
        (6, 60),
        (12, 120),
        (30, 300),
        (7, 70),
        (17, 170)
    ]

    for key, value in key_value_pairs:
        print(f"Inserting: Key={key}, Value={value}")
        btree.insert(key, value)
    
    # Verify traversal and structure
    print("\nTraversing the B-tree:")
    traversal_result = traverse_btree(btree)
    for key, value in traversal_result:
        print(f"Key={key}, Value={value}")

    # Display the structure of the B-tree
    print("\nB-tree structure (nodes loaded in memory):")
    display_btree_structure(btree)

def traverse_btree(btree):
    """
    Traverse the B-tree and return all keys and values in sorted order.
    """
    def traverse_node(node):
        result = []
        for i in range(node.num_keys):
            if not node.is_leaf:
                child = btree.load_node_in_memory(node.children[i])
                result.extend(traverse_node(child))
            result.append((node.keys[i], node.values[i]))
        if not node.is_leaf:
            child = btree.load_node_in_memory(node.children[node.num_keys])
            result.extend(traverse_node(child))
        return result
    
    root = btree.load_node_in_memory(btree.get_root_id())
    return traverse_node(root)

def display_btree_structure(btree):
    """
    Display the structure of the B-tree by traversing nodes in memory.
    """
    def display_node(node, level=0):
        print("  " * level + f"Node (Block ID={node.block_id}):")
        print("  " * level + f"  Keys: {node.keys[:node.num_keys]}")
        print("  " * level + f"  Values: {node.values[:node.num_keys]}")
        print("  " * level + f"  Children: {node.children[:node.num_keys + 1]}")
        for i in range(node.num_keys + 1):
            if not node.is_leaf and node.children[i] != 0:
                child = btree.load_node_in_memory(node.children[i])
                display_node(child, level + 1)
    
    root = btree.load_node_in_memory(btree.get_root_id())
    display_node(root)

if __name__ == "__main__":
    main()