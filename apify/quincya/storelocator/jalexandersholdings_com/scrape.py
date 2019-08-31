import requests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "http://jalexandersholdings.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')
	
	data = []
	sections = base.findAll('div', attrs={'class': 'conceptcontainer'})
	for section in sections:
		items = section.findAll('div', attrs={'class': 'location-details'})
		locator_domain = "jalexandersholdings.com"
		location_name = section.find('h3').text.strip()
		print (location_name)
		for item in items:
			if "Opening" not in item.text:
				raw_data = str(item.find('a')).replace('<p>',"").replace('</p>',"").replace('\n',"").replace('\t'," ").strip().split('<br/>')
				street_address = raw_data[0][raw_data[0].rfind('blank">')+7:].strip()
				raw_line = raw_data[1][2:raw_data[1].find('<')].strip()
				city = raw_line[:raw_line.rfind(',')].strip()
				if "Suite" in city:
					street_address = street_address + " " + city[:city.find("    ")].strip()
					city = city[city.find("    "):].strip()

				state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
				zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
				try:
					int(zip_code)
				except:
					raw_data = str(item.find('a')).replace('<p>',"").replace('</p>',"").replace('\n',"").replace('\t'," ").strip().split('<br/>')
					street_address = raw_data[0][raw_data[0].rfind('blank">')+7:].strip() + raw_data[1].strip()
					raw_line = raw_data[2][2:raw_data[2].find('<')].strip()
					city = raw_line[:raw_line.rfind(',')].strip()
					state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
					zip_code = raw_line[raw_line.rfind(' ')+1:].strip()

				country_code = "US"
				store_number = "<MISSING>"
				try:
					phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", item.text)[0]
				except:
					phone = re.findall("[[\d]{3}-[\d]{3}-[\d]{4}", item.text)[0]
				location_type = "<MISSING>"

				raw_gps = item.find('a')['href']

				start_point = raw_gps.find("@") + 1
				latitude = raw_gps[start_point:raw_gps.find(',',start_point)]
				long_start = raw_gps.find(',',start_point)+1
				longitude = raw_gps[long_start:raw_gps.find(',',long_start)]
				try:
					int(latitude[4:8])
				except:
					try:
						start_point = raw_gps.find("ll=") + 3
						latitude = raw_gps[start_point:raw_gps.find(',',start_point)]
						long_start = raw_gps.find(',',start_point)+1
						longitude = raw_gps[long_start:raw_gps.find('&',long_start)]
					except:
						latitude = "<MISSING>"
						longitude = "<MISSING>"
					try:
						int(latitude[4:8])
					except:
						latitude = "<MISSING>"
						longitude = "<MISSING>"						

				hours_of_operation = item.find('div', attrs={'class': 'hours'}).p.get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
				hours_of_operation = re.sub(' +', ' ', hours_of_operation)

				data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
