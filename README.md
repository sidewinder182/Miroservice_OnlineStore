# 677 Lab 3

## System requirements
The system runs on Python 3. Please make sure you have any version of Python 3 installed and also run any python commands using `python 3`
Install the following packages before running the system:
- Flask
- requests

## Steps to run the system
- Please configure the config file - 'config.json' with the IP of the machine on which the respective server will run and port number you wish to run it on.
The congif file maps each server to its IP and port number in the format `serverName : IP:portNumber`

A sample config file would look as follows:
```
{
"CatalogServer" : "192.168.0.8:8913",
"OrderServer" : "192.168.0.8:8911",
"FrontEndServer" : "192.168.0.8:8912"
}
```

- Once the config file is set up you can run each server with the following command `python3 serverName.py`.
There are three servers - `catalogServer.py`, `orderServer.py` and `frontEndServer.py`
For example, to run the catalogServer use the command `python3 catalogServer.py`
You may start the servers in any order. Once you severs are started you can start the client application using the command `python3 client.py`

- Follow the client interface to perform the operations on Pygmy.com