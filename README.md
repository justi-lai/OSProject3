# OSProject3
CS 4348.502 Project 3 - BTree

In order to run this program:
    Run the main.py file from the OSProject3 directory.
    It should create a csv and indexes folder if it wasn't created before. This is where you store your index files and csv files to load and extract.
    The testing folder and test_utils.py is to run tests for the node_utils.py file. Try not to use it since it will most likely error out due to not having the respective testing txt files.

Files in this project:
    main.py - This file is the main driver of this project, and manages the console ui and inputs from the user. It will create BTree objects from the btree.py file and use methods from it to perform operations on an index file.

    btree.py - This file is the main functionality of this project. It operates with a maximum of three nodes in memory (a list of 3 nodes in the object), and using node_utils.py to modify the index file when needed. A clock replacement policy is used on the memory, and generally saves the state of a node immediately after modifying it for safety.

    node_utils.py - This file contains utility methods to easily read and write to the index file in the formats required for the headers and nodes at their specific locations.

    test_utils.py - This file contains a testing class for node_utils.py.

    devlog.md - This file contains my logs of all of my working sessions and records the process of completing this project.