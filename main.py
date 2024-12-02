import btree as bt
import os

DEGREE = 10

def main():
    initiate_directory()
    B = None
    while True:
        choice = menu()
        
        if choice == 1:
            file_name = input("Enter the name of the file: ")
            file_path = os.path.join(os.path.dirname(__file__), 'indexes', file_name)
            if os.path.exists(file_path):
                overwrite = input("File already exists. Overwrite? (Y/N): ")
                if overwrite.lower() != 'y':
                    continue
            with open(file_path, 'w') as f:
                f.write('')
            B = bt.BTree(file_name, DEGREE)
            print(f"{file_name} is open.")

        elif choice == 2:
            current_files = os.listdir(os.path.join(os.path.dirname(__file__), 'indexes'))
            if not current_files:
                print("No files to open.")
                continue
            print("Current files:")
            i = 1
            for file in current_files:
                print(f"{i}.\t{file}")
                i += 1
            file_name = input("Enter the name/number of the file: ")
            if file_name.isnumeric():
                file_name = current_files[int(file_name) - 1]
            file_path = os.path.join(os.path.dirname(__file__), 'indexes', file_name)
            if not os.path.exists(file_path):
                print(f"{file_name} does not exist.")
                continue
            B = bt.BTree(file_name, DEGREE)
            print(f"{file_name} is open.")

        elif choice == 3:
            if B is None:
                print("No file is open.")
                continue
            key = int(input("Enter the key to insert: "))
            if B.search_key(key) is not None:
                print("Key already exists.")
                continue
            value = int(input("Enter the value to insert: "))
            B.insert(key, value)
            print(f"{key}: {value} inserted.")
        
        elif choice == 4:
            if B is None:
                print("No file is open.")
                continue
            key = int(input("Enter the key to search: "))
            value = B.search_key(key)
            if value is None:
                print("Key not found.")
            else:
                print(f"{key}: {value}")
        
        elif choice == 5:
            current_files = os.listdir(os.path.join(os.path.dirname(__file__), 'csv'))
            if not current_files:
                print("No files to load.")
                continue
            print("Current files:")
            i = 1
            for file in current_files:
                print(f"{i}.\t{file}")
                i += 1
            file_name = input("Enter the name of the file to load: ")
            if file_name.isnumeric():
                file_name = current_files[int(file_name) - 1]
            file_path = os.path.join(os.path.dirname(__file__), 'csv', file_name)
            if not os.path.exists(file_path):
                print(f"{file_name} does not exist.")
                continue
            B.load(file_path)
            print(f"{file_name} has been loaded.")
        
        elif choice == 6:
            if B is None:
                print("No file is open.")
                continue
            B.print_tree()
        
        elif choice == 7:
            if B is None:
                print("No file is open.")
                continue
            current_files = os.listdir(os.path.join(os.path.dirname(__file__), 'csv'))
            file_name = input("Enter the name of the file to extract: ")
            file_path = os.path.join(os.path.dirname(__file__), 'csv', file_name)
            if os.path.exists(file_path):
                overwrite = input("File already exists. Overwrite? (Y/N): ")
                if overwrite.lower() != 'y':
                    continue
            B.extract(file_path)
            print(f"{file_name} extracted.")
        
        elif choice == 8:
            if B is not None:
                B.close()
            break

def initiate_directory():
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'indexes')):
        os.makedirs(os.path.join(os.path.dirname(__file__), 'indexes'))
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'csv')):
        os.makedirs(os.path.join(os.path.dirname(__file__), 'csv'))

def menu():
    _display_menu()
    while True:
        choice = input("Enter your choice: ").lower()
        if choice in ['1', 'create']:
            return 1
        elif choice in ['2', 'open']:
            return 2
        elif choice in ['3', 'insert']:
            return 3
        elif choice in ['4', 'search']:
            return 4
        elif choice in ['5', 'load']:
            return 5
        elif choice in ['6', 'print']:
            return 6
        elif choice in ['7', 'extract']:
            return 7
        elif choice in ['8', 'quit']:
            return 8
        else:
            print("Invalid choice. Please try again.")

def _display_menu():
    print("________________________________________________________")
    print("1. Create")
    print("2. Open")
    print("3. Insert")
    print("4. Search")
    print("5. Load")
    print("6. Print")
    print("7. Extract")
    print("8. Quit")

if __name__ == '__main__':
    main()