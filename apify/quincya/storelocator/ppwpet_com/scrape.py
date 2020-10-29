import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ppwpet_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "http://www.ppwpet.com/location"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')
	
	items = base.findAll('div', attrs={'class': 'row sqs-row'})
	
	data = []
	locations = []
	for item in items:
		locator_domain = "ppwpet.com"
		try:
			location_name = item.find('h3').text.strip()
			if len(location_name) > 30:
				continue
			if location_name in locations:
				continue
			if "NOW OPEN!" in location_name:
				location_name = location_name.replace("NOW OPEN!","").strip()
				location_type = "Now Open"
			else:
				location_type = "<MISSING>"
			locations.append(location_name)
		except:
			continue
		logger.info(location_name)

		raw_data = str(item.find('p')).split("<br/>")
		street_address = raw_data[0][raw_data[0].rfind(">")+1:]
		try:
			city = raw_data[1][:raw_data[1].find(',')].strip()
		except:
			continue
		state = raw_data[1][raw_data[1].find(',')+1:raw_data[1].find(',')+4].strip()
		zip_code = raw_data[1][raw_data[1].find(',')+5:raw_data[1].find(',')+10].strip()
		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", raw_data[1])[0]
		except:
			phone = raw_data[2].replace("\xa0"," ").replace("</p>","")
		
		raw_gps = str(item)
		start_point = raw_gps.find("mapLat") + 8
		latitude = raw_gps[start_point:raw_gps.find(",",start_point)]
		semi_point = raw_gps.find(":",start_point)
		longitude = raw_gps[semi_point+1:raw_gps.find(',',semi_point)]
		hours_of_operation = item.findAll('p')[1].get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	# Get Missing from bad html structure

	item = base.find('div', attrs={'id': 'block-yui_3_17_2_1_1526323650996_121707'})

	raw_gps = str(base.find('div', attrs={'id': 'block-yui_3_17_2_1_1526323650996_116817'}))
	locator_domain = "ppwpet.com"
	location_name = item.find('h3').text.strip()
	if "NOW OPEN!" in location_name:
		location_name = location_name.replace("NOW OPEN!","").strip()
		location_type = "Now Open"
	else:
		location_type = "<MISSING>"
		locations.append(location_name)
	logger.info(location_name)

	raw_data = str(item.find('p')).split("<br/>")
	street_address = raw_data[0][raw_data[0].rfind(">")+1:]
	city = raw_data[1][:raw_data[1].find(',')].strip()	
	state = raw_data[1][raw_data[1].find(',')+1:raw_data[1].find(',')+4].strip()
	zip_code = raw_data[1][raw_data[1].find(',')+5:raw_data[1].find(',')+10].strip()
	country_code = "US"
	store_number = "<MISSING>"
	try:
		phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", raw_data[1])[0]
	except:
		phone = raw_data[2].replace("\xa0"," ").replace("</p>","")
	start_point = raw_gps.find("mapLat") + 8
	latitude = raw_gps[start_point:raw_gps.find(",",start_point)]
	semi_point = raw_gps.find(":",start_point)
	longitude = raw_gps[semi_point+1:raw_gps.find(',',semi_point)]
	hours_of_operation = item.findAll('p')[1].get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
	hours_of_operation = re.sub(' +', ' ', hours_of_operation)

	data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()