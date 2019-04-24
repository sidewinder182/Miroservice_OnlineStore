from flask import Flask,jsonify,request
import json
import requests
import csv
import traceback
# with open('config.json') as json_file:
# 	data = json.load(json_file)
# 	catalogIP1 = data['CatalogServer1'].split(":")[0] # IP, port number of the catalog server
# 	catalogPort1 = data['CatalogServer1'].split(":")[1]
# # url = 'http://' + orderIP1 + ':' + orderPort1
# # try:
# # 	r = requests.get(url)
# # except requests.exceptions.ConnectionError:
# #     print('occured')
# flags = {}
# flags['catalog1'] = 1
# flags['catalog2'] = 1
# flags['order1'] = 1
# flags['order2'] = 1
# r = requests.get('http://' + catalogIP1 + ':' + catalogPort1 + '/lookup/1/')
# print(r.json())
reader = csv.reader(open("orders1.csv"))
print(type(reader))
