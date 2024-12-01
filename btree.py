import utils.index_utils as iu

class BTree(iu.Index_File):
    def __init__(self, name, degree):
        super().__init__(name)
        self.degree = degree
    
    def insert(self, key, value):
        if self.get_root() is None:
            self.add_node(0, [key], [value], [0] * 20)
            self.adjust_header(root=1, next_node=2)
            return
        
        if self.get_root()['num_keys'] == 2 * self.degree - 1:
            new_root_id = self.add_node(0, [], [], [self.get_header()['root']])
            self.get_root()['parent_id'] = new_root_id
            self.adjust_header(root=new_root_id)
            self.split_child(new_root_id, 0)
            self.insert_non_full(new_root_id, key, value)
        else:
            self.insert_non_full(self.get_header()['root'], key, value)
    
    def insert_non_full(self, location, key, value):
        i = self.get_node(location)['num_keys'] - 1

        if self.get_node(location)['children'] == [0] * 20:
            self.get_node(location)['keys'].append(None)
            self.get_node(location)['values'].append(None)
            while i >= 0 and key < self.get_node(location)['keys'][i]:
                self.get_node(location)['keys'][i + 1] = self.get_node(location)['keys'][i]
                self.get_node(location)['values'][i + 1] = self.get_node(location)['values'][i]
                i -= 1
            self.get_node(location)['keys'][i + 1] = key
            self.get_node(location)['values'][i + 1] = value
            self.get_node(location)['num_keys'] += 1
        else:
            while i >= 0 and key < self.get_node(location)['keys'][i]:
                i -= 1
            i += 1
            if self.get_node(self.get_node(location)['children'][i])['num_keys'] == 2 * self.degree - 1:
                self.split_child(location, i)
                if key > self.get_node(location)['keys'][i]:
                    i += 1
            self.insert_non_full(self.get_node(location)['children'][i], key, value)
    
    def split_child(self, location, i):
        temp_children = self.get_node(location)['children']
        temp_children.insert(i + 1, self.add_node(location, [], [], [0] * 20))
        self.adjust_node(location, children=temp_children)
        y_location = self.get_node(location)['children'][i]
        z_location = self.get_node(self.get_node(location)['children'][i + 1])['block_id']

        self.get_node(location)['num_keys'] += 1
        self.get_node(location)['keys'].insert(i, self.get_node(y_location)['keys'][self.degree - 1])
        self.get_node(z_location)['keys'] = self.get_node(y_location)['keys'][self.degree: 2 * self.degree - 1]
        self.get_node(y_location)['keys'] = self.get_node(y_location)['keys'][0: self.degree - 1]
        if self.get_node(y_location)['children'] != [0] * 20:
            self.get_node(z_location)['children'] = self.get_node(y_location)['children'][self.degree: 2 * self.degree]
            self.get_node(y_location)['children'] = self.get_node(y_location)['children'][0: self.degree - 1]

    def print_tree(self, location, level=0):
        print('B-Tree')
        print('Level ', level, " : ", end='')
        for i in range(self.get_node(location)['num_keys']):
            print(self.get_node(location)['keys'][i], end=' ')
            print(self.get_node(location)['values'][i], end=' | ')
        print()
        level += 1
        if self.get_node(location)['children'] != [0] * 20:
            for i in range(self.get_node(location)['num_keys'] + 1):
                self.print_tree(self.get_node(location)['children'][i], level)

    def search(self, key):
        pass

    def load(self, file):
        pass

    def print(self):
        pass

    def extract(self):
        pass

    def display(self):
        pass

def main():
    B = BTree('B', 2)
    for i in range(10):
        B.insert(i, 2 * i)
    B.print_tree(0)

if __name__ == '__main__':
    main()