from flask import Flask,jsonify,request
import csv
import requests
import json
from datetime import datetime
import time
import threading

lock = threading.Lock()
orderServer2 = Flask(__name__)
with open('config.json') as json_file:
	data = json.load(json_file)
	catalogIP1 = data['CatalogServer1'].split(":")[0] # IP, port number of the catalog server 1
	catalogPort1 = data['CatalogServer1'].split(":")[1]
	catalogIP2 = data['CatalogServer2'].split(":")[0] # IP, port number of the catalog server 2
	catalogPort2 = data['CatalogServer2'].split(":")[1]
	orderIP1 = data['OrderServer1'].split(":")[0]	# IP, port number of the order server 1
	orderPort1 = data['OrderServer1'].split(":")[1]
current_catalog_server = 1		#This flag decides which catalog server should be requested in a round robin fashion
flags = {}		#This dictionary contains flags to track the state of all the backend servers
flags['catalog1'] = 1
flags['catalog2'] = 1
flags['order1'] = 1
flags['order2'] = 1

@orderServer2.route("/")
def index():
	return "Welcome to Pygmy.com, the world's best book store!"

@orderServer2.route("/buy/<string:item_number>/",methods=['GET'])
def buy(item_number):
	'''This method buys an item from one of the catalog servers in a round robin manner. It first queries the catalog server for the requested item.
	If the item is in stock, it calls the buy method on the catalog server to actually buy the item.'''
	global current_catalog_server, flags
	if current_catalog_server == 0 and flags['catalog1'] == 1:
		catalogIP = catalogIP1
		catalogPort = catalogPort1
		current_catalog_server = 1
		print('chose catalog server 1 for buy')
	elif flags['catalog2'] == 1:
		catalogIP = catalogIP2
		catalogPort = catalogPort2
		current_catalog_server = 0
		print('chose catalog server 2 for buy')
	else:
		catalogIP = catalogIP1
		catalogPort = catalogPort1
		current_catalog_server = 1
		print('chose catalog server 1 for buy')
	lookup_url = 'http://' + catalogIP + ':' + catalogPort + '/lookup/' + item_number	 # URL for the catalog server lookup method
	# start = time.time()
	try:
		r = requests.get(lookup_url, timeout = 5)
		resp = r.json()
		if not resp: # If received an empty json, which can happen in case of a wrong item number, just return the empty json as is
			return jsonify(resp)
		elif int(resp['Stock']) > 0: # If json is not empty, check stock
			buy_url = 'http://' + catalogIP + ':' + catalogPort + '/buy/' # URL for the catalog server buy method
			# start = time.time()
			buy_request = requests.post(buy_url,json = {'ItemNumber' : item_number}, timeout = 5)
			result = buy_request.json()['Result'] # Result denotes whether the buy on the catalog server was successful or not
			if result == '1':
				resp['Result'] = '1'
				new_row = {'ItemNumber' : resp['ItemNumber'], 'Title' : resp['Title'], 'Cost' : resp['Cost'], 'Timestamp' : datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")}
				fieldnames = ['ItemNumber', 'Title','Cost','Timestamp']
				with open('orders2.csv', 'a') as csvfile: # Write the updated stock value to the catalog file
					writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
					writer.writerow(new_row)
				update_url = 'http://' + orderIP1 + ':' + orderPort1 + '/update_order/'
				try:
					if flags['order1'] == 1:
						update_request = requests.post(update_url, json = new_row, timeout = 10)
						print('Update request sent to orderServer1 to update orders file')
					else:
						print('Cannot update orders  for orderServer1 since it is down')
				except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
					print('Cannot update orders  for orderServer1 since it is down')
			else:
				resp['Result'] = '0'
		else:
			resp['Result'] = '0'
		return jsonify(resp)
	except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
		return jsonify({'Result' : 0})
	# end = time.time()
	# time_taken = end - start
	# print('Lookup took ',time_taken,' seconds\n')

		# end = time.time()
		# time_taken = end - start
		# print('Buy took ',time_taken,' seconds\n')

@orderServer2.route("/update_order/",methods=['POST'])
def update_order():
	'''This method is used to update the orders file  when the other orderServer replica makes an entry to its
	order server.'''
	posted_json = request.get_json()
	fieldnames = ['ItemNumber', 'Title','Cost','Timestamp']
	with open('orders2.csv', 'a') as csvfile: # Write the updated stock value to the catalog file
		writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
		writer.writerow(posted_json)
	resp = {}
	resp['updated'] = True
	return jsonify(resp)

@orderServer2.route("/heartbeat/",methods=['PUT'])
def heartbeat():
	'''This method is called by the frontEndServer when there is a change in state of any other
	backend server. This allows the order server to reroute any requests to the server that is down.'''
	global flags
	posted_json = request.get_json()
	flags = json.loads(posted_json)
	print(flags)
	return(jsonify({'updates_flags' : True}))

@orderServer2.route("/sync/",methods=['GET'])
def sync():
	'''This method is called on startup by the other replica. This migrates the state of this server to
	 the other in case of failure and recovery'''
	a = []
	lock.acquire()
	try:
		fieldnames = ['ItemNumber', 'Title','Cost','Timestamp']
		with open('orders2.csv') as f:
			a = [{k: v for k, v in row.items()} for row in csv.DictReader(f, fieldnames = fieldnames)]
	except:
		print("File Error")
	finally:
		lock.release()
	return jsonify(a)

if __name__ == "__main__":
	try:
		print('syncing')
		sync_url = 'http://' + orderIP1 + ':' + orderPort1 + '/sync/'
		sync_request = requests.get(sync_url, timeout = 10)
		sync_data = sync_request.json()
		fieldnames = ['ItemNumber', 'Title','Cost','Timestamp']
		f = open("orders2.csv", "w")
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writerows(sync_data)
		f.close()
	except(requests.exceptions.ConnectionError):
		print('unable to sync because orderServer1 is not up')
	with open('config.json') as json_file:
		data = json.load(json_file)
		portnum = data['OrderServer2'].split(":")[1] # Read port number from config file
	orderServer2.run(host = '0.0.0.0',port = portnum,debug = False,threaded = True)
