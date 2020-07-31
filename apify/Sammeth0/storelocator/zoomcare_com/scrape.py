from sgrequests import SgRequests
from bs4 import BeautifulSoup
from lxml import html
import csv
import re

def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

	locs = []
	streets = []
	states=[]
	cities = []
	types=[]
	phones = []
	zips = []
	longs = []
	lats = []
	timing = []
	ids=[]
	pages=[]
	
	locator_domain ="https://www.zoomcare.com"
	country_code="US"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
		
	r = session.get(locator_domain)
	soup=BeautifulSoup(r.text,'lxml')

	divs=soup.findAll(class_="sub-list")
	for div in divs:
		page_locator=locator_domain+div.a.get('href')
		if page_locator=="https://www.zoomcare.com/about":
			break
		else:
			r_locator=session.get(page_locator)
			soup_locator=BeautifulSoup(r_locator.text,'lxml')
			if "Goodbye" in soup_locator.h1.text:
				continue
			print(page_locator)
			pages.append(page_locator)
			try:
				locs.append(soup_locator.find(class_="header-3").text)
			except:
				locs.append(soup_locator.title.text.split("|")[0].strip())
			streets.append(soup_locator.find(class_="clinic-address").contents[0].text)
			cities.append(soup_locator.find(class_="clinic-address").contents[2].text.split(',')[0])
			states.append(soup_locator.find(class_="clinic-address").contents[2].text.split(', ')[1])
			try:
				zips.append(soup_locator.find(class_="map-info-column").a.get('href').split('+')[-1])
			except:
				try:
					zips.append(str(soup_locator.findAll("script")[-9]).split('postalCode="')[1].split('"')[0])
				except:
					try:
						map_link = soup_locator.find('iframe')['src']
						zip_code = re.findall(r'\+[0-9]{5}', map_link)[0][1:]
						zips.append(zip_code)
					except:
						zips.append("<MISSING>")
			types_list=soup_locator.findAll(class_="col-8")
			list=[]
			for type in types_list:
				list.append(type.h2.text)
			types.append(', '.join(list))
			lats.append(str(soup_locator.findAll("script")[-9]).split('latitude="')[1].split('"')[0])
			longs.append(str(soup_locator.findAll("script")[-9]).split('longitude="')[1].split('"')[0])
			try:
				timing.append(soup_locator.find(class_="Clinic__body__hours").text.strip())
			except:
				timing.append("<MISSING>")
		
	return_main_object=[]
	for i in range(len(locs)):
		row = []
		row.append(locator_domain)
		row.append(locs[i] if locs[i] else "<MISSING>")
		row.append(streets[i] if streets[i] else "<MISSING>")
		row.append(cities[i] if cities[i] else "<MISSING>")
		row.append(states[i] if states[i] else "<MISSING>")
		row.append(zips[i] if zips[i] else "<MISSING>")
		row.append(country_code)
		row.append("<MISSING>")
		row.append("<MISSING>")
		row.append(types[i] if types[i] else "<MISSING>")
		row.append(lats[i] if lats[i] else "<MISSING>")
		row.append(longs[i] if longs[i] else "<MISSING>")
		row.append(timing[i] if timing[i] else "<MISSING>")
		row.append(pages[i] if pages[i] else "<MISSING>")
		
		return_main_object.append(row)
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
