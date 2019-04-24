from flask import Flask,jsonify,request
import csv
import threading
import json
import requests
import datetime
import time

lock = threading.Lock()
catalogServer2 = Flask(__name__)
with open('config.json') as json_file:
    data = json.load(json_file)
    catalogIP1 = data['CatalogServer1'].split(":")[0] # IP and port number of the catalog server, useful to trigger the restock method
    catalogPort1 = data['CatalogServer1'].split(":")[1]
    frontEndIP = data['FrontEndServer'].split(":")[0] # IP and port number of the catalog server, useful to trigger the restock method
    frontEndPort = data['FrontEndServer'].split(":")[1]
    catalogIP2 = data['CatalogServer2'].split(":")[0] # IP and port number of the catalog server, useful to trigger the restock method
    catalogPort2 = data['CatalogServer2'].split(":")[1]

@catalogServer2.route("/")
def index():
    return "Welcome to Pygmy.com, the world's best book store!"

@catalogServer2.route("/search/<string:topic>/",methods=['GET'])
def search(topic):
    '''This method searches the catalog for books belonging to the specified topic, and returns them in a JSON object'''
    d,d2 = {},{}
    with open('catalog2.csv') as csvfile: # Read catalog file and check for matches with the specified topic
        catalogreader = csv.DictReader(csvfile)
        for row in catalogreader:
            if row['Topic'] == topic:
                d[row['Title']] = row['ItemNumber']
    d2['items'] = d
    return jsonify(d2)

@catalogServer2.route("/lookup/<string:item_number>/",methods=['GET'])
def lookup(item_number):
    '''This method looks up the catalog for a book corresponding to a specified item number, and returns its information in a JSON object.
    If there is no book corresponding to the specified item number, then it returns an empty object.'''
    d = {}
    with open('catalog2.csv') as csvfile: # Read catalog file and check for matches with the specified item number
        catalogreader = csv.DictReader(csvfile)
        for row in catalogreader:
            if row['ItemNumber'] == item_number:
                d['ItemNumber'] = row['ItemNumber']
                d['Title'] = row['Title']
                d['Topic'] = row['Topic']
                d['Cost'] = row['Cost']
                d['Stock'] = row['Stock']
                d['Time'] = datetime.datetime.now()

    return jsonify(d)

@catalogServer2.route("/buy/",methods=['POST'])
def buy():
    ''' This method buys a book with a specified item number. The item number is specified in the incoming JSON object along with the request.
    This method first acquires a lock, so that two buys cannot happen at the same time. Once acquired, it reads the catalog and checks if the
    specified book is in stock. If it is, it decrements its stock, and writes the updated stock value to the catalog file. If out of stock,
    it does not decrement the stock. Then, it releases the lock. It returns a JSON object containing the result of the method, whether it was
    successful or not. '''
    posted_json = request.get_json()
    item_number = posted_json['ItemNumber']
    d = {'Result':'0'}
    new_rows = []
    urlCatalog1 = ''
    urlFrontEnd = ''
    lock.acquire() # Acquire lock
    try:
        with open('catalog2.csv','r') as csvfile: # Read catalog file, check for match with the specified item number and check its stock
            catalogreader = csv.DictReader(csvfile)
            for row in catalogreader:
                # print(row)
                new_row = dict(row)
                if row['ItemNumber'] == item_number and int(row['Stock']) > 0: # If match and in stock, decrement stock value
                    new_row['Stock'] = str(int(row['Stock']) - 1)
                    d['Result'] = '1'
                    urlCatalog2 = 'http://' + catalogIP1 + ':' + catalogPort1 + '/update/' + row['ItemNumber'] + ':' + new_row['Stock']
                    urlFrontEnd = 'http://' + frontEndIP + ':' + frontEndPort + '/invalidate/' + row['ItemNumber']
                    print('reached here')
                new_rows.append(new_row)

            fieldnames = ['ItemNumber', 'Title','Topic','Cost','Stock']
            with open('catalog2.csv', 'w') as csvfile: # Write changes to catalog file
                writer = csv.DictWriter(csvfile,fieldnames = fieldnames)
                writer.writeheader()
                writer.writerows(new_rows)
            r_frontEnd = requests.delete(urlFrontEnd)
            r_catalog2 = requests.put(urlCatalog2)
    except:
        print("File error occured\n")
    finally:
        lock.release() # Release lock
    return jsonify(d)

def checkAndRestock():
    ''' This method runs in a separate thread, and every 30 seconds triggers the restock method of this catalog server. '''
    print('Restock thread started')
    while True:
        time.sleep(30)
        url = 'http://' + catalogIP2 + ':' + catalogPort2 + '/restock/'
        r = requests.post(url)

@catalogServer2.route("/restock/",methods=['POST'])
def restock():
    ''' This method checks the catalog file, and if any item is found to be out of stock, it restocks it.'''
    change = False
    with open('catalog2.csv','r') as csvfile: # Read catalog file
        catalogreader = csv.DictReader(csvfile)
        for row in catalogreader:
            if int(row['Stock']) <= 0: # If found item out of stock, set the change flag to true
                change = True
                break
    if change: # Execute only if a change needs to be made
        new_rows = []
        urlCatalog2 = ''
        urlFrontEnd = ''
        lock.acquire() # Acquire the lock. This is the same lock used by the buy method, as we don't want a buy to happen at the same time as
        # a restock. It can lead to race conditions.
        try:
            with open('catalog2.csv','r') as csvfile:
                catalogreader = csv.DictReader(csvfile)
                for row in catalogreader:
                    new_row = dict(row)
                    if int(row['Stock']) <= 0: # If found item out of stock, restock it.
                        new_row['Stock'] = '50'
                        print('Restocked the book : ' + row['Title'])
                        urlCatalog2 = 'http://' + catalogIP2 + ':' + catalogPort2 + '/update/' + row['ItemNumber'] + ':' + new_row['Stock']
                        urlFrontEnd = 'http://' + frontEndIP + ':' + frontEndPort + '/invalidate/' + row['ItemNumber']
                    new_rows.append(new_row)
            fieldnames = ['ItemNumber', 'Title','Topic','Cost','Stock']
            with open('catalog2.csv', 'w') as csvfile: # Write changes to catalog file
                writer = csv.DictWriter(csvfile,fieldnames = fieldnames)
                writer.writeheader()
                writer.writerows(new_rows)
            r_frontEnd = requests.delete(urlFrontEnd)
            r_catalog2 = requests.put(urlCatalog2)
        except:
            print("File error occured\n")
        finally:
            lock.release() # Release the lock
    ret_dict = {'Restocked' : change}
    return jsonify(ret_dict)

@catalogServer2.route("/update/<string:item_and_stock>/",methods=['PUT'])
def update(item_and_stock):
    item_number = item_and_stock.split(":")[0]
    new_stock = item_and_stock.split(":")[1]
    new_rows = []
    lock.acquire()
    try:
        with open('catalog2.csv','r') as csvfile:
            catalogreader = csv.DictReader(csvfile)
            for row in catalogreader:
                new_row = dict(row)
                if row['ItemNumber'] == item_number:
                    new_row['Stock'] = new_stock
                    print('Updating stock for ' + row['Title'] + ' to ' + new_stock)
                new_rows.append(new_row)
        fieldnames = ['ItemNumber', 'Title','Topic','Cost','Stock']
        with open('catalog2.csv', 'w') as csvfile: # Write changes to catalog file
            writer = csv.DictWriter(csvfile,fieldnames = fieldnames)
            writer.writeheader()
            writer.writerows(new_rows)
    except:
        print("File error occured\n")
    finally:
        lock.release() # Release the lock
    ret_dict = {'updated' : True}
    return jsonify(ret_dict)

if __name__ == "__main__":
    with open('config.json') as json_file:
        data = json.load(json_file)
        portnum = data['CatalogServer2'].split(":")[1]
    serverThread = threading.Thread(target = catalogServer2.run,kwargs = {'host' : '0.0.0.0','port' : portnum,'threaded':True}) # This is the server thread
    restockThread = threading.Thread(target = checkAndRestock) # This is the restock thread
    serverThread.start()
    restockThread.start()
