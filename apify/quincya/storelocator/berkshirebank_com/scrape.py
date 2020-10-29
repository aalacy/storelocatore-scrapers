from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = 'https://hosted.where2getit.com/berkshire/ajax?&xml_request=%3Crequest%3E%3Cappkey%3EB538A6EC-5E9B-11E2-B47F-11FE86C790F0%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Climit%3E500%3C%2Flimit%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3ENew+York%3C%2Faddressline%3E%3Clongitude%3E-74.0059728%3C%2Flongitude%3E%3Clatitude%3E40.7127753%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E200%3C%2Fsearchradius%3E%3Cwhere%3E%3Cor%3E%3Cbranch%3E%3Ceq%3E1%3C%2Feq%3E%3C%2Fbranch%3E%3Catm%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fatm%3E%3Cother%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fother%3E%3Cinsurancegroup%3E%3Cin%3E%3C%2Fin%3E%3C%2Finsurancegroup%3E%3Clending%3E%3Cin%3E%3C%2Fin%3E%3C%2Flending%3E%3C%2For%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E'

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []

	items = base.find_all("poi")
	locator_domain = "berkshirebank.com"

	for item in items:
		if item.find("atm").text == "1":
			continue
		location_name = item.find("name").text.strip()
		street_address = (item.find("address1").text.strip() + " " + item.find("address2").text).strip()
		if "Corporate Headquarters" in street_address:
			street_address = street_address.replace("Corporate Headquarters","").strip()
			location_name = location_name + " Corporate Headquarters"
		city = item.find("city").text.strip()
		state = item.find("state").text.strip()
		zip_code = item.find("postalcode").text.strip()
		country_code = item.find("country").text.strip()
		store_number = item.find("uid").text.replace("-","").strip()
		location_type = "<MISSING>"
		phone = item.find("phone").text.strip()
		hours_of_operation = item.find("lobbyhours").text.replace("<br>"," ").replace("  "," ").split("Call")[0].strip()
		latitude = item.find("latitude").text.strip()
		longitude = item.find("longitude").text.strip()

		data.append([locator_domain, "<MISSING>", location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
