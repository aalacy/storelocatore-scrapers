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
	locator_domain = base_url = "https://www.bayhealth.org"

	r = session.get("https://www.bayhealth.org/locations-and-contact",headers=headers)
	soup= BeautifulSoup(r.text,"lxml")
	for link  in soup.find_all("div",{"class":"section-spacer"}):
		if link.find("h3") != None:
			location_type=link.find("h3").text.strip()
			for info in link.find_all("div",{"class":"address-block"}):
				location_name = info.find("p",{"class":"title"}).text.strip()
				page_url = "https://www.bayhealth.org"+info.find("p",{"class":"title"}).find("a")['href']
				phone1 = info.find("p",{"class":"phone address-block-last-element"}).text.strip()
				if phone1:
					phone = phone1
				else:
					phone = "<MISSING>"
				hours='<MISSING>'
				add = info.find("a",{"class":"address"}).text.strip()
				street_address = list(info.find("a",{"class":"address"}).stripped_strings)[0]
				city = list(info.find("a",{"class":"address"}).stripped_strings)[-1].split(",")[0]
				state = list(info.find("a",{"class":"address"}).stripped_strings)[-1].split(",")[1].split( )[0]
				# zipp =list(info.find("a",{"class":"address"}).stripped_strings)[-1].split(",")[1].split( )[1]
				if len(list(info.find("a",{"class":"address"}).stripped_strings)[-1].split(',')[1].strip().split( ))==1:
					state = "<MISSING>"
				else:
					state = list(info.find("a",{"class":"address"}).stripped_strings)[-1].split(",")[1].split( )[0]
				
				us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(list(info.find("a",{"class":"address"}).stripped_strings)[-1]))
				if us_zip_list:
					zipp = us_zip_list[-1]
				else:
					zipp="<MISSING>"
				location_type1 =location_type
				hours3 ='<MISSING>'
				country_code = "US"
				store_number="<MISSING>"
				r1 = session.get(page_url,headers=headers)
				soup_loc = BeautifulSoup(r1.text,"lxml")
				try:
					latitude = soup_loc.text.split('var location_lat_lng ')[1].split("};")[0].split("= {lat:")[1].split(",")[0]
					longitude = soup_loc.text.split('var location_lat_lng ')[1].split("};")[0].split("= {lat:")[1].split(",")[1].split(" lng:")[-1]
				except:
					latitude = "<MISSING>"
					longitude ="<MISSING>"
				if latitude.strip():
					latitude=latitude
					longitude = longitude
				else:
					latitude = "<MISSING>"
					longitude ="<MISSING>"
				hours1=''
			

				
				try:
					# hours = soup_loc.find(text="Hours").parent.parent.text.strip()
					hours = soup_loc.find(lambda tag: (tag.name == "strong") and "Hours"==tag.text.strip()).parent.text
				except:
					pass

				try:
					# hours = soup_loc.find(text="Hours").parent.parent.text.strip()
					hours = soup_loc.find(lambda tag: (tag.name == "h3") and "Hours" in tag.text.strip()).text
					m = hours = soup_loc.find(lambda tag: (tag.name == "p") and "Monday" in tag.text.strip()).text
					if hours=="Hours":
						hours = m
					else:
						hours = hours
				except:
					pass				
				
				if ".Hours" in hours.split("We offer the")[0]:
					hours1 = hours.split("We offer the")[0].split(".Hours")[-1]
				else:
					hours1 =  hours.split("We offer the")[0]
				if "Center is staffed and" in hours1:
					hours1 = hours1.split("Center is staffed and")[1]
				if hours1.split("Phone")[0].strip().lstrip():
					hours3 = hours1.replace("Sunday:",' Sunday: ').replace("Hours",' Hours ').replace(".,",'')
				# print(hours3)
				hours3 = hours3
				street_address = street_address.replace(", 2nd Floor",'').split("Floor")[0].split("Suite")[0].replace(",",'')
				store =[]
				store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
					store_number, phone, location_type1, latitude, longitude, hours3.replace("Hours: By appointment only",'<MISSING>').encode('ascii', 'ignore').decode('ascii').strip().replace("\n",' '),page_url]

				# print("data = " + str(store))
				# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
				yield store


	



def scrape():
	data = fetch_data()
	write_output(data)

scrape()
