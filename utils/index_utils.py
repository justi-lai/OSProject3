import utils.node_utils as nu
import os

NODE_SIZE = 512
MEMORY_SIZE = 3

class Index_File:
    def __init__(self, name):
        self.name = name
        self.file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'indexes', self.name)
        self.memory = [None] * MEMORY_SIZE
        self.clock = 0
        self.use_bit = [1, 0, 0]

    def _clock_policy(self):
        while True:
            if self.use_bit[self.clock] == 0:
                return self.clock
            self.use_bit[self.clock] = 0
            self.clock = (self.clock + 1) % MEMORY_SIZE

    def _write_to_file(self, node):
        nu.overwrite_node(self.file, node)

    def _load_from_file(self, block_id):
        nu.read_node(self.file, block_id)

    def get_node(self, block_id):
        for i in range(MEMORY_SIZE):
            if self.memory[i] is not None and self.memory[i]['block_id'] == block_id:
                self.use_bit[i] = 1
                return self.memory[i]
            
        index = self._clock_policy()

        if self.memory[index] is not None:
            self._write_to_file(self.memory[index])

        self.memory[index] = self._load_from_file(block_id)
        self.use_bit[index] = 1
        return self.memory[index]

    def add_node(self, parent_id, keys, values, children):
        header = self.get_header()
        next_node_id = header['next_node']

        index = self._clock_policy()

        if self.memory[index] is not None:
            self._write_to_file(self.memory[index])
        
        self.memory[index] = nu.init_node(self.file, next_node_id, parent_id, len(keys), keys, values, children)
        self.use_bit[index] = 1
        header['next_node'] += 1
        self.get_header()
        nu.adjust_header(self.file, next_node_id=header['next_node'])
        return next_node_id

    def adjust_node(self, block_id, parent_id=None, num_keys=None, keys=None, values=None, children=None):
        self.get_node(block_id)
        nu.adjust_node(self.file, block_id, parent_id, num_keys, keys, values, children)
        return

    def get_header(self):
        return self.get_node(0)

    def get_root(self):
        header = self.get_header()
        return self.get_node(header['root'])