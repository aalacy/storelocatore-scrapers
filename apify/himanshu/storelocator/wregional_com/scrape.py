import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
	with open('data.csv', mode='w',newline= "") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	addresses = []
	locator_domain='https://www.wregional.com'
	base_url = "https://www.wregional.com"
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
	}
	r= session.get("https://www.wregional.com/main/find-a-facility-or-clinic",headers=headers)
	soup = BeautifulSoup(r.text,"lxml")
	# for ltype in soup.find("div",class_="template2-row-1").find_all("h3",class_="inside-pages"):
	# 	location_type = ltype.text.strip()
	for ul in soup.find("div",class_="template2-row-1").find_all("ul"):
		location_type = ul.parent.parent.find("h3").text.strip()
		for li in ul.find_all("li"):
			if "http" in li.find("a")["href"]:
				page_url = li.find("a")["href"]
			elif "/" not in li.find("a")["href"]:
				page_url = "https://www.wregional.com/main/"+li.find("a")["href"]
			else:
				page_url = "https://www.wregional.com"+li.find("a")["href"]
			location_name = li.find("a").text.strip()
			r1 = session.get(page_url,headers=headers)
			soup1 = BeautifulSoup(r1.text,"lxml")
			Hours=''
			try:
				full_address = list(soup1.find("div",class_="clinics").find("p").stripped_strings)
				if "(" in full_address[1]:
					del full_address[1]
				try:
					data=int(full_address[0].strip()[0])
					try:
						Hours = " ".join(list(soup1.find(lambda tag: (tag.name == "h3" ) and "Hours" in tag.text.strip()).next_sibling.next_sibling.stripped_strings)).split("Other clinic")[0].replace("Hours at",'').replace("\n",' ').replace("Fayetteville:",'').replace("Springdale",'').split("The clinic is")[-1].replace("The Fayetteville clinic is",'').replace("other clinic locations vary. For more information, please call 479-571-4338.",'').replace("The Fayetteville clinic at the Pat Walker Center for Seniors is",'').replace("Our clinic on the Lincoln Square is",'').replace("The  clinic is",'')
					except:
						Hours="<MISSING>"
					address01 =full_address[0]
					city =full_address[1].split(",")[0]
					state =full_address[1].split(",")[1].strip().split( )[0]
					zipp =full_address[1].split(",")[1].strip().split( )[1]
					phone_tag = full_address[2].replace("Telephone:",'')
					phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
					if phone_list:
						phone= phone_list[0]
						
					else:
						phone = "<MISSING>"

						
					storeNumber='<MISSING>'
					country_code="US"
					# location_type="<MISSING>"
					latitude="<MISSING>"
					longitude="<MISSING>"
					hours_of_operation="<MISSING>"
					store = [locator_domain, location_name,address01,city , state, zipp, country_code,
                        storeNumber, phone.strip(), location_type, latitude, longitude, Hours,page_url]
					yield store
				except:
					# print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~vk~~~~~~~~~~~")
					try:
						Hours = " ".join(list(soup1.find(lambda tag: (tag.name == "h3" ) and "Hours" == tag.text.strip()).nextSibling.next_sibling.stripped_strings)).split("Other clinic")[0].replace("Hours at",'').replace("\n",' ').replace("Fayetteville:",'').replace("Springdale",'').split("The clinic is")[-1].replace("The Fayetteville clinic is",'').replace("other clinic locations vary. For more information, please call 479-571-4338.",'').replace("The Fayetteville clinic at the Pat Walker Center for Seniors is",'').replace("Our clinic on the Lincoln Square is",'').replace("The  clinic is",'')
					except:
						Hours="<MISSING>"
					address01 =full_address[1]
					city =full_address[2].split(",")[0]
					state =full_address[2].split(",")[1].strip().split( )[0]
					zipp =full_address[2].split(",")[1].strip().split( )[1]
					phone_tag = full_address[3].replace("Telephone:",'')
					phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
					if phone_list:
						phone= phone_list[0]
						
					else:
						phone = "<MISSING>"
					storeNumber='<MISSING>'
					country_code="US"
					# location_type="<MISSING>"
					latitude="<MISSING>"
					longitude="<MISSING>"
					hours_of_operation="<MISSING>"
					store = [locator_domain, location_name,address01,city , state, zipp, country_code,
                        storeNumber, phone.strip(), location_type, latitude, longitude, Hours,page_url]
					yield store
					# print(store)
	
			except:
				pass


def scrape():
	data = fetch_data()
	write_output(data)

scrape()
