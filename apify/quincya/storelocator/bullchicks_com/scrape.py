import requests
from bs4 import BeautifulSoup
import csv
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bullchicks_com')



def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "http://bullchicks.com/locations.html"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')


	items = base.findAll('li', attrs={'class': 'col-md-12 location_panel'})
	items.pop(-1)

	data = []

	for item in items:
		main_col = item.findAll('div', attrs={'class': 'col-md-3 location_subpanel'})[1]
		hours_col = item.findAll('div', attrs={'class': 'col-md-3 location_subpanel'})[2]

		locator_domain = "bullchicks.com"
		location_name = main_col.find('h3').text.strip()
		raw_data = str(main_col.find('p', attrs={'class': 'col-md-12 address'})).replace('</p>',"").split('<br/>')

		street_address = raw_data[1].strip()
		city = raw_data[2][:raw_data[2].find(',')].strip()
		state = raw_data[2][raw_data[2].find(',')+1:raw_data[2].rfind(' ')].strip()
		zip_code = raw_data[2][raw_data[2].rfind(' ')+1:].replace("</span>","").strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = main_col.find('p', attrs={'class': 'col-md-12 phone'}).text.replace("Call Us:","").strip()
		location_type = "<MISSING>"
		gps_link =  gps_link =  main_col.findAll('a')[1]['href']
		start_point = gps_link.find('@') + 1
		end_point = gps_link.find(',',start_point)
		latitude = gps_link[start_point:end_point]
		longitude = gps_link[end_point+1:gps_link.find(',',end_point+2)]
		try:
			hours_1 = hours_col.findAll('p')[0].get_text(separator=u' ').replace("\n"," ").replace("   "," ").strip()
			hours_2 = hours_col.findAll('p')[1].get_text(separator=u' ').replace("\n"," ").replace("   "," ").strip()
			hours_of_operation = hours_1 + " " + hours_2
		except:
			hours_of_operation = hours_col.findAll('p')[0].get_text(separator=u' ').replace("\n"," ").replace("  "," ").strip()

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()