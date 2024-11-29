import node_utils as nu
import os

NODE_SIZE = 512

class Index_File:
    def __init__(self, name):
        self.name = name
        self.file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'indexes', self.name)
        self.memory = [nu.init_header(self.file), None, None]
        self.clock = 0
        self.use_bit = [0, 0, 0]

    def read_from_location(self, location):
        # clock policy
        for i in range(3):
            self.clock = (self.clock + 1) % 3
            if self.use_bit[self.clock] == 0:
                break
        
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
                if self.memory[i] is not None and self.memory[i]['block_id'] == location:
                    return i
        return None

    def check_memory_fv(self, field, value):
        for i in range(len(self.memory)):
            if self.memory[i][field] == value:
                return i
        return None
    
    def get_node(self, location):
        check = self.check_memory(location)
        if check is not None:
            self.use_bit[check] = 1
            return self.memory[check]
        else:
            return self.read_from_location(location)

    def get_node_fv(self, attribute, value, location):
        check = self.check_memory(attribute, value)
        if check is not None:
            self.use_bit[check] = 1
            return self.memory[check]
        else:
            return self.read_from_location(location)

    def get_header(self):
        return self.get_node(0)

    def get_root(self):
        header = self.get_header()
        root_id = header['root']
        return self.read_from_location(root_id)
    
    def add_node(self, parent_id, keys, values, children):
        header = self.get_header()
        next_node_id = header['next_node']
        for i in range(3):
            self.clock = (self.clock + 1) % 3
            if self.use_bit[self.clock] == 0:
                break
        self.memory[self.clock] = nu.init_node(self.file, next_node_id, parent_id, len(keys), keys, values, children)
        self.use_bit[self.clock] = 1
        nu.adjust_header(self.file, next_node_id=next_node_id + 1)
        return next_node_id
    
