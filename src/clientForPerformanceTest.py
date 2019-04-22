import requests
import json
import time
import sys

if __name__ == "__main__":
	with open('config.json') as json_file:
		data = json.load(json_file)
		frontEndIP = data['FrontEndServer'].split(":")[0]
		frontEndPort = data['FrontEndServer'].split(":")[1]
	url = 'http://' + frontEndIP + ':' + frontEndPort + '/'

	## sequential search
	time_taken = 0.0
	for i in range(1000):
		start_time = time.time()
		r = requests.get(url + 'search/DistributedSystems')
		end_time = time.time()
		time_taken += end_time - start_time
	time_taken /= 1000
	print('Average time per search query after doing 1000 sequential search queries is : ',time_taken,' seconds\n')

	## sequential lookups
	time_taken = 0.0
	for i in range(1000):
		start_time = time.time()
		r = requests.get(url + 'lookup/1')
		end_time = time.time()
		time_taken += end_time - start_time
	time_taken /= 1000
	print('Average time per lookup after doing 1000 sequential lookups is : ' , time_taken , ' seconds\n')

	## sequential buys
	time_taken = 0.0
	for i in range(1000):
		start_time = time.time()
		r = requests.get(url + 'buy/1')
		end_time = time.time()
		time_taken += end_time - start_time
	time_taken /= 1000
	print('Average time per buy after doing 1000 sequential buys is : ' , time_taken , ' seconds\n')