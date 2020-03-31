import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
import requests
session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }

    base_url = "http://www.mysalonsuite.com"
    json_data = requests.get("https://easylocator.net/ajax/search_by_lat_lon/Weebly%20Hearts/33.5973469/-112.1072528/null/null").json()['physical']
    for data in json_data:
        if data['street_address'] == "Coming Soon!" or data['street_address'] == "Opening Soon!":
            continue
        location_name = data['name'].replace("MY SALON Suite of Whitney Ranch","Whitney Ranch")
        street_address = (str(data['street_address']) +" "+ str(data['street_address_line2']) +" "+ str(data['street_address_line3'])).replace("(at 4th Avenue North)","").replace("Now Open!","").replace("(Next to Regal Cinema)","").strip()
        if "Coming Soon" in street_address:
            continue
        city = data['city']
        state = data['state_province']
        zipp = data['zip_postal_code'].replace("6825","06824")
        if street_address == "1559 CA-1, Hermosa Beach, CA 90254":
            city = "Hermosa Beach"
            state = "CA"
            zipp = "90254"
        street_address = street_address.replace("1559 CA-1, Hermosa Beach, CA 90254","1559 CA-1")
        country_code = data['country'].replace("Canada","CA")
        if len(zipp) == 5 or len(zipp) == 0:
            country_code = "US"
        phone = data['phone'].replace("MSS","").replace("MYSS","").strip()
        latitude = data['lat']
        longitude = data['lon']
        if data['website_url']:
            if 'http:' in data['website_url']:
                page_url = data['website_url']
            else:
                page_url = "http://"+data['website_url']
        else:
            page_url = "http://www.mysalonsuite.com/"+str(location_name.replace(" ","-").lower())
        if street_address:
            street_address = street_address
        else:
            r1 = requests.get(page_url)
            soup1 = BeautifulSoup(r1.text, "lxml")
            street_address1 = list(soup1.find("span",{"class":"wsite-text wsite-headline-paragraph"}).stripped_strings)
            street_address =street_address1[0]
        if zipp:
            zipp = zipp
        else:
            r1 = requests.get(page_url)
            soup1 = BeautifulSoup(r1.text, "lxml")
            zipp1 = list(soup1.find("span",{"class":"wsite-text wsite-headline-paragraph"}).stripped_strings)
            zipp = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp1))[0]
            print(zipp)
           # street_address =street_address1[0]# phone = number[-1].replace("949) 424-6770","(949) 424-6770").replace("63-608-9772","863-608-9772").replace("Leasing Phone Number:","")
        if phone:
            phone = phone
        else:
            r1 = requests.get(page_url)
            soup1 = BeautifulSoup(r1.text, "lxml")
            number = list(soup1.find("span",{"class":"wsite-text wsite-headline-paragraph"}).stripped_strings)
            if number[-1] == ".":
                del number[-1]
            phone = number[-1].replace("949) 424-6770","(949) 424-6770").replace("63-608-9772","863-608-9772").replace("Leasing Phone Number:","")
    
        store = []
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code)
        store.append("<MISSING>") 
        store.append(phone.replace("813.602.1 (677)","813.602.1677") if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store.append(page_url)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # print("data~~~~~~"+str(store))
        yield store

        




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
