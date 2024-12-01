import utils.node_utils as nu
import os

NODE_SIZE = 512

class Index_File:
    def __init__(self, name):
        self.name = name
        self.file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'indexes', self.name)
        self.memory = [nu.init_header(self.file), None, None]
        self.clock = 0
        self.use_bit = [1, 0, 0]

    def clock_policy(self):
        for i in range(3):
            self.use_bit[self.clock] = 0
            self.clock = (self.clock + 1) % 3
            if self.use_bit[self.clock] == 0:
                break

    def read_from_location(self, location):
        check = self.check_memory(location)
        if check is not None:
            self.use_bit[check] = 1
            return self.memory[check]
        
        # clock policy
        self.clock_policy()
        
        # writing to file from memory
        if self.memory[self.clock] is not None:
            nu.overwrite_node(self.file, self.memory[self.clock])

        # reading from file into memory as a dictionary
        self.memory[self.clock] = nu.read_node(self.file, location)
        return self.memory[self.clock]
            
    def check_memory(self, location):
        if location == 0:
            for i in range(len(self.memory)):
                if self.memory[i] is not None and self.memory[i]['header']:
                    return i
        else:
            for i in range(len(self.memory)):
                if self.memory[i] is not None and not self.memory[i]['header'] and self.memory[i]['block_id'] == location:
                    return i
        return None

    def check_memory_fv(self, field, value):
        for i in range(len(self.memory)):
            if self.memory[i][field] == value:
                return i
        return None
    
    def get_node(self, location):
        return self.read_from_location(location)

    def get_node_fv(self, attribute, value, location):
        check = self.check_memory_fv(attribute, value)
        if check is not None:
            self.use_bit[check] = 1
            return self.memory[check]
        else:
            return self.read_from_location(location)

    def get_header(self):
        return self.get_node(0)

    def get_root(self):
        header = self.get_header()
        if header['root'] == 0:
            return None
        root_id = header['root']
        return self.read_from_location(root_id)
    
    def add_node(self, parent_id, keys, values, children):
        header = self.get_header()
        next_node_id = header['next_node']
        self.clock_policy()

        if self.memory[self.clock] is not None:
            nu.overwrite_node(self.file, self.memory[self.clock])
        self.memory[self.clock] = nu.init_node(self.file, next_node_id, parent_id, len(keys), keys, values, children)
        self.use_bit[self.clock] = 1
        self.adjust_header(next_node=next_node_id + 1)
        return next_node_id
    
    def adjust_header(self, root=None, next_node=None):
        header = self.get_header()
        if root is not None:
            nu.adjust_header(self.file, root=root)
            header['root'] = root
        if next_node is not None:
            nu.adjust_header(self.file, next_node_id=next_node)
            header['next_node'] = next_node

    def adjust_node(self, block_id, parent_id=None, num_keys=None, keys=None, values=None, children=None):
        node = self.get_node(block_id)
        if parent_id is not None:
            nu.adjust_node(self.file, block_id, parent_id=parent_id)
            node['parent_id'] = parent_id
        if num_keys is not None:
            nu.adjust_node(self.file, block_id, num_keys=num_keys)
            node['num_keys'] = num_keys
        if keys is not None:
            nu.adjust_node(self.file, block_id, keys=keys)
            node['keys'] = keys
        if values is not None:
            nu.adjust_node(self.file, block_id, values=values)
            node['values'] = values
        if children is not None:
            nu.adjust_node(self.file, block_id, children=children)
            node['children'] = children