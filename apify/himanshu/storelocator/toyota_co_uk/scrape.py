
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import time
session = SgRequests()


def request_wrapper(url,method,headers,data=None):
	request_counter = 0
	if method == "get":
		while True:
			try:
				r = requests.get(url,headers=headers)
				return r
				break
			except:
				time.sleep(2)
				request_counter = request_counter + 1
				if request_counter > 10:
					return None
					break
	elif method == "post":
		while True:
			try:
				if data:
					r = requests.post(url,headers=headers,data=data)
				else:
					r = requests.post(url,headers=headers)
				return r
				break
			except:
				time.sleep(2)
				request_counter = request_counter + 1
				if request_counter > 10:
					return None
					break
	else:
		return None


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 
    addresses = []
    base_url = "https://www.toyota.co.uk/"

    # print("remaining zipcodes: " + str(len(search.zipcodes)))
    result_coords = []
    soup = session.get("https://www.toyota.co.uk/api/dealer/drive/-0.1445783/51.502436?count=1000&extraCountries=im|gg|je&isCurrentLocation=false").json()
    for data in soup['dealers']:
        street_address1=''
        location_name = data['name']
        # print(location_name)
        street_address1 = data['address']['address1'].strip()
        if street_address1:
            street_address1=street_address1
        street_address =street_address1+ ' '+ data['address']['address'].strip()
        city = data['address']['city']
        state = data['address']['_region']
        zipp = data['address']['zip']
        hours="<MISSING>"
        hours = ''
        for i in data['openingDays']:
            hours += ' '+(i['startDay'] + ' - '+i['endDay'] +' '+ i['hours'][0]['startTime']+' '+ i['hours'][0]['endTime'])
        # print(hours)
        phone = data['phone']
        if "geo" in  data['address']:
            lat = data['address']['geo']['lat']
            lng = data['address']['geo']['lon']
        else:
            lat ="<MISSING>"
            lng ="<MISSING>"
        page_url = data['url']
        store_number = "<MISSING>"
       
        headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
	    }
        # print(page_url+"/about-us#anchor-views-opening_hours-block_3")
        # r = request_wrapper(page_url+"/about-us#anchor-views-opening_hours-block_3","get", headers=headers)
        # try:
        #     hours = " ".join(list(bs(r.content, "lxml").find("div",{"class":"views-row views-row-1 views-row-odd views-row-first views-row-last zero-dep"}).stripped_strings))
        # except:
        #     hours="<MISSING>"
        
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("UK")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url if page_url else "<MISSING>")     
    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store

     
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
