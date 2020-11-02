import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('balladhealth_org')





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
	locator_domain = base_url = "https://www.balladhealth.org"

	r = session.get("https://www.balladhealth.org/locations",headers=headers)
	soup= BeautifulSoup(r.text,"lxml")
	
	for link1  in soup.find_all("div",{"class":"view-id-locations"}):
		# logger.info()
		for link in link1.find_all("div",{"class":"views-row"}):
			location_type = link1['class'][3].replace("view-display-id-",'').replace("_",' ')
			street_address = list(link.find("div",{"class":"views-field views-field-address"}).stripped_strings)[0].split("Suite")[0].split("Floor")[0].replace(",",'')
			# logger.info(street_address)
			city = list(link.find("div",{"class":"views-field views-field-address"}).stripped_strings)[-1].split(",")[0]
			

			# state =list(link.find("div",{"class":"views-field views-field-address"}).stripped_strings)[-1].split(",")[1].strip().split(" ")[0]
			state_list = re.findall(r'([A-Z]{2})', str(list(link.find("div",{"class":"views-field views-field-address"}).stripped_strings)[-1].split(",")[1].strip()))
			us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(list(link.find("div",{"class":"views-field views-field-address"}).stripped_strings)[-1].split(",")[1].strip()))
			
			if state_list:
				state = state_list[-1]
			else:
				state="<MISSING>"
			# logger.info(state)
			if us_zip_list:
				zipp = us_zip_list[-1]
			else:
				zipp="<MISSING>"
			phone1 = link.find("div",{"class":"views-field views-field-phone"}).text.strip()
			if phone1:
				phone = phone1.replace("\t",'').replace("\n",'').replace("\\t",'')
			else:
				phone = "<MISSING>"
			# location_type = link.find("div",{"class":"views-field views-field-title"}).find("a")['href'].split("/")[1].replace("-",' ')
			page_url = "https://www.balladhealth.org"+link.find("div",{"class":"views-field views-field-title"}).find("a")['href']
			location_name = link.find("div",{"class":"views-field views-field-title"}).text.strip()

			country_code = "US"
			store_number="<MISSING>"
			r1 = session.get(page_url,headers=headers)
			soup_loc = BeautifulSoup(r1.text,"lxml")
			try:
				hours = soup_loc.find(lambda tag:  "Hours" == tag.text.strip()).find_next_siblings("ul")[0].text.strip().replace("\n",' ')
			except:
				hours="<MISSING>"

			
			latitude = link.find("div",{"class":"views-field views-field-Latitude element-invisible"}).text.strip()
			longitude = link.find("div",{"class":"views-field views-field-Longitude element-invisible"}).text.strip()
			store =[]
			store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
				store_number, phone, location_type, latitude, longitude, hours.encode('ascii', 'ignore').decode('ascii').strip(),page_url]

			# logger.info("data = " + str(store))
			# logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
			yield store


	



def scrape():
	data = fetch_data()
	write_output(data)

scrape()
