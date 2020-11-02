import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('baystatehealth_org')



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
	locator_domain = "https://www.baystatehealth.org"

	r = session.get("https://www.baystatehealth.org/locations/search-results",headers =headers)
	soup = BeautifulSoup(r.text,"lxml")
	loc_list = []
	page_url_list =[]
	lat_list =[]
	lng_list = []
	for loc_type in soup.find("select",{"id":"main_1_leftpanel_0_ddlLocationType"}).find_all("option")[1:]:
		location_type = loc_type["value"]
		
		r1 = session.get("https://www.baystatehealth.org/locations/search-results?&loctype="+location_type)
		soup1 = BeautifulSoup(r1.text,"lxml")
			
		script = soup1.find(lambda tag: (tag.name == "script") and "var maplocations" in tag.text.strip()).text.split("var maplocations=")[1]
		for link  in json.loads(script):
			loc_list.append(location_type)
			page_url = "https://www.baystatehealth.org"+link['LocationDetailLink']
			page_url_list.append(page_url)
			latitude = link['LocationLat']
			longitude = link['LocationLon']
			lat_list.append(latitude)
			lng_list.append(longitude)
			
			

	for data in range(1,26):
		# logger.info(data)
		r = session.get("https://www.baystatehealth.org/locations/search-results?page="+str(data),headers=headers)
		soup= BeautifulSoup(r.text,"lxml")
		for loc in soup.find_all("div",class_="listing-item"):
			location_name = loc.h4.text.strip()
			page_url = "https://www.baystatehealth.org"+loc.h4.a["href"].strip()
			r1 = session.get(page_url,headers=headers)
			soup1 = BeautifulSoup(r1.text,"lxml")
			address = list(soup1.find("div",{"id":"main_2_contentpanel_1_pnlAddress"}).stripped_strings)
			street_address = address[0].strip()
			city = address[-1].split(",")[0].strip()
			state = address[-1].split(",")[-1].split()[0].strip()
			zipp = address[-1].split(",")[-1].split()[-1].strip()
			country_code="US"
			# location_type = "<MISSING>"
			try:
				phone_tag = soup1.find("div",{"id":"main_2_contentpanel_1_pnlOfficePhone"}).text.replace("Office Phone:","").strip()
				phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
				if phone_list:
					phone = phone_list[0]
				else:
					phone= "<MISSING>"
			except:
				phone = "<MISSING>"
			try:
				hours_of_operation = " ".join(list(soup1.find("div",class_="module-lc-hours").stripped_strings)).replace("Main Clinic Facility: 300 Birnie Avenue Springfield, MA Monday  Friday: 8:30 a.m.-5 p.m. Physical Therapy Services- 2 locations provided: 300 Birnie Avenue Springfield, MA 265 Benton Drive, Suite 104, East Longmeadow MAMain Clinic Facility: 300 Birnie Avenue Springfield, MA Monday  Friday: 8:30 a.m.-5 p.m. Physical Therapy Services- 2 locations provided: 300 Birnie Avenue Springfield, MA 265 Benton Drive, Suite 104, East Longmeadow MA","").replace(" *Pharmacist on call 24/7","").replace(" Evening hours by appointment.","").replace(" *Extended hours for some services will be held until 6 p.m. on Tuesdays and Wednesdays.","").replace("Once per month on the second or third week","").replace("Phone lines are open: 8 a.m.-4:30 p.m.","").replace("*Open until 8 p.m. on select days (call us to learn more)","").replace("(mammogram screenings only)",'').replace("Office Hours","").replace("Temporary Hours Change","").replace(" We provide 24/7 on-call coverage available through our answering service","").strip()

			except:
				hours_of_operation = "<MISSING>"
			if "Temporarily CLOSED as of 3/25/2020" == hours_of_operation or "Temporarily CLOSED" == hours_of_operation:
				hours_of_operation ="<MISSING>"
			store_number = "<MISSING>"
			for i in range(len(page_url_list)):
				if page_url == page_url_list[i]:
					location_type = loc_list[i]
					latitude = lat_list[i]
					longitude= lng_list[i]
			# for j in range(len(loc_list)):
			# 	if page_url  == page_url_list[j]:
			# 		location_type = loc_list[j]
			# 	else:
			# 		location_type = "<MISSING>"
			store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
				 store_number, phone, location_type, latitude, longitude, hours_of_operation.split("daily We")[0],page_url]
			if (store[-1]) in addressess123:
				continue
			addressess123.append(store[-1])
			store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
			yield store
			# logger.info("~~~",store)
			# logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
def scrape():
	data = fetch_data()
	write_output(data)

scrape()
