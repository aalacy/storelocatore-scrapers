import requests
from bs4 import BeautifulSoup
from lxml import html
import csv


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
	
	locator_domain ="https://www.siteone.com/"
	country_code="US"
	
	for i in range(808):
		page_url="https://www.siteone.com/store/"+str(i+1)
		print(page_url)
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

		
		r = requests.get(page_url,headers=headers)
		soup=BeautifulSoup(r.text,'lxml')
		divs=soup.findAll(class_="store_map_details")
		for r in divs:
			locs.append(str(r).split('class=strong&gt;')[1].split('#')[0])
			streets.append(str(r).split('&lt;div&gt;')[1].split('/div&gt;')[0].replace('&lt;',''))
			cities.append(str(r).split('&lt;div&gt;')[3].split('&lt;/div&gt;')[0])
			try:
				longs.append(str(r).split('"longitude":"')[1].split('",')[0])
			except:
				longs.append("<MISSING>")
			try:
				lat=str(r).split('"latitude":"')[1].split('",')[0]
				if len(lat)<=4:
					lats.append(lat+'00')
					print(lats)
				else:
					lats.append(lat)
			except:
				lats.append("<MISSING>")
			try:
				zips.append(str(r).split('&lt;div&gt;')[4].split('-')[0].replace('&lt','').replace('/div&gt','').replace(';',''))
			except:
				zips.append("<MISSING>")
			try:	
				ids.append(i+1)
			except:
				ids.append("<MISSING>")
			print(len(locs))
		try:
			states.append(soup.find("title").text.split(', ')[1].split(' |')[0])
		except:
			continue
		try:
			phones.append(soup.find(class_="tel-phone content-product-title").text)
		except:
			continue
		try:
			timing.append(soup.find(class_="detailSection row").text.replace('\n',''))
		except:
			continue
		try:
			types.append(soup.find(class_="store_details_Sname").text.strip())
		except:
			continue
		pages.append(page_url)
		print(pages)
			
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
		row.append(ids[i] if ids[i] else "<MISSING>")
		row.append(phones[i] if phones[i] else "<MISSING>")
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
