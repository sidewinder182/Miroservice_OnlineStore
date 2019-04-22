from flask import Flask, jsonify, Request
import csv
import requests
import json

if __name__ == "__main__":
	print("Welcome to Pygmy.com, the world's smallest book store!\n")
	## IP and port number of the frontEndServer are first fetched from the config file
	with open('config.json') as json_file:
		data = json.load(json_file)
		frontEndIP = data['FrontEndServer'].split(":")[0]	#IP of frontEndServer
		frontEndPort = data['FrontEndServer'].split(":")[1]	#port number on which frontEndServer is listening on
	url = 'http://' + frontEndIP + ':' + frontEndPort + '/'
	while(True):
		selection_main = input("Please select one of the following indices:\n 1. Search for a topic \n 2. Lookup a title with its item number \n 3. Buy a title\n")
		## This section executes the interface flow of a search request
		if(selection_main == '1'):
			while(True):
				selection_topic = input("Please choose the topic you want to search for:\n 1. Distributed Systems \n 2. Graduate School\n 3. Misc \n  Or press b to return to main menu\n")
				if selection_topic == '1':
					r = requests.get(url + 'search/DistributedSystems')
					response_client = r.json()
					print('Results :')
					for key, value in response_client['items'].items():
						print(key + " : " + value)
					print("")
					break
				elif selection_topic == '2':
					r = requests.get(url + 'search/GraduateSchool')
					response_client = r.json()
					print('Results :')
					for key, value in response_client['items'].items():
						print(key + " : " + value)
					print("")
					break
				elif selection_topic == '3':
					r = requests.get(url + 'search/Misc')
					response_client = r.json()
					print('Results :')
					for key, value in response_client['items'].items():
						print(key + " : " + value)
					print("")
					break
				elif selection_topic == 'b':
					break
				else:
					print("Invalid search. Please enter an option number\n")
					continue
		## This section executes the interface flow of a lookup request
		elif selection_main == '2':
			while(True):
				selection_lookup = input("Please enter an item number you wish to lookup: \nIf you wish to go to the main menu press b\n")
				if selection_lookup == 'b':
					break
				else:
					r = requests.get(url + 'lookup/' + selection_lookup)
					response_client = r.json()
					if response_client:
						for key, value in response_client.items():
							print(key + " : " + value)
						print("")
						continue
					else:
						print("Invalid item number. Retry\n")
						continue

		## This section executes the interface flow of a buy request
		elif selection_main == '3':
			while(True):
				selection_buy = input("Please enter an item number you wish to buy: \nIf you wish to go to the main menu press b\n")
				if selection_buy == 'b':
					break
				else:
					r = requests.get(url + 'buy/' + selection_buy)
					response_client = r.json()
					if not response_client:
						print("Invalid item number. Retry\n")
						continue
					elif response_client['Result'] == '0':
						print("Buy failed. Item out of stock, please try again after a few seconds\n")
					else:
						print('Bought book ' + response_client['Title'])
						break
