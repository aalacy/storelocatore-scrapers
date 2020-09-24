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
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
		'accept': '*/*',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
	}
	locator_domain = base_url = "https://www.augustahealth.com/"
	r = session.get("https://www.augustahealth.com/primary-care/locations",headers=headers)
	soup= BeautifulSoup(r.text,"lxml")
	for link  in soup.find_all("div",class_="view-content")[1:]:
		location_type = "primary-care"
		page_url = "https://www.augustahealth.com"+link.find("a")["href"]
		location_name = link.find("a").text.strip()
		street_address  = link.find("div",class_="street-block").text.split("Suite")[0].strip()
		city = link.find("span",class_="locality").text.strip()
		state =link.find("span",class_="state").text.strip() 
		zipp  =link.find("span",class_="postal-code").text.strip()
		country_code = "US"
		store_number="<MISSING>"
		r1 = session.get(page_url,headers=headers)
		soup_loc = BeautifulSoup(r1.text,"lxml")
		info = soup_loc.find("div",class_="basic-info")
		phone = info.find("p",class_="phone").text.strip()
		hours_of_operation =" ".join(list(info.find("div",class_="view-office-hours").stripped_strings))
		latitude = info.find("a",text = re.compile("Get Directions"))["href"].split("@")[1].split(",")[0]
		longitude = info.find("a",text = re.compile("Get Directions"))["href"].split("@")[1].split(",")[1]
		store = [locator_domain, location_name, street_address.replace(",",""), city, state, zipp, country_code,
			 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
		# print("data = " + str(store))
		# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
		store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
		yield store
	r = session.get("https://www.augustahealth.com/urgent-care",headers=headers)
	soup = BeautifulSoup(r.text,"lxml")
	for loc in soup.find_all("div",class_="location"):
		location_name = loc.h4.text.strip()
		add = " ".join(list(loc.find("p",class_="address").stripped_strings)).split("\n")
		if len(add) == 1:
			street_address = add[0].split(",")[0].split("Suite")[0]
			city = add[0].split(",")[1]
		else:
			street_address =" ".join(add[:-1]).split("Suite")[0]
			city = add[-1].split(",")[0]
		state = add[-1].split(",")[-1].split()[0]
		zipp = add[-1].split(",")[-1].split()[-1]
		country_code = "US"
		
		try:
			latitude = loc.find("p",class_="address").find("a")["href"].split("@")[1].split(",")[0]
			longitude = loc.find("p",class_="address").find("a")["href"].split("@")[1].split(",")[1]
			phone = loc.find("p",class_="phone").text.strip()
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"
			phone = "<MISSING>"
		hours_of_operation = loc.find("div",class_="hours").text.strip()
		location_type = "urgent-care"
		store_number = "<MISSING>"
		page_url ="https://www.augustahealth.com/urgent-care"
		store = [locator_domain, location_name, street_address.replace(",",""), city, state, zipp, country_code,
				 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
		# print("data = " + str(store))
		# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
		store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
		yield store
	r = session.get("https://www.augustahealth.com/laboratory/locations",headers=headers)
	soup = BeautifulSoup(r.text,"lxml")
	div_yellow = soup.find("div",class_="box-rounded-yellow")
	address = list(div_yellow.find("p",class_="location").stripped_strings)
	location_name = address[0]
	street_address = address[1].split("Suite")[0]
	city = address[-1].split(",")[0]
	state = address[-1].split(",")[-1].split()[0].strip()
	zipp = address[-1].split(",")[-1].split()[-1].strip()
	country_code = "US"
	latitude = div_yellow.find("p",class_="location").find("a")["href"].split("@")[1].split(",")[0]
	longitude = div_yellow.find("p",class_="location").find("a")["href"].split("@")[1].split(",")[1]
	phone = list(div_yellow.find("h4",text=re.compile("Phone")).nextSibling.stripped_strings)[0]
	hours_of_operation = " ".join(list(div_yellow.find("table").stripped_strings))
	location_type = "laboratory"
	store_number = "<MISSING>"
	page_url ="https://www.augustahealth.com/laboratory/locations"
	store = [locator_domain, location_name, street_address.replace(",",""), city, state, zipp, country_code,
			 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
	# print("data = " + str(store))
	# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
	store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
	yield store
	r = session.get("https://www.augustahealth.com/laboratory/locations",headers=headers)
	soup = BeautifulSoup(r.text,"lxml")
	for div_blue in soup.find_all("h3"):
		location_name = div_blue.text
		address = list(div_blue.find_next("div",class_="box-rounded-blue").find("p",class_="location").stripped_strings)
		# print(address)
		street_address = address[0].split("Suite")[0]
		city = address[-1].split(",")[0]
		state = address[-1].split(",")[-1].split()[0].strip()
		zipp = address[-1].split(",")[-1].split()[-1].strip()
		country_code = "US"
		latitude = div_blue.find_next("div",class_="box-rounded-blue").find("p",class_="location").find("a")["href"].split("@")[1].split(",")[0]
		longitude = div_blue.find_next("div",class_="box-rounded-blue").find("p",class_="location").find("a")["href"].split("@")[1].split(",")[1]
		phone = list(div_blue.find_next("div",class_="box-rounded-blue").find("h4",text=re.compile("Phone")).nextSibling.stripped_strings)[0]
		hours_of_operation = " ".join(list(div_blue.find_next("div",class_="box-rounded-blue").find("table").stripped_strings))
		location_type = "laboratory"
		store_number = "<MISSING>"
		page_url ="https://www.augustahealth.com/laboratory/locations"
		store = [locator_domain, location_name, street_address.replace(",",""), city, state, zipp, country_code,
				 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
		# print("data = " + str(store))
		# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
		store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
		yield store
def scrape():
	data = fetch_data()
	write_output(data)
scrape()
