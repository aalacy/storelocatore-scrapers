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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.wyndhamhotels.com/bin/propertypages.json?locale=en-us&brandId=DX"
    r = session.get(base_url).json()['subcategory']
    return_main_object = []
    for i in range(len(r)):
        country=r[i]['name']
        if country=="United States":
            country="US"
        if country=="Canada":
            country="CA"
        if "subcategory" in r[i]:
            for val in r[i]['subcategory']:
                for data in val['properties']:
                    state=data['state']
                    city=data['city']
                    link=data['path']
                    r1 = session.get(link)
                    soup = BeautifulSoup(r1.text,"lxml")
                    mainadd = json.loads(soup.find('script',{"type":"application/ld+json"}).text)
                    script=soup.find_all('script')
                    hour=""
                    for scr in script:
                        if "var overview_lat" in scr.text:
                            link1="https://www.wyndhamhotels.com/BWSServices/services/search/property/search?propertyId="+scr.text.split('"')[1]+"&isOverviewNeeded=true&isAmenitiesNeeded=true&channelId=tab&language=en-us"
                            r1 = session.get(link1).json()
                            if "properties" in r1:
                                for d in r1['properties']:
                                    hour=d['checkInTime']+'-'+d['checkOutTime']
                    store = []
                    store.append("https://www.wyndhamhotels.com/dolce")
                    store.append(mainadd['name'])
                    store.append(mainadd['address']['streetAddress'])
                    store.append(city)
                    store.append(state)
                    if(country=='US'):
                        store.append(mainadd['address']['postalCode'].split(' - ')[0].strip().replace(" ","").replace(" ",""))
                    else:
                         store.append(mainadd['address']['postalCode'].strip().replace(" ",""))
                    store.append(country)
                    store.append("<MISSING>")
                    try:
                        store.append(mainadd['telephone'])
                    except:
                        store.append("<MISSING>")
                    store.append("wyndhamhotels")
                    try:
                        store.append(mainadd['geo']['latitude'])
                        store.append(mainadd['geo']['longitude'])
                    except:
                        store.append("<MISSING>")
                        store.append("<MISSING>")
                    if hour != '':
                        store.append(hour)
                    else:
                        store.append("<MISSING>")
                    return_main_object.append(store)
        else:
            for data in r[i]['properties']:
                state=data['state']
                city=data['city']
                link=data['path']
                r1 = session.get(link)
                soup = BeautifulSoup(r1.text,"lxml")
                hour=""
                mainadd = json.loads(soup.find('script',{"type":"application/ld+json"}).text)
                script=soup.find_all('script')
                for scr in script:
                    if "var overview_lat" in scr.text:
                        link1="https://www.wyndhamhotels.com/BWSServices/services/search/property/search?propertyId="+scr.text.split('"')[1]+"&isOverviewNeeded=true&isAmenitiesNeeded=true&channelId=tab&language=en-us"
                        r1 = session.get(link1).json()
                        if "properties" in r1:
                            for d in r1['properties']:
                                hour=d['checkInTime']+'-'+d['checkOutTime']
                store = []
                store.append("https://www.wyndhamhotels.com/dolce")
                store.append(mainadd['name'])
                store.append(mainadd['address']['streetAddress'])
                store.append(city)
                store.append(state)
                store.append(mainadd['address']['postalCode'].strip())
                store.append(country)
                store.append("<MISSING>")
                try:
                    store.append(mainadd['telephone'])
                except:
                    store.append("<MISSING>")
                store.append("wyndhamhotels")
                try:
                    store.append(mainadd['geo']['latitude'])
                    store.append(mainadd['geo']['longitude'])
                except:
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                if hour != '':
                    store.append(hour)
                else:
                    store.append("<MISSING>")
                return_main_object.append(store)

    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
