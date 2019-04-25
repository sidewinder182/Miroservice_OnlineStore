# 677 Lab 3

## System requirements
The system runs on Python 3. Please make sure you have any version of Python 3 installed and also run any python commands using `python 3`
Install the following packages before running the system:
- Flask
- requests
-Flask-Caching

## Steps to run the system
- Please configure the config file - 'config.json' with the IP of the machine on which the respective server will run and port number you wish to run it on.
The congif file maps each server to its IP and port number in the format `serverName : IP:portNumber`

A sample config file would look as follows:
```
{
"CatalogServer1" : "192.168.0.8:8913",
"CatalogServer2" : "192.168.0.8:8914",
"OrderServer1" : "192.168.0.8:8911",
"OrderServer2" : "192.168.0.8:8915",
"FrontEndServer" : "192.168.0.8:8912"
}
```

- Once the config file is set up you can run each server with the following command `python3 serverName.py`.
There are 5 servers - `catalogServer1.py`, `catalogServer2.py` `orderServer1.py`, `orderServer2.py` and `frontEndServer.py`
For example, to run the catalogServer1 use the command
```
python3 catalogServer1.py
```
You may start the servers in any order. Once you severs are started you can start the client application using the command `python3 client.py`

- Follow the client interface to perform the operations on Pygmy.com

## Docker
Before creating the docker images for the server files, make sure the config.json file is correctly configured with the IPs and ports of the respective servers. To create docker images for each of the server files, run the docker build command for each file as follows.

```
docker build . -f Dockerfile.catalog1 -t catalog1
```

To run the image, use the docker run command as follows.

```
docker run -p 8913:8913 catalog1
```

The port number for the -p argument (8913 in the above example) should be as mentioned in the config file.
Note the client does not have a Dockerfile, only the servers do.
