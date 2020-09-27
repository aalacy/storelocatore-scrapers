import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    addressess = []
    headers = {

		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
	}
    base_url = "https://www.redroof.com/hometowne-studios"
    location_url = "https://www.redroof.com/extendedstay/hometownestudios/all-locations"
    r = session.get(location_url,headers=headers)
    soup=BeautifulSoup(r.text,'lxml')
    link = soup.find("div",{"class":"rich-text-content"}).find_all("a")
    for i in link:
        page_url = "https://www.redroof.com/"+i['href']
        r1 = session.get(page_url,headers=headers)
        soup1 = BeautifulSoup(r1.text,'lxml')
        jd = json.loads(str(soup1).split('Utilities.SDL.Add("ServicePropertyDetails", ')[1].split(');')[0])
        location_name = jd['Description']
        street_address = jd['Street1']
        city = jd['City']
        state = jd['State']
        zipp = jd['PostalCode']
        country_code = jd['Country']
        store_number = "<MISSING>"
        phone = jd['PhoneNumber']
        location_type = jd['PropertyType']
        latitude = jd['Latitude']
        longitude = jd['Longitude']
        hours_of_operation = "<MISSING>"


        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code)
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type)
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
