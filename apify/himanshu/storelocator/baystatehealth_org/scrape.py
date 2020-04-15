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
	addressess123=[]
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
		'accept': '*/*',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
	}
	locator_domain = base_url = "https://www.baystatehealth.org"

	r = session.get("https://www.baystatehealth.org/locations/search-results",headers=headers)
	soup= BeautifulSoup(r.text,"lxml")
	for link1 in soup.find_all("div",{"class":"dd-1 drop"})[2].find_all("li"):
		if "/locations/search-results?loctype=hospital" in link1.find("a")['href']:
			newlinke = "https://www.baystatehealth.org"+link1.find("a")['href']
			# print("~~~~~~~~~~~~~~~",newlinke)
		else:
			newlinke = link1.find("a")['href']
		# print(newlinke)
		r1 = session.get(newlinke,headers=headers)
		soup1= BeautifulSoup(r1.text,"lxml")
		script = soup1.find(lambda tag: (tag.name == "script") and "var maplocations" in tag.text.strip()).text.split("var maplocations=")[1]
		for link  in json.loads(script):
			location_type = link1.find("a").text.strip()
			page_url = "https://www.baystatehealth.org"+link['LocationDetailLink']
			soup2= BeautifulSoup(link['LocationFullAddress'],"lxml")
			location_name = link["LocationName"]
			street_address = list(soup2.stripped_strings)[0]
			city = list(soup2.stripped_strings)[-1].split(",")[0]
			state =list(soup2.stripped_strings)[-1].split(",")[1].split( )[0]
			zipp  =list(soup2.stripped_strings)[-1].split(",")[1].split( )[-1]
			country_code = "US"
			store_number="<MISSING>"
			r1 = session.get(page_url,headers=headers)
			soup_loc = BeautifulSoup(r1.text,"lxml")
			try:
				phone = list(soup_loc.find("div",{"id":"main_2_contentpanel_1_pnlOfficePhone"}).stripped_strings)[-1].replace("Office Phone:",'').replace("(To schedule an MRI)",'').strip()
			except:
				phone ="<MISSING>"
			try:
				hours_of_operation =" ".join(list(soup_loc.find("div",class_="module-lc-hours").stripped_strings)).strip()
			except:
				hours_of_operation="<MISSING>"
			if hours_of_operation.strip():
				hours_of_operation=hours_of_operation
			else:
				hours_of_operation="<MISSING>"
			latitude = link['LocationLat']
			longitude = link['LocationLon']
			store =[]
			street_address = street_address.split("Floor")[0].split("Suite")[0].replace(",",'')
			if "Office Hours Temporarily" in hours_of_operation:
				hours_of_operation = "<MISSING>"
			store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
				 store_number, phone, location_type, latitude, longitude, hours_of_operation.encode('ascii', 'ignore').decode('ascii').strip().replace(". (mammogram screenings only)",'').replace("on select days (call us to learn more)",'').replace('Office Hours',''),page_url]
			# print("data = " + str(store))
			# if store[2]  in addressess123:
			# 	continue
			# addressess123.append(store[2])
			yield store
		# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

	
def scrape():
	data = fetch_data()
	write_output(data)

scrape()
