import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation" ,"page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    location_url= "https://locations.ctownsupermarkets.com/"
    r_locations= requests.get(location_url, headers=headers)
    soup = BeautifulSoup(r_locations.text, "lxml")
    data = (soup.find_all("script")[17])
    k = ''.join(data.text.split('=')[1:])
    json_data = json.loads(k.replace('null};','null}'))
    for i in json_data["dataLocations"]["collection"]["features"]:
        location_name = i["properties"]["name"]
        store_number = '<MISSING>'
        link = "https://locations.ctownsupermarkets.com/"+i["properties"]["slug"]
        r1 = requests.get(link, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        km = (soup1.find("script",{"type":"application/ld+json"}).text)
        state  = (soup1.find("span",{"itemprop":"addressRegion"}).text.strip())
        json_data1 = json.loads(km)
        street_address = json_data1['address']['streetAddress']
        city = json_data1['address']['addressLocality']
        zipp = json_data1['address']['postalCode']
        phone = json_data1['telephone']
        country_code = json_data1['address']['addressCountry']
        latitude = json_data1['geo']['latitude']
        longitude = json_data1['geo']['longitude']
        store_number = json_data1['branchCode']
        location_type = json_data1['@type']
        hours = json_data1['openingHoursSpecification']
        mp =''
        for k in hours:   
            d = datetime.strptime(k['opens'], "%H:%M")
            t=d.strftime("%I:%M %p")
            d1 = datetime.strptime(k['closes'], "%H:%M")
            t1=d1.strftime("%I:%M %p")
            mp = mp +' '+k['dayOfWeek']+ ' '+ t + ' '+  t1 
        hours_of_operation = (mp.strip())
        store=[]   
        store.append("https://www.ctownsupermarkets.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(link)
        #print(store)
        yield store 


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
