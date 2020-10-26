from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thelittlebeet_com')




def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.thelittlebeet.com/locations"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)

	try:
		base = BeautifulSoup(req.text,"lxml")
		logger.info("Got today page")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	items = base.findAll('div', attrs={'class': 'location__body'})

	data = []
	for item in items:
		locator_domain = "thelittlebeet.com"
		location_name = item.find('h2').text.strip()
		logger.info(location_name)
		raw_data = str(item.find('div', attrs={'class': 'sqs-block-content'}).p).replace("<p>","").replace("</p>","").split('<br/>')
		if len(raw_data) > 2:			
			street_address = (raw_data[0][raw_data[0].find(">") +1 :] + " " + raw_data[1]).replace("&amp;","&").replace("  "," ")
		else:			
			street_address = raw_data[0][raw_data[0].find(">") +1 :].strip()
		city = raw_data[-1][:raw_data[-1].find(',')].strip()
		state = raw_data[-1][raw_data[-1].find(',')+1:raw_data[-1].rfind(' ')].strip()
		zip_code = raw_data[-1][raw_data[-1].rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		try:
			raw_phone = item.findAll('p')[1].text.strip()
			phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", raw_phone)[0]
		except:
			phone = "<MISSING>"
		location_type = "<MISSING>"
		raw_gps = item.find('a', string="Get Directions")['href']
		start_point = raw_gps.find("@") + 1
		latitude = raw_gps[start_point:raw_gps.find(",",start_point)]
		comma_point = raw_gps.find(",",start_point)
		longitude = raw_gps[comma_point+1:raw_gps.find(',',comma_point+2)]
		if "maps" in latitude:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		hours_of_operation = item.findAll('div', attrs={'class': 'sqs-block-content'})[2].get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		if len(hours_of_operation) < 20:
			hours_of_operation = item.findAll('div', attrs={'class': 'sqs-block-content'})[0].get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)


		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()