# Description:  This file contains utility functions for reading and writing nodes to the file system.
#               These methods are all tested to be working as expected.

MAGIC_NUMBER = "4337PRJ3"
NODE_SIZE = 512

def write(file_path, data, location=0):
    if data is None:
        return False
    if file_path is None:
        return False
    
    try:
        with open(file_path, 'r+b') as file:
            file.seek(location)
            file.write(data)
    except FileNotFoundError:
        with open(file_path, 'wb') as file:
            file.write(data)
    return True

def has_header(file_path):
    try:
        with open(file_path, 'rb') as file:
            data = file.read(8)
            return data == MAGIC_NUMBER.encode('utf-8')
    except:
        return False

def init_header(file_path, root=0, next_node_id=1):
    magic_number = MAGIC_NUMBER.encode('utf-8')
    root_bytes = root.to_bytes(8, 'big')
    next_node_id_bytes = next_node_id.to_bytes(8, 'big')
    header = magic_number + root_bytes + next_node_id_bytes
    header += b'\x00' * (NODE_SIZE - len(header))
    
    write(file_path, header)
    return {
        'header': True,
        'root': root,
        'next_node': next_node_id
    }

def adjust_header(file_path, root=None, next_node_id=None):
    if root is not None:
        root_bytes = root.to_bytes(8, 'big')
        write(file_path, root_bytes, 8)
    
    if next_node_id is not None:
        next_node_id_bytes = next_node_id.to_bytes(8, 'big')
        write(file_path, next_node_id_bytes, 16)
    return

def init_node(file_path, block_id, parent_id, num_keys, keys, values, children):
    block_id_bytes = block_id.to_bytes(8, 'big')
    parent_id_bytes = parent_id.to_bytes(8, 'big')
    num_keys_bytes = num_keys.to_bytes(8, 'big')
    
    keys_bytes = b''.join(key.to_bytes(8, 'big') for key in keys) + b'\x00' * ((152 - (len(keys) * 8)))
    values_bytes = b''.join(value.to_bytes(8, 'big') for value in values) + b'\x00' * ((152 - (len(values) * 8)))
    children_bytes = b''.join(child.to_bytes(8, 'big') for child in children) + b'\x00' * ((160 - (len(children) * 8)))
    
    node = block_id_bytes + parent_id_bytes + num_keys_bytes + keys_bytes + values_bytes + children_bytes
    node += b'\x00' * (NODE_SIZE - len(node))
    
    write(file_path, node, block_id * NODE_SIZE)
    return {
        'header': False,
        'block_id': block_id,
        'parent_id': parent_id,
        'num_keys': num_keys,
        'keys': keys,
        'values': values,
        'children': children
    }

def adjust_node(file_path, block_id, parent_id=None, num_keys=None, keys=None, values=None, children=None):
    if parent_id is not None:
        parent_id_bytes = parent_id.to_bytes(8, 'big')
        write(file_path, parent_id_bytes, block_id * NODE_SIZE + 8)
    
    if num_keys is not None:
        num_keys_bytes = num_keys.to_bytes(8, 'big')
        write(file_path, num_keys_bytes, block_id * NODE_SIZE + 16)
    
    if keys is not None:
        keys_bytes = b''.join(key.to_bytes(8, 'big') for key in keys) + b'\x00' * ((152 - (len(keys) * 8)))
        write(file_path, keys_bytes, block_id * NODE_SIZE + 24)
    
    if values is not None:
        values_bytes = b''.join(value.to_bytes(8, 'big') for value in values) + b'\x00' * ((152 - (len(values) * 8)))
        write(file_path, values_bytes, block_id * NODE_SIZE + 176)
    
    if children is not None:
        children_bytes = b''.join(child.to_bytes(8, 'big') for child in children) + b'\x00' * ((160 - (len(children) * 8)))
        write(file_path, children_bytes, block_id * NODE_SIZE + 328)
    return

def overwrite_node(file_path, node):
    if node['header']:
        adjust_header(file_path, node['root'], node['next_node'])
    else:
        adjust_node(file_path, node['block_id'], node['parent_id'], node['num_keys'], node['keys'], node['values'], node['children'])
    return

def read_header(data):
    root = int.from_bytes(data[8:16], 'big')
    next_node_id = int.from_bytes(data[16:24], 'big')
    return {
        'header': True,
        'root': root,
        'next_node': next_node_id
    }

def get_next_node_id(file_path):
    with open(file_path, 'rb') as file:
        file.seek(16)
        next_node_id = int.from_bytes(file.read(8), 'big')
        return next_node_id

def read_node(file_path, location):
    result = None
    with open(file_path, 'rb') as file:
        file.seek(location * NODE_SIZE)
        data = file.read(NODE_SIZE)

        if data[:8] == MAGIC_NUMBER.encode('utf-8'):
            result = read_header(data)
        else:
            block_id = int.from_bytes(data[:8], 'big')
            parent_id = int.from_bytes(data[8:16], 'big')
            num_keys = int.from_bytes(data[16:24], 'big')
            
            keys = [int.from_bytes(data[24 + i * 8:32 + i * 8], 'big') for i in range(num_keys)]
            values = [int.from_bytes(data[176 + i * 8:184 + i * 8], 'big') for i in range(num_keys)]
            children = [int.from_bytes(data[328 + i * 8:336 + i * 8], 'big') for i in range(20)]
            trimmed_children = [x for x in children if x != 0]

            result = {
                'header': False,
                'block_id': block_id,
                'parent_id': parent_id,
                'num_keys': num_keys,
                'keys': keys,
                'values': values,
                'children': trimmed_children
            }
    return result

def to_data(node):
    if node['header']:
        root = node['root'].to_bytes(8, 'big')
        next_node_id = node['next_node'].to_bytes(8, 'big')
        return MAGIC_NUMBER.encode('utf-8') + root + next_node_id + b'\x00' * (NODE_SIZE - 24)
    
    block_id = node['block_id'].to_bytes(8, 'big')
    parent_id = node['parent_id'].to_bytes(8, 'big')
    num_keys = node['num_keys'].to_bytes(8, 'big')
    
    keys = b''.join(key.to_bytes(8, 'big') for key in node['keys']) + b'\x00' * (152 - (len(node['keys']) * 8))
    values = b''.join(value.to_bytes(8, 'big') for value in node['values']) + b'\x00' * (152 - (len(node['values']) * 8))
    children = b''.join(child.to_bytes(8, 'big') for child in node['children']) + b'\x00' * (160 - (len(node['children']) * 8))
    
    length = len(block_id + parent_id + num_keys + keys + values + children)
    return block_id + parent_id + num_keys + keys + values + children + b'\x00' * (NODE_SIZE - length)