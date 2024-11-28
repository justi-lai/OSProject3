MAGIC_NUMBER = "4337PRJ3"
NODE_SIZE = 512

class Node_File:
    def __init__(self, location=0, file_path=None, data=None):
        self.location = location * NODE_SIZE
        self.file_path = file_path
        self.data = data
    
    def write(self):
        if self.data is None:
            raise ValueError("No data to write")
        if len(self.data) != NODE_SIZE:
            raise ValueError("Data length should be 512 bytes")
        if self.file_path is None:
            raise ValueError("No file path provided")
        
        with open(self.file_path, 'r+b') as file:
            file.seek(self.location)
            file.write(self.data)
    
    def init_header(self, root=0, next_node_id=0):
        magic_number = MAGIC_NUMBER.to_bytes(8, byteorder='big')
        root = root.to_bytes(8, 'big')
        next_node_id = next_node_id.to_bytes(8, 'big')
        header = magic_number + root + next_node_id
        header += b'\x00' * (NODE_SIZE - len(header))
        
        self.data = header
        self.write()
        return header
    
    def adjust_header(self, root=None, next_node_id=None):
        if self.data[:8] != MAGIC_NUMBER.to_bytes(8, byteorder='big'):
            raise ValueError("Invalid header data")
        
        if root is not None:
            root_bytes = root.to_bytes(8, 'big')
            self.data = self.data[:8] + root_bytes + self.data[16:]
        
        if next_node_id is not None:
            next_node_id_bytes = next_node_id.to_bytes(8, 'big')
            self.data = self.data[:16] + next_node_id_bytes + self.data[24:]
        
        self.write()
        return self.data
    
    def init_node(self, block_id, parent_id, num_keys, keys, values, children):
        block_id_bytes = block_id.to_bytes(8, 'big')
        parent_id_bytes = parent_id.to_bytes(8, 'big')
        num_keys_bytes = num_keys.to_bytes(8, 'big')
        
        keys_bytes = b''.join(key.to_bytes(8, 'big') for key in keys) + b'\x00' * ((152 - len(keys)))
        values_bytes = b''.join(value.to_bytes(8, 'big') for value in values) + b'\x00' * ((152 - len(values)))
        children_bytes = b''.join(child.to_bytes(8, 'big') for child in children) + b'\x00' * ((160 - len(children)))
        
        node = block_id_bytes + parent_id_bytes + num_keys_bytes + keys_bytes + values_bytes + children_bytes
        node += b'\x00' * (NODE_SIZE - len(node))
        
        self.data = node
        self.write()
        return node
    
    def adjust_node(self, block_id=None, parent_id=None, num_keys=None, keys=None, values=None, children=None):
        if self.data[:8] == MAGIC_NUMBER.to_bytes(8, byteorder='big'):
            raise ValueError("Trying to adjust header data as a node")
        
        if block_id is not None:
            block_id_bytes = block_id.to_bytes(8, 'big')
            self.data = block_id_bytes + self.data[8:]
        
        if parent_id is not None:
            parent_id_bytes = parent_id.to_bytes(8, 'big')
            self.data = self.data[:8] + parent_id_bytes + self.data[16:]
        
        if num_keys is not None:
            num_keys_bytes = num_keys.to_bytes(8, 'big')
            self.data = self.data[:16] + num_keys_bytes + self.data[24:]
        
        if keys is not None:
            keys_bytes = b''.join(key.to_bytes(8, 'big') for key in keys) + b'\x00' * ((152 - len(keys)))
            self.data = self.data[:24] + keys_bytes + self.data[176:]
        
        if values is not None:
            values_bytes = b''.join(value.to_bytes(8, 'big') for value in values) + b'\x00' * ((152 - len(values)))
            self.data = self.data[:176] + values_bytes + self.data[328:]
        
        if children is not None:
            children_bytes = b''.join(child.to_bytes(8, 'big') for child in children) + b'\x00' * ((160 - len(children)))
            self.data = self.data[:328] + children_bytes + self.data[488:]
        
        self.write()
        return self.data

    @staticmethod
    def read_header(file, location=0):
        file.seek(location * NODE_SIZE)
        data = file.read(NODE_SIZE)

        root = int.from_bytes(data[8:16], 'big')
        next_node_id = int.from_bytes(data[16:24], 'big')
        return {
            'header': True,
            'root': root,
            'next_node': next_node_id
        }
    
    @staticmethod
    def read_node(file, location):
        file.seek(location * NODE_SIZE)
        data = file.read(NODE_SIZE)

        if data[:8] == MAGIC_NUMBER.to_bytes(8, byteorder='big'):
            return Node_File.read_header(data)
        
        block_id = int.from_bytes(data[:8], 'big')
        parent_id = int.from_bytes(data[8:16], 'big')
        num_keys = int.from_bytes(data[16:24], 'big')
        
        keys = [int.from_bytes(data[24 + i * 8:32 + i * 8], 'big') for i in range(19)]
        values = [int.from_bytes(data[176 + i * 8:184 + i * 8], 'big') for i in range(19)]
        children = [int.from_bytes(data[328 + i * 8:336 + i * 8], 'big') for i in range(20)]
        
        return {
            'header': False,
            'block_id': block_id,
            'parent_id': parent_id,
            'num_keys': num_keys,
            'keys': keys,
            'values': values,
            'children': children
        }
    
    @staticmethod
    def to_data(node):
        if node['header']:
            root = node['root'].to_bytes(8, 'big')
            next_node_id = node['next_node'].to_bytes(8, 'big')
            return MAGIC_NUMBER.to_bytes(8, byteorder='big') + root + next_node_id + b'\x00' * (NODE_SIZE - 24)
        
        block_id = node['block_id'].to_bytes(8, 'big')
        parent_id = node['parent_id'].to_bytes(8, 'big')
        num_keys = node['num_keys'].to_bytes(8, 'big')
        
        keys = b''.join(key.to_bytes(8, 'big') for key in node['keys']) + b'\x00' * (152 - len(node['keys']))
        values = b''.join(value.to_bytes(8, 'big') for value in node['values']) + b'\x00' * (152 - len(node['values']))
        children = b''.join(child.to_bytes(8, 'big') for child in node['children']) + b'\x00' * (160 - len(node['children']))
        
        length = len(block_id + parent_id + num_keys + keys + values + children)
        return block_id + parent_id + num_keys + keys + values + children + b'\x00' * (NODE_SIZE - length)