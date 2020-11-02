import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('unitypoint_org')



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
	
	}
	locator_domain = base_url = "https://www.unitypoint.org"

	r = session.get("https://www.unitypoint.org/interstitial.aspx",headers=headers)
	soup= BeautifulSoup(r.text,"lxml")
	
	for link1 in soup.find("select",{"id":"ctl00_interstitial_websiteSelect"}).find_all("option")[1:]:
		if link1['data-folder']:
			newlink = "https://www.unitypoint.org/"+link1['data-folder']+"/default.aspx"
			page_url = newlink
			r1 = session.get(newlink,headers=headers)
			soup1= BeautifulSoup(r1.text,"lxml")
			try:
				locator_domain= "https://www.unitypoint.org"
				location_type="<MISSING>"
				country_code = "US"
				store_number="<MISSING>"
				location_name = soup1.find("span",{"class":"map-name"}).text.strip()
				phone = list(soup1.find("span",{"class":"map-address"}).stripped_strings)[-1]
				street_address =list(soup1.find("span",{"class":"map-address"}).stripped_strings)[0]
				city = list(soup1.find("span",{"class":"map-address"}).stripped_strings)[-2].split(",")[0]
				state = list(soup1.find("span",{"class":"map-address"}).stripped_strings)[-2].split(",")[1].strip().split(" ")[0]
				zipp = list(soup1.find("span",{"class":"map-address"}).stripped_strings)[-2].split(",")[1].strip().split(" ")[1]
				latitude =  soup1.find("iframe",{"id":"mapFrame"})['src'].split("2d")[1].split("!3d")[1].split("!2")[0].split("!3m")[0]
				longitude =soup1.find("iframe",{"id":"mapFrame"})['src'].split("2d")[1].split("!3d")[0]
				hours_of_operation="<MISSING>"
				store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
				store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
				# logger.info(latitude)
				yield store
			except:
				pass

			
	newlink = "https://marshalltown.unitypoint.org/"
	r2 = session.get(newlink,headers=headers)
	soup2= BeautifulSoup(r2.text,"lxml")
	page_url ="https://marshalltown.unitypoint.org"+ soup2.find("div",{"class":"footerWrapInner site-footer-inner"}).find("div",{"class":"columns"}).find("div",{"class":"column column-third column-3"}).find("a")['href']
	r3 = session.get(page_url,headers=headers)
	soup3= BeautifulSoup(r3.text,"lxml")
	location_type="<MISSING>"
	country_code = "US"
	store_number="<MISSING>"
	hours_of_operation = "<MISSING>"
	location_name="UnityPoint Health - Marshalltown"
	latitude = 	soup3.find_all("iframe")[1]['src'].split("sll=")[1].split(',')[0]
	longitude = soup3.find_all("iframe")[1]['src'].split("sll=")[1].split(',')[1].split("&am")[0].split("&sspn=")[0]
	street_address = list(soup2.find("div",{"class":"footerWrapInner site-footer-inner"}).find("div",{"class":"columns"}).find("div",{"class":"column column-third column-3"}).stripped_strings)[1]
	city = list(soup2.find("div",{"class":"footerWrapInner site-footer-inner"}).find("div",{"class":"columns"}).find("div",{"class":"column column-third column-3"}).stripped_strings)[-1].split(",")[0]
	state = list(soup2.find("div",{"class":"footerWrapInner site-footer-inner"}).find("div",{"class":"columns"}).find("div",{"class":"column column-third column-3"}).stripped_strings)[-1].split(",")[1].strip().split( )[0]
	zipp = list(soup2.find("div",{"class":"footerWrapInner site-footer-inner"}).find("div",{"class":"columns"}).find("div",{"class":"column column-third column-3"}).stripped_strings)[-1].split(",")[1].strip().split( )[1]
	phone = soup2.find("div",{"class":"footerWrapInner site-footer-inner"}).find("div",{"class":"columns"}).find("div",{"class":"column column-third column-1"}).find("li").find("a").text.replace("Main Hospital:",'')
	store1 = ["https://www.unitypoint.org", location_name, street_address, city, state, zipp, country_code,
				store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
	yield store1

	page_url="https://www.unitypoint.org/quadcities/muscatine-directions-and-maps.aspx"
	r3 = session.get("https://www.unitypoint.org/quadcities/muscatine-directions-and-maps.aspx",headers=headers)
	soup3= BeautifulSoup(r3.text,"lxml")
	location_type="<MISSING>"
	country_code = "US"
	store_number="<MISSING>"
	hours_of_operation = "<MISSING>"
	location_name=list(soup3.find("aside",{"class":"page-callouts"}).stripped_strings)[1]
	latitude = 	soup3.find_all("iframe")[2]['src'].split("&sll=")[1].split(",")[0]
	longitude = soup3.find_all("iframe")[2]['src'].split("&sll=")[1].split(",")[1].split("&")[0]
	street_address = soup3.find_all("iframe")[2]['src'].split("&hnear=")[-1].split("&t=m&z=")[0].replace("+",' ').split(",")[0]
	city = soup3.find_all("iframe")[2]['src'].split("&hnear=")[-1].split("&t=m&z=")[0].replace("+",' ').split(",")[1]
	state = soup3.find_all("iframe")[2]['src'].split("&hnear=")[-1].split("&t=m&z=")[0].replace("+",' ').split(",")[-1].strip().split(" ")[0]
	zipp = soup3.find_all("iframe")[2]['src'].split("&hnear=")[-1].split("&t=m&z=")[0].replace("+",' ').split(",")[-1].strip().split(" ")[1]
	phone = list(soup3.find("aside",{"class":"page-callouts"}).stripped_strings)[-1]
	# logger.info(soup3.find_all("iframe")[2]['src'].split("&sll=")[1].split(",")[1].split("&")[0])
	# .find("div",{"class":"columns"}).find("div",{"class":"column column-third column-1"}).find("li").find("a").text.replace("Main Hospital:",'')
	store1 = ["https://www.unitypoint.org", location_name, street_address, city, state, zipp, country_code,
				store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
	yield store1




	
def scrape():
	data = fetch_data()
	write_output(data)

scrape()
