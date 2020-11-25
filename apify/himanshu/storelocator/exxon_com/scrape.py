import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('exxon_com')




session = SgRequests()

def write_output(data):
	with open('data.csv', mode='w',newline = "") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
	search.initialize(country_codes= ["US"])
	MAX_RESULTS = 250
	MAX_DISTANCE = 25
	current_result_len = 0
	coords = search.next_coord()

	addresses = []

	while coords:
		result_coords = []
		# logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
		# logger.info(coords[0],coords[1])
		base_url = "https://www.exxon.com/en/api/locator/Locations?Latitude1="+str(coords[0])+"&Latitude2="+str(coords[0]+1)+"&Longitude1="+str(coords[1])+"&Longitude2="+str(coords[1]+1)+"&DataSource=RetailGasStations&Country=US"
		# base_url = "https://www.exxon.com/en/find-station/?longitude1="+str(coords[1])+"&longitude2="+str(coords[1]-1)+"&latitude1="+str(coords[0])+"&latitude2="+str(coords[0]-1)
		# logger.info(base_url)
		r = session.get(base_url).json()
		return_main_object = []
		current_result_len = len(r)
		for location in r:
			
			page_url = "https://www.exxon.com/en/find-station/"+location['City'].lower().replace(" ","").strip()+"-"+location["StateProvince"].lower().strip()+"-"+location["DisplayName"].lower().replace(" ","").replace("#","-").strip()+"-"+location["LocationID"].strip()
			result_coords.append((location['Latitude'],location['Longitude']))
			
			store = []
			store.append("https://www.exxon.com")
			store.append(location['DisplayName'].strip())
			store.append(location['AddressLine1'].strip())
			store.append(location['City'].strip())
			store.append(location['StateProvince'].strip())
			store.append(location['PostalCode'].strip())
			if location['Country']=='United States':
				store.append('US')
			else:
				store.append(location['Country']) 
			store.append(location['LocationID'].strip())
			if location['Telephone']:
				store.append(location['Telephone'].strip())
			else: 
				store.append("<MISSING>")
			store.append("exxon")
			store.append(location['Latitude'])
			store.append(location['Longitude'])
			if location['WeeklyOperatingHours']:
				 store.append(location['WeeklyOperatingHours'].replace('<br/>',','))
			else: 
				store.append("<MISSING>")
			store.append(page_url)	
			if (str(store[2])+str(store[-1])) in addresses:
				continue
			addresses.append(str(store[2])+str(store[-1]))
			store = [str(x).strip() if x else "<MISSING>" for x in store]
			yield store
			# logger.info(store)
		if current_result_len < MAX_RESULTS:
			# logger.info("max distance update")
			search.max_distance_update(MAX_DISTANCE)
		elif current_result_len == MAX_RESULTS:
			# logger.info("max count update")
			search.max_count_update(result_coords)
		else:
			raise Exception("expected at most " + str(MAX_RESULTS) + " results")
		coords = search.next_coord()
def scrape():
	data = fetch_data()
	write_output(data)

scrape()
