from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://services.anthology-digital.com/locations/dil?lat=31.9685988&lng=-99.9018131&premierGoldFlag=0&radius=10000&code=k&limit=1000"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")
	script = base.text.replace('\n', '').strip()
	stores = json.loads(script)["dealers"]
		
	all_ids = []

	for store in stores:
		all_ids.append(store["obj"]["dealer_code"])

	data = []
	total_links = len(all_ids)
	locator_domain = "kenworth.com"
	for i, store_id in enumerate(all_ids):
		print("Link %s of %s" %(i+1,total_links))
		link = "https://www.kenworth.com/dealers/dealer?d=" + store_id
		print(link)
		api_link = "https://services.anthology-digital.com/locations/dealers?dealer_code=%s&callback=?" %store_id
		req = session.get(api_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")
		store = json.loads(base.text)

		location_name = store["Dealership_Name"].strip()
		street_address = store["Address_Physical"].strip()
		city = store["City"].strip()
		state = store["State_Province"].strip()
		
		zip_code = store["Zip_Postal_Code_Physical"].strip()
		if " " in zip_code:
			country_code = "CA"
			if zip_code == "S9H 5RH":
				zip_code = "S0N 2Y0"
				state = "SK"
				city = "Swift Current"
		else:
			country_code = "US"
		if state == "NF":
			state = "NL"

		store_number = store_id
		phone = store["Phone"]
		if not phone:
		  phone = "<MISSING>"

		location_type = store["Status_Description"].strip()
		if not location_type:
		  location_type = "<MISSING>"

		hours_of_operation = ""
		if "x" in store["24hrs_Dealer"].lower():
			hours_of_operation = "24 Hours Daily"
		else:
			try:
				if "24 Hours" in store["Monday_Close_Sales"]:
					mon = "Mon: 24 Hours"
				else:
					mon = "Mon: " + store["Monday_Open_Sales"] + " - " + store["Monday_Close_Sales"]
			except:
				mon = "Mon: Closed"
			try:
				if "24 Hours" in store["Tuesday_Close_Sales"]:
					tue = " Tue: 24 Hours"
				else:
					tue = " Tue: " + store["Tuesday_Open_Sales"] + " - " + store["Tuesday_Close_Sales"]
			except:
				tue = " Tue: Closed"
			try:
				if "24 Hours" in store["Wednesday_Close_Sales"]:
					wed = " Wed: 24 Hours"
				else:
					wed = " Wed: " + store["Wednesday_Open_Sales"] + " - " + store["Wednesday_Close_Sales"]
			except:
				wed = " Wed: Closed"
			try:
				if "24 Hours" in store["Thursday_Close_Sales"]:
					thu = " Thu: 24 Hours"
				else:
					thu = " Thu: " + store["Thursday_Open_Sales"] + " - " + store["Thursday_Close_Sales"]
			except:
				thu = " Thu: Closed"
			try:
				if "24 Hours" in store["Friday_Close_Sales"]:
					fri = " Fri: 24 Hours"
				else:
					fri = " Fri: " + store["Friday_Open_Sales"] + " - " + store["Friday_Close_Sales"]
			except:
				fri = " Fri: Closed"
			try:
				if "24 Hours" in store["Saturday_Close_Sales"]:
					sat = " Sat: 24 Hours"
				else:
					sat = " Sat: " + store["Saturday_Open_Sales"] + " - " + store["Saturday_Close_Sales"]
			except:
				sat = " Sat: Closed"
			try:
				if "24 Hours" in store["Sunday_Close_Sales"]:
					sun = " Sun: 24 Hours"
				else:
					sun = " Sun: " + store["Sunday_Open_Sales"] + " - " + store["Sunday_Close_Sales"]
			except:
				sun = " Sun: Closed"

			hours_of_operation = mon + tue + wed + thu + fri + sat + sun

		if hours_of_operation.count("Closed") == 7:
			try:
				mon = "Mon: " + store["Monday_Open_Parts"] + " - " + store["Monday_Close_Parts"]
			except:
				mon = "Mon: Closed"
			try:
				tue = " Tue: " + store["Tuesday_Open_Parts"] + " - " + store["Tuesday_Close_Parts"]
			except:
				tue = " Tue: Closed"
			try:
				wed = " Wed: " + store["Wednesday_Open_Parts"] + " - " + store["Wednesday_Close_Parts"]
			except:
				wed = " Wed: Closed"
			try:
				thu = " Thu: " + store["Thursday_Open_Parts"] + " - " + store["Thursday_Close_Parts"]
			except:
				thu = " Thu: Closed"
			try:
				fri = " Fri: " + store["Friday_Open_Parts"] + " - " + store["Friday_Close_Parts"]
			except:
				fri = " Fri: Closed"
			try:
				sat = " Sat: " + store["Saturday_Open_Parts"] + " - " + store["Saturday_Close_Parts"]
			except:
				sat = " Sat: Closed"
			try:
				sun = " Sun: " + store["Sunday_Open_Parts"] + " - " + store["Sunday_Close_Parts"]
			except:
				sun = " Sun: Closed"

			hours_of_operation = mon + tue + wed + thu + fri + sat + sun

		if not hours_of_operation:
			hours_of_operation = "<MISSING>"

		latitude = store["Latitude"]
		longitude = store["Longitude"]

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
