from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import re

from random import randint


def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.norms.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	
	req = session.get(base_link, headers = HEADERS)
	time.sleep(randint(1,2))
	
	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	all_scripts = base.find_all('script')
	for script in all_scripts:
		if "latlng" in str(script):
			js = str(script)
			break

	starts = re.findall(r'{"id":[0-9]+,',js)

	data = []
	poi_raw = []
	for i in range(0, len(starts)):
		try:
			poi_raw.append(js[js.find(starts[i]):js.find(starts[i+1])].strip())
		except:
			poi_raw.append(js[js.find(starts[i]):js.find('"thumbnail"',js.find(starts[i]))].strip())

	for item in poi_raw:
		item = item.replace("\\","")
		if "COMING SOON" in item:
			continue
		
		locator_domain = "norms.com"
		
		location_name = re.findall('title":.+,"lat', item)[0].replace('title":','').split(",")[0].replace('"',"")
		print(location_name)
		
		zip_code = re.findall('zip":.+,"tags"', item)[0].replace('zip":"','').split(",")[0].replace('"',"")

		raw_address = re.findall('<br />.+'+zip_code, item)[0][6:]
		street_address = raw_address[:raw_address.rfind("rn")].strip()
		city = raw_address[raw_address.rfind("rn")+2:raw_address.rfind(",")].strip()
		state = raw_address[raw_address.rfind(",")+1:raw_address.rfind(" ")].strip()
		country_code = "US"

		try:
			phone = re.findall("[[(\d)]{3}-[\d]{3}-[\d]{4}", item)[0]
		except:
			phone = "<MISSING>"

		location_type = "<MISSING>"
		try:
			hours_of_operation = re.findall('Hours:.+</p', item)[0].replace('Hours:','')[:-3].strip()
		except:
			try:
				hours_of_operation = re.findall('HOURS:.+</p', item)[0].replace('HOURS:','')[:-3].strip()
			except:
				hours_of_operation = "<MISSING>"
				
		store_number = item[item.find(":")+1:item.find(",")].strip()

		geo = re.findall(r'\[[0-9]+\.[0-9]+,-[0-9]+\.[0-9]+\]', item)[0].replace("[","").replace("]","").split(",")
		latitude = geo[0]
		longitude = geo[1]

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()

