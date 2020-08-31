import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import sgzip
import json
# import phonenumbers
session = SgRequests()

def write_output(data):
	with open('data.csv', mode='w', newline='') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
						 "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
		# Body
		for row in data:
			writer.writerow(row)
def fetch_data():
	headers = {
			'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
		}
	locator_domain = 'https://www.valvoline.com/'
	addresses = []
	search = sgzip.ClosestNSearch()
	search.initialize(country_codes= ["US"])
	MAX_RESULTS = 500
	MAX_DISTANCE = 25
	current_result_len = 0
	zip_code = search.next_zip()
	while zip_code:
		result_coords = []
		# print("zip_code === " + str(zip_code))
		# print("remaining zip =====" + str(search.zipcodes_remaining()))
		headers = {
			'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
			'content-type' : 'application/x-www-form-urlencoded'
		}
		data = "scController=StoreLocatorUS&scAction=SubmitLocation&Zip="+str(zip_code)+"&All-hidden=&Express-hidden=checked&HD-hidden=&VIOC-hidden=checked&Other-hidden=&All-hidden-retail=&HD-hidden-retail="
		r = session.post('https://www.valvoline.com/store-locator', headers=headers,data=data)
		soup = BeautifulSoup(r.text,"lxml")
		li = soup.find("li",{"data-content":"servicesLocations"})
		
		if li.find("div",class_="location"):
			current_result_len = len(li.find_all("div",class_='location'))
			for loc in li.find_all("div",class_='location'):
				latitude = loc["data-latitude"]
				longitude= loc["data-longitude"]
				if "Valvoline Express Care™" in loc["data-name"].strip() :
					location_type = "Valvoline Express Care™"
				elif "Valvoline Instant Oil Change™" in loc["data-name"].strip():
					location_type = "Valvoline Instant Oil Change™"
				else:
					continue
				city_state_zipp = loc["data-location"].split(",")
				city = city_state_zipp[0].strip().capitalize()
				state = city_state_zipp[1].strip()
				zipp = city_state_zipp[-1].strip()
				country_code = "US"
				location_name =	loc.find("h5",class_="location-title").text.capitalize().strip()
				full_address = list(loc.find("p",class_="location-address").stripped_strings)
				street_address = full_address[0].strip().capitalize()
				phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(" ".join(full_address)))
				if phone_list:
					phone= phone_list[0]
				else:
					phone="<MISSING>"
				try:
					hours_of_operation = " ".join(list(loc.find("p",class_="location-hours").stripped_strings)).replace("Hours:","").strip()
				except:
					hours_of_operation="<MISSING>"
				try:
					page_url= loc.find("a",class_="gtm-locator-storeLink")["href"]
				except:
					page_url="<MISSING>"
				try:
					store_number = page_url.split("-")[-1].split(".")[0].strip()
				except:
					store_number="<MISSING>"
				result_coords.append((latitude,longitude))
				store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
						 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

				if str(store[2]+" "+store[-5]) not in addresses :
					addresses.append(str(store[2]+" "+store[-5]))

					store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

					# print("data = " + str(store))
					# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
					yield store
		if current_result_len < MAX_RESULTS:
			# print("max distance update")
			search.max_distance_update(MAX_DISTANCE)
		elif current_result_len == MAX_RESULTS:
			# print("max count update")
			search.max_count_update(result_coords)
		else:
			raise Exception("expected at most " + str(MAX_RESULTS) + " results")
		zip_code = search.next_zip()
def scrape():
	data = fetch_data()
	write_output(data)
scrape()
