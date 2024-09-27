# Python-Socket-Chat-App

# To run the application: 

``` python server.py ```

``` python client1.py  ```
``` python client2.py  ```
``` python client3.py  ```


# Summary

Server:

--- Starts and listens for incoming client connections.
# For each client connection, it spawns a new thread to handle communication.
# Receives messages from clients and broadcasts them to all other connected clients.
# Allows the server to send messages to all clients via console input.

Clients:

# Each client connects to the server and starts a GUI.

# Users can send messages through the GUI, which are sent to the server.

# Clients receive messages from the server and display them in the chat area.

# Each client has a unique ID (client1, client2, client3) to differentiate between them.

Communication: Clients can send messages to the server, which will broadcast them to all other clients. The server can also send messages to all clients via console input.