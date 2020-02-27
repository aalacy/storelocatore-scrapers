import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.wyndhamhotels.com/en-ca/travelodge"
    r = requests.get(base_url+'/locations')
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find_all('li',{'class':"property"})
    for li in main:
        link=li.find('a')['href']
        # print(link)
        try:
            r1 = requests.get("https://www.wyndhamhotels.com"+link)
        except:
            pass
        soup1 = BeautifulSoup(r1.text,"lxml")
        script=soup1.find_all('script')
        for scr in script:
            if "var overview_lat" in scr.text:
                try:
                    link1="https://www.wyndhamhotels.com/BWSServices/services/search/property/search?propertyId="+scr.text.split('"')[1]+"&isOverviewNeeded=true&isAmenitiesNeeded=true&channelId=tab&language=en-ca"
                except:
                    pass
                r1 = requests.get(link1).json()
                if "properties" in r1:
                    for d in r1['properties']:
                        hour=""
                        hour+=d['checkInTime'] if d['checkInTime'] else ''
                        hour+='-'+d['checkOutTime'] if d['checkOutTime'] else ''
                        name=d['name']
                        address=d['address1']
                        if d['address2']:
                            address+=" "+d['address2']
                        city=d['city']
                        state=d['stateCode']
                        country=d['countryCode']
                        zip=d['postalCode']
                        lat=d['latitude']
                        lng=d['longitude']
                        phone=d['phone1']
                        storeno=d['propertyId']
                        store=[]
                        store.append(base_url)
                        store.append(name if name else "<MISSING>")
                        store.append(address if address else "<MISSING>")
                        store.append(city if city else "<MISSING>")
                        store.append(state if state else "<MISSING>")
                        store.append(zip if zip else "<MISSING>")
                        store.append(country if country else "<MISSING>")
                        store.append(storeno if storeno else "<MISSING>")
                        store.append(phone if phone else "<MISSING>")
                        store.append("Travelodge")
                        store.append(lat if lat else "<MISSING>")
                        store.append(lng if lng else "<MISSING>")
                        store.append(hour if hour else "<MISSING>")
                        print(store)
                        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
