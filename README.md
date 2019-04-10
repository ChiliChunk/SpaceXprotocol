##SpaceX
                
                
####Instructions to launch the client

In this folder you will found the following files :
    
    SpaceXprotocol
    ├── server
    │   ├── server.py
    │   ├── Robot.py
    │   ├── spaceXserver.conf
    │   ├── spaceX.logs
    ├── Client
    │   ├── client.py
    │   ├── application.py
    │   ├── spaceXclient.conf
    └── README.md


First of all, we have to launch the server that can be founded on this directory, then you can do execute it like this by opening your terminal
 and typing the following command:

    python server.py

You dont need to specify the port because we have the configuration file of the server that contains the port
and the information needed to launch the application, like the dimensions of the map, the number of clients that
can be connected at the same time and the resources that there are in the map with their
probability to appear too. 

Then you will be able to launch the client with the following command:

    python application.py

Either, in this case your need to specify the ip address and the port number, all this information
are saved in the configuration file of the client.

Once the client is launched, you have just to follows the instructions printed on the terminal.
You will pick a pseudo and then command a robot on a grid, you can move on this grid and collect resources. 
You can :

* move your robot on a adjacent row
* get the list of all the players and the resources they collected
* pause the program and unpause it
* change your current pseudo
* and logout when you want to quit the program

When you logout your robot is removed from the map.

You will find the history of the commands that didnt go well in the **spaceX.logs** file which is in this folder.
This file contains the IP address of the client that executed the command, the description of the error and its error code.


If you need more information about this application, you can see the **RFC.txt** file in this 
folder; this file contains all the information about the exchange between the server and the client.


