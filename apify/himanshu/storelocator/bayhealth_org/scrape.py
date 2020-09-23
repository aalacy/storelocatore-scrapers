import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time



session = SgRequests()


def write_output(data):
	with open('data.csv', mode='w',newline="") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
						 "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
		# Body
		for row in data:
			writer.writerow(row)


def fetch_data():
	addressess = []
	payload = '{"Query":"_templatename:Location AND is_crawlable_b:true","Page":1,"NumberOfResults":100,"Sort":"item_name_s asc"}'
	headers = {
	'accept': 'application/json, text/plain, */*',
	'content-type': 'application/json;charset=UTF-8',
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
	}
	base_url = "https://www.bayhealth.org"
	location_url = "https://www.bayhealth.org/api/search"

	json_data = session.post(location_url,headers=headers,data=payload).json()
	load_data = json.loads(json_data)
	for val in load_data['Results']:
		page_url = base_url+val['Path'].replace(" ","%20")
		# print(page_url)
		r = session.get(page_url,headers=headers)
		soup = BeautifulSoup(r.text,'lxml')
		location_name = soup.find("h1",{"class":"location-details-heading"}).text.strip()
		addr = list(soup.find("p",{"class":"address-text"}).stripped_strings)
		street_address = addr[0]
		city = addr[1].split(",")[0]
		state = addr[1].split(",")[1].strip().split(" ")[0]
		zipp = addr[1].split(",")[1].strip().split(" ")[1]
		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = soup.find("p",{"class":"phone"}).text.strip()
		except:
			phone = "<MISSING>"
		location_type = "<MISSING>"
		try:
			hours = soup.find("div",{"class":"full-text"}).find_all('strong', text = re.compile('Hours'))
			if len(hours)!=0:
				hours_of_operation = hours[0].text
			else:
				hours_of_operation = list(soup.find("div",{"class":"col-sm-8"}).stripped_strings)[-1].replace("Get Directions","<MISSING>")
		except:
			hours_of_operation = "<MISSING>"
		
		
		if page_url=="https://www.bayhealth.org/sitecore/content/bayhealth/home/locations/outpatient center middletown":
			hours_of_operation = "7 a.m. - 5:30 p.m., Monday - Friday"
		# time.sleep(10)
		# map_url = soup.find("p",{"class":"address-text"}).find("a")['href']
		# coords = session.get(map_url).url
		# if "/@" in coords:
		# 	lat = coords.split("/@")[1].split(",")[0]
		# 	lng = coords.split("/@")[1].split(",")[1]
		# else:
		# 	soup1 = BeautifulSoup(session.get(map_url).text, "lxml")
		# 	file_name = open("data.txt","w",encoding="utf8")
		# 	file_name.write(str(soup1))
		# 	try:
		# 		map_href = soup1.find("a",{"href":re.compile("https://maps.google.com/maps?")})['href']
		# 		lat = str(BeautifulSoup(session.get(map_href).text, "lxml")).split("/@")[1].split(",")[0]
		# 		lng = str(BeautifulSoup(session.get(map_href).text, "lxml")).split("/@")[1].split(",")[1]
		# 	except:
		# 		lat = str(soup1).split("/@")[1].split(",")[0]
		# 		lng = str(soup1).split("/@")[1].split(",")[1]
		latitude = '<MISSING>'
		longitude = '<MISSING>'
		store = []
		store.append(base_url if base_url else '<MISSING>')
		store.append(location_name if location_name else '<MISSING>')
		store.append(street_address if street_address else '<MISSING>')
		store.append(city if city else '<MISSING>')
		store.append(state if state else '<MISSING>')
		store.append(zipp if zipp else '<MISSING>')
		store.append(country_code)
		store.append(store_number if store_number else '<MISSING>')
		store.append(phone if phone else '<MISSING>')
		store.append(location_type)
		store.append(latitude if latitude else '<MISSING>')
		store.append(longitude if longitude else '<MISSING>')
		store.append(hours_of_operation if hours_of_operation else '<MISSING>')
		store.append(page_url)
		store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
		# if store[2] in addressess:
		# 	continue
		# addressess.append(store[2])
		yield store

def scrape():
	data = fetch_data()
	write_output(data)
scrape()
