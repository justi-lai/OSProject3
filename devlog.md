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

11/28   16:00:  I want to finish the implementation of index_utils.py in this session, or get close to it so that I can start working on the functionality of the B-Tree soon. It is 
                also Thanksgiving today though so I might not have enough time today. I haven't really had any thoughts about the project since last night.

11/28   17:21:  * I am using the clock replacement policy in my memory scheme to maintain only 3 frames at once.
                * Now I'm thinking about just having the id represent it's respective location * NODE_SIZE as it's not like we're going to be changing the ids, just which node is pointing to which.
                * I'm going to have node ids starting from 1 and then going on further because technically they will be at position 1 in the file.
                I'm going to take a break from this as I have now implemented the bullets above, and can now add nodes.
                I think it would be more optimal currently if I just make node_utils only contain static methods, where I can then just input the data directly to the method in a 
                    dictionary, as that would probably be more convinient for writing to files because that means no more having to create a new object every time I want to write to the file. 
                    A possible solution for this would be to just imput the data as a field, as the data already contains the block_id. This way we can just have the add_node method in index_utils to add a new node, and edit previous nodes using adjust_header() or adjust_node() and add a block_id parameter to know which node we are adjusting.
                    I'm probably going to be back later today after dinner and a quick run, so I'll probably work on that, which then I just need to translate this functionality to index_utils, and then I can probably start working on btree_utils.py.

11/28   19:18:  I'm back from Thanksgiving dinner and now I will start working on reworking node_utils.py. I will do this in a separate branch as I want to back it up in case.

11/28   21:39:  * Ok I'm just going to create test classes to make sure that these methods work so far so I won't have to worry about debugging a huge mess later.
                Ok all of node_utils.py is now tested to be working. I manually checked each test output in files by hand. This means that I can probably just start using index_utils without worrying about weird reading and writing errors to files. I might continue later today again at midnight, or I'll just take a break and enjoy Black Friday tomorrow. I think that index_utils is also almost done, so that is good. I'm expecting to be done with all of this utility by tomorrow.

11/30   14:47:  I ended up not having any time yesterday to do work, so I'm going to push the schedule by one day. What is nice though is that index_utils shouldn't need any more 
                functionality, so I can just start implementing the B-Tree already. My plan is to get B-Tree working today.
                My current thoughts are to just basically instead of using an array to perform operations in the B-Tree, I can just use index_utils.py instead as the representation of the B-Tree, so that I'm only keeping up to 3 nodes in memory at once, and I can fetch nodes and edit nodes at once without having to worry about memory problems.
                * There is currently a problem with when I insert nodes the key and values are not matching, and it potentially (not sure if this is the actual cause) creates None values inside the keys, which is causing errors.

11/30   22:43:  I'm going to create a branch and try to revamp index_utils so that it's easier to manage right now. I'm going to try to make it similar to the ArrayList class in Java
                so that I can easily create a B-Tree algorithm. I believe this to be the easiest way, as I can manage making the utils into a List type class, but trying to make the B-Tree to work with the current system is too difficult for me right now. The main problem that I am seeing is that I'm trying to currently use the object references to my advantage by sending them around methods, but the ones that stay in memory are not consistent, so problems will arise where some may just go missing and not get updated. Other times, random key value pairs just don't match up correctly.

12/01   00:45:  I'm tired, I'm going to go sleep. Right now, I'm just starting to combine both index_utils and btree into one, and I'm going to try to work with that. Lots of errors 
                right now.

12/01   15:47:  I didn't put this down last night, but the arraylist idea would not work that well. The reason for that is that I need to keep track of multiple nodes at different 
                times, and trying to make it into an arraylist just adds an extra layer of complexity, as opposed to just baking the entire btree methods into the memory. I'm going to just continue trying to get this implementation to work.

12/01   18:38:  I got the BTree to work for insert. The rest is just getting search, and then the rest should just be simple pulling and just the load. They should be pretty easy 
                to do, so I'm not really thinking about it right now.
                I fixed the main problem of having nodes going in and out of memory by just simply referencing the node before I need to use it, and then anytime another node gets used, if I want to go back to the previous node, I have to make sure it's in memory again. This way, everything is in memory when it is needed.