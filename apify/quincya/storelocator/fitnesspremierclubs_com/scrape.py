from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
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
	
	base_link = "https://www.fitnesspremierclubs.com"

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

	data = []

	items = base.find(id="menu-item-275").ul.find_all("a")
	locator_domain = "fitnesspremierclubs.com"

	for item in items:

		link = item['href']
		req = session.get(link, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")			
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')
		
		location_name = base.h1.text.strip()

		try:
			club_number = re.findall(r'clubNumber=(\d+)', str(base))[0]
		except:
			continue
		print(link)
		club_url = 'https://mico.myiclubonline.com/iclub/club/getClubExternal.htm?club=%s&_=1564200271209' % club_number
		add_req = session.get(club_url, headers = HEADERS)
		address_base = str(BeautifulSoup(add_req.text,"lxml"))
		add_json = json.loads(address_base[address_base.find("{"):address_base.rfind("}")+1].replace("\n",""))

		street_address = (add_json["address1"] + " " + add_json['address2']).strip()
		city = add_json["city"]
		state = add_json["state"]
		zip_code = add_json["zip"]
		country_code = "US"
		store_number = add_json["number"]
		location_type = base.find_all(class_="panel-grid-cell")[1].text.replace("FEATURES","").strip().replace("\n",", ")
		phone = add_json["phone"].replace(" Ext.","").strip()
		hours_of_operation = base.find_all(class_="panel-grid-cell")[2].p.text.replace(" –\xa0","-").replace("\n"," ")

		try:
			map_link = base.find("iframe")['src']
			lat_pos = map_link.rfind("!3d")
			latitude = map_link[lat_pos+3:map_link.find("!",lat_pos+5)].strip()
			lng_pos = map_link.find("!2d")
			longitude = map_link[lng_pos+3:map_link.find("!",lng_pos+5)].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
