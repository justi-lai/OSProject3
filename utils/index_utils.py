from node_utils import Node_File
import os

NODE_SIZE = 512

class Index_File:
    def __init__(self, name):
        self.name = name
        self.file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'indexes', self.name)
        self.memory = [Node_File.read_header(Node_File(file_path=self.file).init_header())]
        self.clock = 0

    def read_from_file(self, location):
        with open(self.file, 'rb') as file:
            self.memory[self.clock] = Node_File.read_node(file, location)
        self.clock = (self.clock + 1) % 3
        return self.memory[self.clock]
    
    def read_from_location(self, location):
        return self.read_from_file(location * NODE_SIZE)

    def check_memory(self, field, value):
        for i in range(len(self.memory)):
            if self.memory[i][field] == value:
                return i
        return None

    def get_header(self):
        check = self.check_memory('header', True)
        if check is not None:
            return self.memory[check]
        else:
            header = self.read_from_file(0)
            return header


    def get_root(self):
        check = self.check_memory('parent_id', 0)
        if check is not None:
            return self.memory[check]
        else:
            header = self.get_header()
            root_location = int.from_bytes(header['root'], 'big')

