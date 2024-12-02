import unittest
import os
import node_utils

def test_path(name):
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', name)

class TestNodeUtils(unittest.TestCase):
    # Works
    def test_write(self):
        magic_number = '4337PRJ3'.encode('utf-8')
        root_id = 0
        next_node_id = 1
        header = magic_number + root_id.to_bytes(8, 'big') + next_node_id.to_bytes(8, 'big') + b'\x00' * (node_utils.NODE_SIZE - 24)
        self.assertTrue(node_utils.write(test_path('write.txt'), header, 0))
        # check if the file has been created
    
    # Works
    def test_init_header(self):
        test_header = {
            'header': True,
            'root': 50,
            'next_node': 54
        }
        self.assertEqual(node_utils.init_header(test_path('init_header.txt'), 50, 54), test_header)
        # check if the file has been created

    # Works
    def test_adjust_header(self):
        node_utils.init_header(test_path('adjust_header.txt'), 50, 54)
        self.assertIsNone(node_utils.adjust_header(test_path('adjust_header.txt'), 29, 40))
        # check if the file has been updated

    # Works
    def test_init_node(self):
        test_node_1 = {
            'header': False,
            'block_id': 1,
            'parent_id': 0,
            'num_keys': 2,
            'keys': [0, 1],
            'values': [0, 1],
            'children': [2]
        }
        test_node_2 = {
            'header': False,
            'block_id': 2,
            'parent_id': 1,
            'num_keys': 2,
            'keys': [2, 3],
            'values': [2, 3],
            'children': [4]
        }
        with open(test_path('init_node.txt'), 'w') as file:
            file.write('')
        node_utils.init_header(test_path('init_node.txt'), 0, 3)
        self.assertEqual(node_utils.init_node(test_path('init_node.txt'), 1, 0, 2, [0, 1], [0, 1], [2]), test_node_1)
        self.assertEqual(node_utils.init_node(test_path('init_node.txt'), 2, 1, 2, [2, 3], [2, 3], [4]), test_node_2)
        # check if the file has been created

    # Works
    def test_adjust_node(self):
        with open(test_path('adjust_node.txt'), 'w') as file:
            file.write('')
        node_utils.init_header(test_path('adjust_node.txt'), 0, 2)
        node_utils.init_node(test_path('adjust_node.txt'), 1, 0, 2, [0, 1], [0, 1], [2])
        # This is the reference node
        test_node = {
            'header': False,
            'block_id': 1,
            'parent_id': 1,
            'num_keys': 2,
            'keys': [2, 3],
            'values': [2, 3],
            'children': [4]
        }
        self.assertIsNone(node_utils.adjust_node(test_path('adjust_node.txt'), 1, 1, 2, [2, 3], [2, 3], [4]))

    # Works
    def test_read_header(self):
        test_node = {
            'header': True,
            'root': 50,
            'next_node': 54
        }
        with open(test_path('read_header.txt'), 'w') as file:
            file.write('')
        node_utils.init_header(test_path('read_header.txt'), 50, 54)
        self.assertEqual(node_utils.read_header(node_utils.to_data(test_node)), test_node)

    # Works
    def test_read_node(self):
        test_node = {
            'header': False,
            'block_id': 1,
            'parent_id': 0,
            'num_keys': 2,
            'keys': [2, 3],
            'values': [2, 3],
            'children': [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
        with open(test_path('read_node.txt'), 'w') as file:
            file.write('')
        node_utils.init_header(test_path('read_node.txt'), 1, 2)
        node_utils.init_node(test_path('read_node.txt'), 1, 0, 2, [2, 3], [2, 3], [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(node_utils.read_node(test_path('read_node.txt'), 1), test_node)

        test_header = {
            'header': True,
            'root': 1,
            'next_node': 2
        }
        self.assertEqual(node_utils.read_node(test_path('read_node.txt'), 0), test_header)

    # Works
    def test_to_data(self):
        node_utils.init_header(test_path('to_data.txt'), 1, 2)
        node_utils.init_node(test_path('to_data.txt'), 1, 0, 2, [2, 3], [2, 3], [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        test_node = {
            'header': False,
            'block_id': 1,
            'parent_id': 0,
            'num_keys': 2,
            'keys': [2, 3],
            'values': [2, 3],
            'children': [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
        with open(test_path('to_data.txt'), 'rb') as file:
            file.seek(512)
            data = file.read(512)
            self.assertEqual(node_utils.to_data(test_node), data)

if __name__ == '__main__':
    unittest.main()