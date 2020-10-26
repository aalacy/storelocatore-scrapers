from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	data = []
	for page_num in range(1,4):

		base_link = ("https://www.bakedbymelissa.com/rest/V1/storelocator/search/?searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bfield%5D=lat\
					&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bvalue%5D=&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bcondition_type%5D=eq\
					&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bfield%5D=lng&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bvalue%5D=&searchCriteria%\
					5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bfield%5D=country_id\
					&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bvalue%5D=&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bcondition_type%5D=eq\
					&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bfield%5D=store_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bvalue%5D=1\
					&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bfield%5D=region_id\
					&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bfield%5D=region\
					&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bvalue%5D=New+York&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bcondition_type%5D=eq\
					&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bfield%5D=distance&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bvalue%5D=25\
					&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B7%5D%5Bfield%5D=onlyLocation\
					&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B7%5D%5Bvalue%5D=0&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B7%5D%5Bcondition_type%5D=eq\
					&searchCriteria%5Bcurrent_page%5D=" + str(page_num) + "&searchCriteria%5Bpage_size%5D=6&_=1595392284554").replace("\t","")

		req = session.get(base_link, headers = HEADERS)
		time.sleep(randint(1,2))

		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		stores = json.loads(base.text)['items']

		for store in stores:		
			locator_domain = "bakedbymelissa.com"
			location_name = store['name']
			print(location_name)

			street_address = store['street']
			city = store['city']
			state = store['region']
			zip_code = store['postal_code']

			country_code = "US"
			store_number = "<MISSING>"
			
			location_type = "<MISSING>"
			phone = store['phone']

			hours_of_operation = store['description'].replace('\r\n',' ')
			latitude = store['lat']
			longitude = store['lng']
			page_url = "https://www.bakedbymelissa.com/storelocator"

			data.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()

