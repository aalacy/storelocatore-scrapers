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
	
	base_link = "https://www.urthcaffe.com/our-cafes/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	req = requests.get(base_link, headers=headers)

	try:
		base = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print ('[!] Error Occured. ')
		print ('[?] Check whether system is Online.')
	
	items = base.findAll('div', attrs={'class': 'list-text'})
	
	data = []
	for item in items:
		locator_domain = "urthcaffe.com"		
		location_name = item.find('h2').text.strip()
		print (location_name)
		location_type = "<MISSING>"
		raw_data = str(item.findAll('p')[0]).replace('<p>',"").replace('</p>',"").replace('\n',"").split('<br/>')
		street_address = raw_data[0].strip()
		if "Los Angeles International" in street_address:
			street_address = raw_data[0].strip() + " " + raw_data[1].strip()
			city = "Los Angeles"
			state = "CA"
			zip_code = "<MISSING>"
		else:
			if "Now Open" not in street_address:			
				raw_line = raw_data[1].strip()
			else:
				location_type = "Now Open"
				street_address = raw_data[1].strip()
				raw_line = raw_data[2].strip()
			city = raw_line[:raw_line.rfind(',')].strip()
			state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
			zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
		if state == "":
			state = zip_code
			zip_code = "<MISSING>"

		country_code = "US"
		store_number = "<MISSING>"
		try:
			phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", str(item.text))[0]
		except:
			phone = re.findall("[[(\d)]{5} [\d]{3} [\d]{4}", str(item.text))[0]
		latitude = "<MISSING>"
		longitude = "<MISSING>"
		got_del = False
		hours = item.findAll('p')[1].get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		if "Hours" not in hours:
			hours = item.findAll('p')[2].get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
			if "currently unavailable" in hours:
				deliv = ""
				got_del = True
			else:
				try:
					deliv = item.findAll('p')[3].get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
					got_del = True
				except IndexError:
					item_text = item.text
					if "currently unavailable" in item_text:
						deliv = "Delivery service is currently unavailable"
						got_del = True				
		if not got_del:
			try:
				deliv = item.findAll('p')[2].get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
				if deliv == "":
					item_text = item.text
					deliv = "Delivery Hours: " + item_text[item_text.rfind("Days")-7:item_text.rfind('pm')+2].strip()
			except IndexError:
				item_text = item.text
				deliv = item_text[item_text.rfind("Delivery")+5:item_text.rfind('able')+4].strip()
				if deliv == "":
					deliv = "Delivery Hours: " + item_text[item_text.rfind("Days")-2:item_text.rfind('pm')+2].strip()

		hours = re.sub(' +', ' ', hours)
		deliv = re.sub(' +', ' ', deliv)
		hours_of_operation = (hours + " " + deliv).strip()

		data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
