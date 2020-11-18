from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('oldcountrybuffet_com')


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
	locator_domain = "oldcountrybuffet.com"
	link = "http://www.oldcountrybuffet.com/locator/"
	
	for i in range(52):

		base_link = "http://www.oldcountrybuffet.com/wp-admin/admin-ajax.php?action=usahtml5map_state_info&map_id=0&sid=%s" %i
		logger.info(base_link)

		req = session.get(base_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		items = base.find_all(class_="collapseomatic_content")
		if len(items) == 0:
			continue

		for item in items:

			try:
				location_name = item.div.div.text.strip()
			except:
				pass

			if "old country" not in location_name.lower():
				continue

			street_address = list(item.stripped_strings)[1].strip()
			if "Home Town AYCE" in street_address:
				continue
				
			city_line = list(item.stripped_strings)[2].strip().split(",")
			city = city_line[0].strip()
			state = city_line[-1].strip().split()[0].strip()
			zip_code = city_line[-1].strip().split()[1].strip()
			country_code = "US"
			store_number = item["id"].split("-")[1]
			location_type = "<MISSING>"

			try:
				phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", str(item))[0]
			except:
				phone = "<MISSING>"

			hours_of_operation = " ".join(list(item.p.stripped_strings)).replace("HOURS","").encode("ascii", "replace").decode().replace("?","-").strip()

			try:
				map_link = item.a['href']
				at_pos = map_link.rfind("!3d")
				latitude = map_link[at_pos+3:map_link.rfind("!")].strip()
				longitude = map_link[map_link.find("!4d", at_pos)+3:].strip()
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"

			data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
