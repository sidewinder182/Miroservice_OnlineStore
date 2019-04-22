from flask import Flask,jsonify,request
import csv
import requests
import json
from datetime import datetime
import time

orderServer = Flask(__name__)
with open('config.json') as json_file:
	data = json.load(json_file)
	catalogIP = data['CatalogServer'].split(":")[0] # IP, port number of the catalog server
	catalogPort = data['CatalogServer'].split(":")[1]

@orderServer.route("/")
def index():
	return "Welcome to Pygmy.com, the world's best book store!"

@orderServer.route("/buy/<string:item_number>/",methods=['GET'])
def buy(item_number):
	'''This method buys an item from the catalog server. It first queries the catalog server for the requested item.
	If the item is in stock, it calls the buy method on the catalog server to actually buy the item.'''
	lookup_url = 'http://' + catalogIP + ':' + catalogPort + '/lookup/' + item_number	 # URL for the catalog server lookup method
	# start = time.time()
	r = requests.get(lookup_url)
	# end = time.time()
	# time_taken = end - start
	# print('Lookup took ',time_taken,' seconds\n')
	resp = r.json()
	if not resp: # If received an empty json, which can happen in case of a wrong item number, just return the empty json as is
		return jsonify(resp)
	elif int(resp['Stock']) > 0: # If json is not empty, check stock
		buy_url = 'http://' + catalogIP + ':' + catalogPort + '/buy/' # URL for the catalog server buy method
		# start = time.time()
		buy_request = requests.post(buy_url,json = {'ItemNumber' : item_number})
		# end = time.time()
		# time_taken = end - start
		# print('Buy took ',time_taken,' seconds\n')
		result = buy_request.json()['Result'] # Result denotes whether the buy on the catalog server was successful or not
		if result == '1':
			resp['Result'] = '1'
			new_row = {'ItemNumber' : resp['ItemNumber'], 'Title' : resp['Title'], 'Cost' : resp['Cost'], 'Timestamp' : datetime.now()}
			fieldnames = ['ItemNumber', 'Title','Cost','Timestamp']
			with open('orders.csv', 'a') as csvfile: # Write the updated stock value to the catalog file
			    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
			    writer.writerow(new_row)
		else:
			resp['Result'] = '0'
	else:
		resp['Result'] = '0'
	return jsonify(resp)

if __name__ == "__main__":
	with open('config.json') as json_file:
		data = json.load(json_file)
		portnum = data['OrderServer'].split(":")[1] # Read port number from config file
	orderServer.run(host = '0.0.0.0',port = portnum,debug = False,threaded = True)
