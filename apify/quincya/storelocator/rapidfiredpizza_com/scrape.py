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
	
	base_link = "https://rapidfiredpizza.com/location-data/getlocations.php"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	HEADERS = {
			'authority': 'rapidfiredpizza.com',
			'method': 'GET',
			'path': '/location-data/getlocations.php',
			'scheme': 'https',
			'accept': 'text/plain, */*; q=0.01',
			'accept-encoding': 'gzip, deflate, br',
			'accept-language': 'en-US,en;q=0.9',
			'content-length': '15',
			'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'cookie': '_ga=GA1.2.697583639.1605159901; _fbp=fb.1.1605159901008.840266221; _gid=GA1.2.1263464095.1605858583',
			'origin': 'https://rapidfiredpizza.com',
			'referer': 'https://rapidfiredpizza.com/locations',
			'sec-fetch-dest': 'empty',
			'sec-fetch-mode': 'cors',
			'sec-fetch-site': 'same-origin',
			'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36',
			'x-requested-with': 'XMLHttpRequest'
		}


	data = []
	payload = {'getstores': 'true'}

	response = session.post(base_link,headers=HEADERS,data=payload)
	base = BeautifulSoup(response.text,"lxml")

	items = base.find_all(class_="location-details location-small col-sm-4")
	locator_domain = "rapidfiredpizza.com"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	for item in items:
		if "coming soon" in str(item).lower():
			continue
		link = item.a["href"]
		location_name = item.a.text.strip()
		
		raw_address = list(item.p.find_all("a")[-1].stripped_strings)
		street_address = " ".join(raw_address[:-1]).strip()
		city_line = raw_address[-1].strip().split(",")
		city = city_line[0].strip()
		state = city_line[-1].strip().split()[0].strip()
		zip_code = city_line[-1].strip().split()[1].strip()
		country_code = "US"
		location_type = "<MISSING>"
		phone = item.p.a.text.strip()
		hours_of_operation = " ".join(list(item.p.stripped_strings)[3:])

		req = session.get(link, headers=HEADERS)
		base = BeautifulSoup(req.text,"lxml")

		store_number = base.find(id="landhere").div["id"].split("store")[1]
		
		try:
			map_link = item.p.find_all("a")[-1]["href"]
			req = session.get(map_link)
			map_link = req.url
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
