import csv
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Cookie': 'ASP.NET_SessionId=kstgb3jkaa1k4uecjmqwml25; TS01f976b6=01e8de0f2c12f21180024dde3be250630cc2d73d7f85c67d6ed442acf8407209bf9706b7206a846ae92265f36e3f9b85560156e06fef5a40a5888337f81596082b4e199974; ASP.NET_SessionId=fuw3qhefmwwpliskmc4lnzmy; TS01f976b6=01e8de0f2c69339f95f97f5a8185f5cbb3b61e90779f40c2cdb19e7d3b62f697f99e5827d6ce48ebe57070ede1f7116704af37271fe8610abb704cc9424d1bdf39f4139274',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
        }
    base_url = "https://www.johnsonbank.com"
    for i in range(1,47):
        page_url = "https://johnsonbank.locatorsearch.com/ATMBranchDtls.aspx?Loc="+str(i)
        r = session.get(page_url,headers=headers)
        soup = BeautifulSoup(r.text,'lxml')
        location_name = soup.find("span",{"id":"LInstitutionName"}).text.replace("Lobby Temporarily Closed","").replace("Drive-thru Open","").replace("| ,","").strip()
        street_address = soup.find("span",{"id":"LStreet"}).text
        city = soup.find("span",{"id":"LCity"}).text
        state = soup.find("span",{"id":"LState"}).text
        zipp = soup.find("span",{"id":"LZipCode"}).text
        phone = soup.find("span",{"id":"LPhone"}).text.replace("Tel:","").strip()
        hours_of_operation = " ".join(list(soup.find("span",{"id":"LBranchHours"}).stripped_strings))
        coord = str(soup).split("position: new google.maps.LatLng(")[1].split("),")[0].split(",")
        lat = coord[0]
        lng = coord[1]
        store=[]
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("Branch")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation.strip() else "<MISSING>")
        store.append(page_url)
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

