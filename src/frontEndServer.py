from flask import Flask,jsonify, Request
from flask_caching import Cache
import csv
import requests
import json
import time
import random
import threading
import time

# cache = {}


frontEndServer = Flask(__name__)
cache = Cache(frontEndServer, config={'CACHE_TYPE': 'simple'})
with open('config.json') as json_file:
	data = json.load(json_file)
	catalogIP1 = data['CatalogServer1'].split(":")[0] # IP, port number of the catalog server replica 1
	catalogPort1 = data['CatalogServer1'].split(":")[1]
	orderIP1 = data['OrderServer1'].split(":")[0]# # IP, port number of the order server replica 1
	orderPort1 = data['OrderServer1'].split(":")[1]
	catalogIP2 = data['CatalogServer2'].split(":")[0] # IP, port number of the catalog server replica 2
	catalogPort2 = data['CatalogServer2'].split(":")[1]
	orderIP2 = data['OrderServer2'].split(":")[0]# # IP, port number of the order server replica 2
	orderPort2 = data['OrderServer2'].split(":")[1]
current_order_server = 0
current_catalog_server = 0
flags = {}
flags['catalog1'] = 1
flags['catalog2'] = 1
flags['order1'] = 1
flags['order2'] = 1
urls = {}
urls['catalog1'] = 'http://' + catalogIP1 + ':' + catalogPort1
urls['catalog2'] = 'http://' + catalogIP2 + ':' + catalogPort2
urls['order1'] = 'http://' + orderIP1 + ':' + orderPort1
urls['order2'] = 'http://' + orderIP2 + ':' + orderPort2

@frontEndServer.route("/")
def index():
	return "Welcome to Pygmy.com, the world's smallest book store!"


@frontEndServer.route("/search/<string:topic>/",methods=['GET'])
@cache.memoize(timeout = 100)
def search(topic):
	'''This method forwards an incoming search request to the catalog server, and returns the response received
	from it to the caller.'''
	global current_catalog_server, flags
	if current_catalog_server == 0 and flags['catalog1'] == 1:
		current_catalog_server = 1
		url = 'http://' + catalogIP1 + ':' + catalogPort1 + '/search/' + topic
		print('chose catalog server 1 for search')
	elif flags['catalog2'] == 1:
		current_catalog_server = 0
		url = 'http://' + catalogIP2 + ':' + catalogPort2 + '/search/' + topic
		print('chose catalog server 2 for search')
	else:
		current_catalog_server = 1
		url = 'http://' + catalogIP1 + ':' + catalogPort1 + '/search/' + topic
		print('chose catalog server 1 for search')
	r = requests.get(url)
	frontEndResponse = r.json()
	return jsonify(frontEndResponse)


@frontEndServer.route("/lookup/<string:itemNumber>/",methods = ['GET'])
@cache.memoize(timeout = 100)
def lookup(itemNumber):
	'''This method forwards an incoming lookup request to the catalog server, and returns the response received
	from it to the caller.'''
	global current_catalog_server, flags
	if current_catalog_server == 0 and flags['catalog1'] == 1:
		current_catalog_server = 1
		url = 'http://' + catalogIP1 + ':' + catalogPort1 + '/lookup/' + itemNumber
		print('chose catalog server 1 for lookup')
	elif flags['catalog2'] == 1:
		current_catalog_server = 0
		url = 'http://' + catalogIP2 + ':' + catalogPort2 + '/lookup/' + itemNumber
		print('chose catalog server 2 for lookup')
	else:
		current_catalog_server = 1
		url = 'http://' + catalogIP1 + ':' + catalogPort1 + '/lookup/' + itemNumber
		print('chose catalog server 1 for lookup')
	# start = time.time()
	try:
		r = requests.get(url, timeout = 5)
	except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
		response_dict = {}
		return jsonify(response_dict)
	# end = time.time()
	# time_taken = end - start
	# print('Lookup took ',time_taken,' seconds\n')
	frontEndResponse = r.json()
	return jsonify(frontEndResponse)

@frontEndServer.route("/buy/<string:itemNumber>/",methods=['GET'])
def buy(itemNumber):
	'''This method forwards an incoming buy request to the order server, and returns the response received
	from it to the caller.'''
	global current_order_server, flags
	if current_order_server == 0 and flags['order1'] == 1:
		current_order_server = 1
		url = 'http://' + orderIP1 + ':' + orderPort1 + '/buy/' + itemNumber
		print('chose order server 1 for buy')
	elif flags['order2'] == 1:
		current_order_server = 0
		url = 'http://' + orderIP2 + ':' + orderPort2 + '/buy/' + itemNumber
		print('chose order server 2 for buy')
	else:
		current_order_server = 1
		url = 'http://' + orderIP1 + ':' + orderPort1 + '/buy/' + itemNumber
		print('chose order server 1 for buy')
	# start = time.time()
	try:
		r = requests.get(url, timeout = 5)
	except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
		return jsonify({'Result' : 0})

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

def heartbeat():
	global flags, urls
	print('starting heartbeat thread')
	while True:
		time.sleep(10)
		try:
			r = requests.get(urls['catalog1'])
			flags['catalog1'] = 1
		except:
			flags['catalog1'] = 0
			print('catalog1 down')
		try:
			r = requests.get(urls['catalog2'])
			flags['catalog2'] = 1
		except:
			flags['catalog2'] = 0
			print('catalog2 down')
		try:
			r = requests.get(urls['order1'])
			flags['order1'] = 1
		except:
			flags['order1'] = 0
			print('order1 down')
		try:
			r = requests.get(urls['order2'])
			flags['order2'] = 1
		except:
			flags['order2'] = 0
			print('order2 down')
		flags_json = json.dumps(flags)
		for key in flags:
			if flags[key] == 1:
				with frontEndServer.app_context():
					try:
						r = requests.put(urls[key] + '/heartbeat/', json = flags_json)
					except requests.exceptions.ConnectionError:
						'Server crashed during heartbeat'

if __name__ == "__main__":
	with open('config.json') as json_file:
		data = json.load(json_file)
		portnum = data['FrontEndServer'].split(":")[1]
	# frontEndServer.run(host = '0.0.0.0',port = portnum,debug = False,threaded = True)
	serverThread = threading.Thread(target = frontEndServer.run,kwargs = {'host' : '0.0.0.0','port' : portnum,'threaded':True}) # This is the server thread
	heartbeatThread = threading.Thread(target = heartbeat)
	serverThread.start()
	heartbeatThread.start()
