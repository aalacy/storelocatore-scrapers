import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import shapely


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
    base_url ="https://www.astonmartin.com"
    cord=sgzip.coords_for_radius(100)
    return_main_object=[]
    output=[]
    for cd in cord:
        print(cd)
        try:
            r = session.get("https://www.astonmartin.com/api/enquire/findDealers?latitude="+cd[0]+"&longitude="+cd[1]+"&cultureName=en-US&take=15000").json()
            for loc in r:
                name=loc['Name'].encode('ascii', 'ignore').decode('ascii').strip()
                address=loc['Address']['Street'].encode('ascii', 'ignore').decode('ascii').strip()
                city=loc['Address']['City'].encode('ascii', 'ignore').decode('ascii').strip()
                state=loc['Address']['StateCode'].encode('ascii', 'ignore').decode('ascii').strip()
                country=loc['Address']['CountryCode'].encode('ascii', 'ignore').decode('ascii').strip()
                zip=loc['Address']['Zip']
                storeno=''
                phone=loc['PhoneNumber'].strip()
                if phone=="-":
                    phone=""
                if zip=="-" or zip=="N/A":
                    zip=""
                lat=loc['Address']['Latitude']
                lng=loc['Address']['Longitude']
                hour=''
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
                store.append("astonmartin")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append(hour if hour.strip() else "<MISSING>")
                adrr =name+' '+address + ' ' + city + ' ' + state + ' ' + zip
                if adrr not in output:
                    output.append(adrr)
                    return_main_object.append(store)
        except:
            continue
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
