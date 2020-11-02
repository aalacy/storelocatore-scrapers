import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('primehealthcare_com')





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
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
		'accept': '*/*',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
	}
	locator_domain = base_url = "https://www.primehealthcare.com/"

	r = session.get("https://www.primehealthcare.com/Our-Locations.aspx?MinLat=18.817327155192622&MinLng=-127.88375854492188&MaxLat=53.22868352921054&MaxLng=-64.61624145507812&Zoom=4&CallAjax=SearchMap",headers=headers).json()
	
	# soup= BeautifulSoup(r.text,"lxml")
	for link  in r:
		soup= BeautifulSoup(link['HTML'],"lxml")
		add = list(soup.find("div",{"class":"facilitiesitem"}).find("p").stripped_strings)
		location_type = "<MISSING>"
		page_url = soup.find("h2",{"class":"firstHeading"}).find("a")['href']
		location_name = soup.find("h2",{"class":"firstHeading"}).text.strip()
		street_address = list(soup.find("div",{"class":"facilitiesitem"}).find("p").stripped_strings)[0].split("Suite")[0].split("floor")[0].replace(",",'').replace("",'')
		city = add[-2].split(",")[0].strip()
		state =add[-2].split(",")[1].split( )[0].strip() 
		zipp  =add[-2].split(",")[1].split( )[1].strip() 
		country_code = "US"
		store_number="<MISSING>"
		phone = soup.find("div",{"class":"facilitiesitem"}).find_all("p")[-1].text
		hours_of_operation ="<MISSING>"
		latitude = link['Latitude']
		longitude = link['Longitude']
		store =[]
		store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
			 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

		# logger.info("data = " + str(store))
		# logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
		yield store

	



def scrape():
	data = fetch_data()
	write_output(data)

scrape()
