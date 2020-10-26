from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mfg_com')



def write_output(data):
	with open('data.csv', mode='w', encoding="utf-8") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "search_link"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	data = []
	all_links = []
	locator_domain = "mfg.com"

	base_links = [	"https://www.mfg.com/search?page=1&term=Minot,%20ND,%20USA&lat=48.2329668&long=-101.2922906&processId=0&radius=2500",
					"https://www.mfg.com/search?page=1&term=Fairbanks,%20AK,%20USA&lat=64.8377778&long=-147.7163888&processId=0&radius=1000",
					"https://www.mfg.com/search?page=1&term=Honolulu,%20HI,%20USA&lat=21.3069444&long=-157.8583333&processId=0&radius=1000"]

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}
	session = SgRequests()
	page_session = SgRequests()

	for base_link in base_links:

		req = session.get(base_link, headers = HEADERS)
		base = BeautifulSoup(req.text,"lxml")
		last_page = base.find(class_="pagination").find_all("a")[-1]["href"].split("=")[-1]

		for page_num in range(1,int(last_page)+1):
			page_link = "https://www.mfg.com/search?page=" + str(page_num) + "&" +  "&".join(base_link.split("&")[1:])
			logger.info(page_link)
	
			req = session.get(page_link, headers = HEADERS)
			base = BeautifulSoup(req.text,"lxml")

			items = base.find(class_="row main-pane-bs").find_all(class_="container")
			for item in items:

				link = "https://www.mfg.com" + item.a["href"]
				if link in all_links:
					logger.info("Skipping Dup..")
					continue

				all_links.append(link)

				location_name = item.find(class_="name").text.strip()
				# logger.info(location_name)
				store_number = "<MISSING>"
				location_type = item.find(class_="category").text.replace("\t","").strip().replace("\n\n\n",",").strip()
				if not location_type:
					location_type = "<MISSING>"
				try:
					phone = item.find(class_="phone").text.replace("\t","").replace("08888","8888").strip()
					if "x" in phone:
						phone = phone[:phone.find("x")].strip()
					if "X" in phone:
						phone = phone[:phone.find("X")].strip()
					if "or" in phone:
						phone = phone[:phone.find("or")].strip()
					phone = phone.replace("e","").replace("E","").strip()
					if len(phone.replace("+","")) < 10:
						phone = "<MISSING>"
				except:
					phone = "<MISSING>"

				hours_of_operation = "<MISSING>"
				latitude = "<MISSING>"
				longitude = "<MISSING>"

				# Getting address from page num list
				if "united states" in item.text.lower():
					country_code = "US"
					if phone[:1] == "+" and phone[1:2] != "1":
						phone = phone.replace("+","+1")
				elif "canada" in item.text.lower():
					country_code = "CA"
				else:
					continue

				if phone == "309922121" or phone == "901854130" or phone == "+161-3-93054077":
					phone = "<MISSING>"
				if phone == "6305523667227":
					phone = "5523667227"
				elif phone == "86660716534":
					phone = "8666071653"
				if phone == "41753261331019":
					phone = "4175326133"
				if phone[-4:] == " 101" or phone[-4:] == " 701":
					phone = phone.split(" ")[0]
				
				raw_address = item.find_all(class_="address")
				if len(raw_address) == 2:
					street_address = raw_address[0].text.replace("\t","").replace(",,",",").strip()
					if len(street_address) < 3:
						street_address = "<MISSING>"
					else:
						raw_address = raw_address[1].text.replace("\t","").replace(",,",",").replace("\xa0","").strip().split("\n\n")[0].split(",")
						city = raw_address[0].strip()
						if city in street_address:
							street_address = "<MISSING>"
						if country_code == "US":
							try:
								zip_code = raw_address[1][-6:].strip()
								state = raw_address[1][:-6].strip()
							except:
								zip_code = raw_address[0][-6:].strip()
								state = raw_address[0][:-6].strip()
						else:
							zip_code = raw_address[1][-7:].strip()
							state = raw_address[1][:-7].strip()
				else:
					street_address = "<MISSING>"

				if street_address == "<MISSING>":
					# Getting address data from page_url instead
					req = page_session.get(link, headers = HEADERS)
					page_base = BeautifulSoup(req.text,"lxml")
					raw_address = page_base.find(class_="col-md-12 address").text.replace("\t","").replace(",,",",").replace("\xa0","").replace("MAP","").strip().split(",")
					street_address = "".join(raw_address[:-2]).strip()
					city = raw_address[-2].strip()
					if country_code == "US":
						zip_code = raw_address[-1].strip()[-5:].strip()
						state = raw_address[-1].strip()[:-5].strip()
					else:
						zip_code = raw_address[-1][-7:].strip()
						state = raw_address[-1][:-7].strip()
				city = city.replace("OLYMPIA","Olympia")

				street_address = street_address.replace("Bill To:","").replace("\u200b","").replace("Quality Craftsmanship - Since","")\
				.replace('"principle office location"','').replace("OH 44610","").replace("PA 19426","").replace("NULL","")
				street_address = (re.sub(' +', ' ', street_address)).strip()
				if "3318 Sandy" in street_address:
					street_address = street_address[:street_address.find("3318")].strip()
				if city in street_address:
					orig_street = street_address
					street_address = street_address[:street_address.rfind(city)].strip()
					if len(street_address) < 10:
						street_address = orig_street
				if state in street_address:
					if city in street_address:
						street_address = street_address[:street_address.rfind(city)].strip()
				elif ", White plains" in street_address or ", VT" in street_address or ", GA" in street_address or ", CA" in street_address:
					street_address = street_address[:street_address.find(",")].strip()
				elif "(Joe" in street_address:
					street_address = street_address[:street_address.find("(Joe")].strip()
				elif "Spartanburg" in street_address:
					street_address = street_address[:street_address.find("Spartanburg")].strip()
				elif "1 Peters Canyon" in street_address:
					street_address = "1 Peters Canyon, Building 100 Irvine"
				elif "Chatsworth" in street_address:
					street_address = street_address[:street_address.find("Chatsworth")].strip()
				if not street_address:
					street_address = "<MISSING>"
				if not city:
					city = "<MISSING>"
				if not state:
					state = "<MISSING>"
				if not zip_code:
					zip_code = "<MISSING>"

				zip_code = zip_code.replace("H4S-1J7","H4S 1J7").replace("?","")
				if zip_code in street_address:
					street_address = street_address[:street_address.rfind(zip_code)-3].strip()
				if country_code == "CA":
					zip_code = zip_code.upper()

				if country_code == "US" and "-" in zip_code:
					zip_code = state.split()[1] + zip_code
					state = state.split()[0]

				if street_address[-1:] == "," or street_address[-1:] == "-":
					street_address = street_address[:-1].strip()

				data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation, page_link])

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()
