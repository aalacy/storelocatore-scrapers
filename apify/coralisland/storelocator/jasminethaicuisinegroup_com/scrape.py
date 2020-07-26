import csv
import re
import pdb
from sgrequests import SgRequests
from lxml import etree
import json

base_url = 'https://www.jasminethaicuisinegroup.com'

def validate(item):	
	if type(item) == list:
		item = ' '.join(item)
	return item.strip()

def get_value(item):
	item = validate(item)
	if item == '':
		item = '<MISSING>'
	return item

def eliminate_space(items):
	rets = []
	for item in items:
		item = validate(item)
		if item != '':
			rets.append(item)
	return rets

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		for row in data:
			writer.writerow(row)

def fetch_data():
	output_list = []
	url = "https://www.jasminethaicuisinegroup.com/"
	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	headers = {'User-Agent' : user_agent}

	session = SgRequests()
	request = session.get(url, headers=headers)
	response = etree.HTML(request.text)
	store_list = response.xpath('//a[@style="color:#000000;"]')
	for loc in store_list:
		link = base_url + loc.xpath('@href')[0]
		data = etree.HTML(session.get(link, headers=headers).text)
		store = eliminate_space(data.xpath('.//div[contains(@class, "dmRespCol  large-4  medium-4  small-12")]')[1].xpath('.//text()'))
		output = []
		output.append(base_url) # url
		output.append(link) #location name
		output.append(store[0]) #location name
		output.append(store[1]) #address
		address = store[2].strip().split(',')
		output.append(address[0]) #city
		output.append(address[1].strip().split(' ')[0]) #state
		output.append(address[1].strip().split(' ')[1]) #zipcode
		output.append('US') #country code
		output.append(loc.xpath('@id')[0]) #store_number
		output.append(store[3]) #phone
		output.append("Jasmine Thai Cuisine") #location type
		output.append(get_value(data.xpath('.//div[contains(@class, "inlineMap")]/@data-lat'))) #latitude
		output.append(get_value(data.xpath('.//div[contains(@class, "inlineMap")]/@data-lng'))) #longitude
		output.append(', '.join(store[4:-2])) #opening hours
		output_list.append(output)
	return output_list

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
