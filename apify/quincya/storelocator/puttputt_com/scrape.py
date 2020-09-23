from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re

def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://puttputt.com/locations/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)
	base = BeautifulSoup(req.text,"lxml")

	data = []
	all_links = []
	final_links = []

	items = base.find(class_="entry-content").find_all("a")
	for item in items:
		link = item["href"]
		if link not in all_links:
			all_links.append(link)

	for link in all_links:
		if "locations" not in link:
			final_links.append([link,"","",""])
		else:
			req = session.get(link, headers = HEADERS)
			base = BeautifulSoup(req.text,"lxml")

			items = base.find(id="content").find_all("p")
			for item in items:
				try:
					street = item.find(class_="mini_body").text.split("\n")[-2]
					city_state = item.strong.text.replace("Putt-Putt","").strip()
					phone = item.find(class_="mini_body").text.split("\n")[-1]
					fin_link = item.a["href"]
					final_links.append([fin_link,street,city_state,phone])
				except:
					pass

	for final_link in final_links:

		locator_domain = "puttputt.com"
		country_code = "US"
		store_number = "<MISSING>"
		location_type = "<MISSING>"

		if "funworks" in final_link[0]:
			link = "https://funworksfuncompany.com/directions-hours"
			req = session.get(link, headers = HEADERS)
			base = BeautifulSoup(req.text,"lxml")
			location_name = base.h1.strong.text
			street_address = str(base.h1).split("<br/>")[-2]
			city_line = str(base.h1).split("<br/>")[-1].replace("</h1>","").strip().split(",")
			city = city_line[0].strip()
			state = city_line[-1].strip().split()[0].strip()
			zip_code = city_line[-1].strip().split()[1].strip()
			phone = "209-578-4386"
			
			hours_of_operation = ""
			ps = base.find_all("h4")
			for p in ps:
				if "day" in p.text.lower():
					hours_of_operation = hours_of_operation + " " + p.text.replace("\n"," ").replace("!"," ").replace("–","-")
			hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()

			latitude = "<MISSING>"
			longitude = "<MISSING>"

		elif "/puttputt.com/" not in final_link[0] and ".puttputt.com" not in final_link[0] and "puttputtpa" not in final_link[0]:
			link = final_link[0]
			street_address = final_link[1]
			city = final_link[2].split(",")[0].strip()
			state = final_link[2].split(",")[1].strip()
			location_name = "Putt-Putt Fun Center"
			phone = final_link[3]
			zip_code = "<INACCESSIBLE>"
			hours_of_operation = "<INACCESSIBLE>"
			latitude = "<INACCESSIBLE>"
			longitude = "<INACCESSIBLE>"
			
		else:
			if "puttputtpa.com" in final_link[0]:
				link = "http://www.puttputtpa.com/mini_about.html"
			elif "hope-mills" in final_link[0] or "lynchburg" in final_link[0]:
				link = (final_link[0] + "hours-location").replace("burghours","burg/hours")
			else:
				link = final_link[0] + "hoursinfo"

			print(link)

			req = session.get(link, headers = HEADERS)
			base = BeautifulSoup(req.text,"lxml")
			
			raw_address = ""
			minis = base.find_all(class_="mini_body")
			for mini in minis:
				if "putt-putt" in mini.text.lower() and "bumper" not in mini.text.lower():
					raw_address = mini.text.split("\n")
					break
			if not raw_address:
				minis = base.find_all("p")
				for mini in minis:
					if "putt-putt" in mini.text.lower() and "bumper" not in mini.text.lower():
						raw_address = mini.text.split("\n")
						break

			if raw_address:
				location_name = raw_address[0].strip()
				street_address = raw_address[-3].strip()
				city_line = raw_address[-2].strip().split(",")
				if "fun center" in street_address.lower():
					street_address = raw_address[-2].strip()
					city_line = raw_address[-1].strip().split(",")
				city = city_line[0].strip()
				state = city_line[-1].strip().split()[0].strip()
				zip_code = city_line[-1].strip().split()[1].strip()
			else:
				if link == "https://puttputt.com/hope-mills/hoursinfo":
					location_name = "Putt-Putt Hope Mills"
					street_address = "3311 Footbridge Ln."
					city = "Fayetteville"
					state = "NC"
					phone = "910-424-7888"
					data.append([locator_domain, link, location_name, street_address, city, state, "<MISSING>", country_code, "<MISSING>", phone, "<MISSING>", "<MISSING>", "<MISSING>", "<MISSING>"])
					continue
				else:
					print("No data found")
					break

			try:
				phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", str(base))[0]
			except:
				try:
					phone = re.findall("[[(\d)]{3}\.[\d]{3}\.[\d]{4}", str(base))[0]
				except:
					phone = "<MISSING>"
			if link == "https://puttputt.com/charlottesville/hoursinfo":
				phone = "(434) 973-5509"
			if link == "https://puttputt.com/amelia-island/hoursinfo":
				phone = "904-261-4443"
			hours_of_operation = ""
			try:
				ps = base.find(id="content").find_all("p")
				if "pm" not in str(ps).lower():
					ps = base.find(id="content").find_all("h4")
			except:
				ps = base.find_all("tr")[1:]
			for p in ps:
				if "pm" in p.text.lower() or "am –" in p.text.lower():
					if "March – October" in p.text or "THANKSGIVING" in p.text or "HOURS BEGINNING" in p.text:
						break
					hours_of_operation = hours_of_operation + " " + p.text.replace("\n"," ").replace("!"," ").replace("–","-")
			if hours_of_operation.count("Monday") > 1:
				hours_of_operation = hours_of_operation[:hours_of_operation.rfind("Monday")].strip()
			hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
			if "*" in hours_of_operation:
				hours_of_operation = hours_of_operation[:hours_of_operation.find("*")].strip()
			if not hours_of_operation:
				hours_of_operation = "<MISSING>"

			try:
				map_link = base.find('a', attrs={'target': "_blank"})["href"]
				at_pos = map_link.rfind("@")
				latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
				longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
			except:
				latitude = "<MISSING>"
				longitude = "<MISSING>"
			if "1080 North Marr Rd" in street_address:
				latitude = "39.209968"
				longitude = "-85.885098"
			elif "3311 Footbridge Lane" in street_address:
				latitude = "34.981662"
				longitude = "-78.97214"
			elif "8105 Timberlake Road" in street_address:
				latitude = "37.350075"
				longitude = "-79.231941"
			elif len(latitude) > 15:
				latitude = "<MISSING>"
				longitude = "<MISSING>"
			elif "puttputtpa.com" in link:
				latitude = "39.92672"
				longitude = "-75.304327"

		data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
