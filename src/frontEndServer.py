from flask import Flask,jsonify, Request
from flask_caching import Cache
import csv
import requests
import json
import time

# cache = {}

frontEndServer = Flask(__name__)
cache = Cache(frontEndServer, config={'CACHE_TYPE': 'simple'})
with open('config.json') as json_file:
	data = json.load(json_file)
	catalogIP = data['CatalogServer'].split(":")[0] # IP, port number of the catalog server
	catalogPort = data['CatalogServer'].split(":")[1]
	orderIP = data['OrderServer'].split(":")[0]# # IP, port number of the order server
	orderPort = data['OrderServer'].split(":")[1]

@frontEndServer.route("/")
def index():
	return "Welcome to Pygmy.com, the world's smallest book store!"


@frontEndServer.route("/search/<string:topic>/",methods=['GET'])
@cache.memoize(timeout = 100)
def search(topic):
	'''This method forwards an incoming search request to the catalog server, and returns the response received
	from it to the caller.'''
	url = 'http://' + catalogIP + ':' + catalogPort + '/search/' + topic
	r = requests.get(url)
	frontEndResponse = r.json()
	return jsonify(frontEndResponse)


@frontEndServer.route("/lookup/<string:itemNumber>/",methods = ['GET'])
@cache.memoize(timeout = 100)
def lookup(itemNumber):
	'''This method forwards an incoming lookup request to the catalog server, and returns the response received
	from it to the caller.'''
	url = 'http://' + catalogIP + ':' + catalogPort + '/lookup/' + itemNumber
	# start = time.time()
	r = requests.get(url)
	# end = time.time()
	# time_taken = end - start
	# print('Lookup took ',time_taken,' seconds\n')
	frontEndResponse = r.json()
	return jsonify(frontEndResponse)

@frontEndServer.route("/buy/<string:itemNumber>/",methods=['GET'])
def buy(itemNumber):
	'''This method forwards an incoming buy request to the order server, and returns the response received
	from it to the caller.'''
	url = 'http://' + orderIP + ':' + orderPort + '/buy/' + itemNumber
	# start = time.time()
	r = requests.get(url)
	# end = time.time()
	# time_taken = end - start
	# print('Buy took ',time_taken,' seconds\n')
	frontEndResponse = r.json()
	return jsonify(frontEndResponse)

@frontEndServer.route("/invalidate/<string:itemNumber>/",methods=['DELETE'])
def invalidate(itemNumber):
	print('entered invalidate')
	response_dict = {'invalidated' : False}
	cache.delete_memoized(lookup, itemNumber)
	response_dict = {'invalidated' : True}
	print('invalidated')
	return jsonify(response_dict)


if __name__ == "__main__":
	with open('config.json') as json_file:
		data = json.load(json_file)
		portnum = data['FrontEndServer'].split(":")[1]
	frontEndServer.run(host = '0.0.0.0',port = portnum,debug = False,threaded = True)
