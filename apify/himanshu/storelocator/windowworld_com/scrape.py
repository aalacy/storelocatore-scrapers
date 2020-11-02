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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url = "https://www.windowworld.com"
    r = session.get("https://www.windowworld.com/store-locator-by-state")
    soup = BeautifulSoup(r.text, "lxml")
    for provience in soup.find("div",{"class":"spy locator-form locator-form--show-counties"}).find("select",{"name":"county"}).find_all("option"):
        if provience['value'] == "":
            continue
        link = "https://www.windowworld.com/stores/"+str(provience['value'])
        rm = ['https://www.windowworld.com/stores/district-of-columbia',
        'https://www.windowworld.com/stores/alaska',
        'https://www.windowworld.com/stores/montana']
        if link in rm:
            continue
        r1 = session.get(link)
        soup1 = BeautifulSoup(r1.text, "lxml")
        for url in soup1.find_all("a",{"title":"Visit Store Profile"}):
            page_url = url['href']
            r3 = session.get(page_url)
            soup3 = BeautifulSoup(r3.text, "lxml")
            script  = soup3.find('script',{'async':'','type':'text/javascript'})['src']
            r4 = session.get(script)
            if "FATAL_ERROR" in r4.text:
                continue
            json_data = json.loads(r4.text.split('Yext._embed(')[1].rstrip(")").replace('@',''))
            for data in json_data['entities']:
                locator_domain = base_url
                location_name = data['attributes']['locationName'].strip()
                if "address2" in data['attributes']:
                    street_address = data['attributes']['address'].strip() +" "+ str(data['attributes']['address2'])
                else:
                    street_address = data['attributes']['address'].strip()
                city = data['attributes']['city']
                state = data['attributes']['isoRegionCode']
                zipp =  data['attributes']['zip']
                country_code = data['attributes']['countryCode']
                store_number = ''
                phone = data['attributes']['phone'].replace('(','')
                location_type = ''
                latitude = data['attributes']['yextDisplayLat']
                longitude = data['attributes']['yextDisplayLng']
                try:
                    hours = " ".join((data['attributes']['hours']))
                except:
                    hours = "<MISSING>"
                store = []
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zipp if zipp else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')
                store.append(hours if hours else '<MISSING>')
                store.append(page_url if page_url else '<MISSING>')
                yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
