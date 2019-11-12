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
    data = ''.join(soup.find_all("script")[14].text.split('=')[1:])
    json_data = json.loads(data.replace('{}};','{}}'))
    for i in json_data["dataLocations"]["collection"]["features"]:
        latitude = i["geometry"]["coordinates"][1]
        longitude = i["geometry"]["coordinates"][0]
        location_name = i["properties"]["name"]
        store_number = '<MISSING>'
        link = "https://locations.ctownsupermarkets.com/"+i["properties"]["slug"]
        r = requests.get(link, headers=headers)
        soup1 = BeautifulSoup(r.text, "lxml")
        data1 =''.join(soup1.find_all("script")[15].text.split('=')[1:])
        json_data1 = json.loads(data1.replace('{}};','{}}'))
        address2 = json_data1['dataLocations']['selectedLocation']['properties']['addressLine2']
        street_address = json_data1['dataLocations']['selectedLocation']['properties']['addressLine1']
        city = json_data1['dataLocations']['selectedLocation']['properties']['city']
        state = json_data1['dataLocations']['selectedLocation']['properties']['province']
        zipp = json_data1['dataLocations']['selectedLocation']['properties']['postalCode']
        phone = json_data1['dataLocations']['selectedLocation']['properties']['phoneNumber']
        hours = json_data1['dataLocations']['selectedLocation']['properties']['hoursOfOperation']
        hours_of_operation =''
        for k in hours:
            for i in hours[k]:
                d = datetime.strptime(i[0], "%H:%M")
                t=d.strftime("%I:%M %p")
                d1 = datetime.strptime(i[1], "%H:%M")
                t1=d1.strftime("%I:%M %p")
                hours_of_operation = hours_of_operation + ' '+ k + ' '+ t + ' '+  t1  
            
        store=[]   
        store.append("https://www.ctownsupermarkets.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
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
