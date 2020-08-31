import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip

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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 200
    coord = search.next_coord()
    base_url ="https://www.beefjerkyoutlet.com"

    while coord:
        result_coords = []

        location = "https://www.beefjerkyoutlet.com/location-finder?proximity_lat="+str(coord[0])+"&proximity_lng="+str(coord[1])
        #print(location)
        r = session.get(location,headers=headers)
        soup=BeautifulSoup(r.text,'lxml')

        main=soup.find('ul',{'class':'geolocation-common-map-locations'}).find_all('li')[:91]
        for ltag in main:
            name=ltag.find('span',{'class':'title'}).text.strip()
            lat=ltag['data-lat']
            lng=ltag['data-lng']
            try:
                link=ltag.find("div",{"class":"location-content"}).find('a',text="Shop this store")['href']
                page_url = base_url+link
            except:
                page_url = "<MISSING>"

            temp_add = ltag.find("p",{"class":"address"})
            try:
                address_line1 = temp_add.find("span",{"class":"address-line1"}).text
                address_line2 = temp_add.find("span",{"class":"address-line2"}).text
                address = address_line1 + " " + address_line2
            except:
                address_line1 = temp_add.find("span",{"class":"address-line1"}).text
                address = address_line1

            city = temp_add.find("span",{"class":"locality"}).text
            state = temp_add.find("span",{"class":"administrative-area"}).text
            zipp = temp_add.find("span",{"class":"postal-code"}).text
            country = temp_add.find("span",{"class":"country"}).text
            if country == "United States":
                country_code = "US"
            phone = ltag.find("div",{"class":"location-content"}).find("a").text
            #print(phone)
            hour = ltag.find("div",{"class":"location-content"}).find_all("div",{"class":"field-item"})
            hoo = []
            for h in hour:
                hoo.append(h.text)
            hours_of_operation = ", ".join(hoo).replace("For Curbside Orders please call during normal business hours to schedule your Pickup","").replace("Store Temporarily Closed - Still Processing Online Orders","<MISSING>").replace("Hours may vary,Please call for hours","")

            result_coords.append((lat,lng))
            store=[]
            store.append(base_url)
            store.append(name.encode('ascii', 'ignore').decode('ascii') if name else "<MISSING>")
            store.append(address.encode('ascii', 'ignore').decode('ascii') if address else "<MISSING>")
            store.append(city.encode('ascii', 'ignore').decode('ascii') if city else "<MISSING>")
            store.append(state.encode('ascii', 'ignore').decode('ascii') if state else "<MISSING>")
            store.append(zipp.encode('ascii', 'ignore').decode('ascii') if zipp else "<MISSING>")
            store.append(country_code.encode('ascii', 'ignore').decode('ascii') if country_code else "<MISSING>")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("beefjerkyoutlet")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hours_of_operation.encode('ascii', 'ignore').decode('ascii') if hours_of_operation.strip() else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store
        
        if len(main) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(main) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
