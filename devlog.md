11/27   14:27:  This is my initial log entry. I am planning to probably first get the B-Tree done, then work on all the actual functions using individual methods for each one. 
                The good part about this project is that it doesn't require any removal from the B-Tree, so that makes it simpler to implement. Most likely, I will use the 
                B-Tree implementation from the homework as reference, and just modify it so that there are only up to three nodes in memory at once.
                In this session, I honestly don't really have a plan, I just want to get started on the B-Tree implementation.

11/27   14:53:  Just remembered to add a .gitignore for the sample files from the professor.

11/27   18:19:  For the most part, I finished making the node_utils.py file, which consists of managing nodes and reading/writing to them.
                I started on index_utils.py, I'm trying to figure out how to finish get_root() as the main problem is that we can get the root id from the header just fine,
                    but we then need to find the right id in the file, as the header contains the root id, not the root location, and the id does not translate to the location.
                    ***Oh wait I just realized it's the block id, not a supposed root id. Because there is no root id, and there is no supposed one "value" that is the root
                       (all values in the node are the root node), I should just be able to implement a root_node_search() in index_utils.py that searches for the block_id value of
                       the header's root id. How that search would work (outside of checking if it's in memory) could be to just read from file down the list until we find the root id.
                I definitely did not finish the B-Tree implementation, barely even started on it actually, but instead I'm changing course and trying to just lay down the framework 
                    of the project, so that I can just easily implement a simple B-Tree implementation afterwards using my current file and memory framework.

11/28   01:24:  Just wanted to start on making reading from the file in index_utils.py a little easier by not having to check if things are in memory every time in each method,
                instead just putting it in the read function.