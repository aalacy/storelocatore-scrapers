from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
import json
import time
from random import randint

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "featured_services"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.selectphysicaltherapy.com//sxa/search/results/?s={D779ED53-C5AD-46DB-AA4F-A2F78783D3B1}|{D779ED53-C5AD-46DB-AA4F-A2F78783D3B1}&itemid={29966A67-0D55-4E7D-968A-88849BF32EF3}&sig=&autoFireSearch=true&v={99A28EFC-3607-4C5B-8D33-D37C5B70E2EF}&p=3000&g=&o=Distance,Ascending"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		base = BeautifulSoup(req.text,"lxml")
		print("Got today page")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	new_base = str(base).replace("</li><li>",",").replace("<br/>",",,").replace('<img src="h'," ,,DDD").replace('"/>',"DDD,,").replace("Request an Appointment",",,").replace("Featured Services",",,")
	final_base = BeautifulSoup(new_base,"lxml")
	store = json.loads(final_base.text)["Results"]

	data = []
	for item in store:
		locator_domain = "selectphysicaltherapy.com"

		raw_data = item["Html"].split(",,")
		location_name = raw_data[0].strip()

		print (location_name)
		location_type = raw_data[-3].replace("DDDt","ht").replace("DDD","")

		if len(raw_data) == 7:
			street_address = raw_data[1].strip() + " " + raw_data[2].strip()
			city_line = raw_data[3].strip()
		else:
			street_address = raw_data[1].strip()
			city_line = raw_data[2].strip()

		city = city_line[:city_line.find(',')].strip()
		state = city_line[city_line.find(',')+1:city_line.find(',')+5].strip() 
		zip_code = city_line[city_line.find('(')-6:city_line.find('(')].strip()
		country_code = "US"

		store_number = "<MISSING>"
		phone = city_line[city_line.find("("):city_line.find("\r")].strip()
		if phone == "(817) 333-018":
			phone = "(817) 333-0181"
		hours = raw_data[-2].replace("Hours","").replace("PM","PM ").replace("Closed","Closed ").strip()
		hours_of_operation = re.sub(' +', ' ', hours)

		if not hours_of_operation:
			hours_of_operation = "<MISSING>"
		
		latitude = item["Geospatial"]["Latitude"]
		longitude = item["Geospatial"]["Longitude"]

		feat_services = raw_data[-1].strip()

		if "," not in feat_services:
			feat_services = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation, feat_services])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
