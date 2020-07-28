import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # print("start")
    address = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }
    base_url = "https://www.genesishealth.com"
    for i in range(1,18):
        r = session.get("https://www.genesishealth.com/facilities/location-search-results/?searchId=25a2f63c-8cd0-ea11-a82f-000d3a611816&sort=13&page="+str(i), headers=headers)
        # print(r)
        soup = BeautifulSoup(r.text, "lxml")
        data = soup.find("div",{"class":"LocationsList"}).find_all("li")
        for j in data:
            data_1 = (j.find("a")['href'])
            link_data = ''
            if "../../" in data_1:
                link_data = ("https://www.genesishealth.com/"+str(data_1)).replace("/../../","/")
                # print(link_data)
            elif "https:" in data_1:
                link_data = data_1
                # print(link_data)
            else:
                link_data = ("https://www.genesishealth.com/facilities/"+str(data_1)).replace("/../","/")
                r1 = session.get(link_data)
                soup1 = BeautifulSoup(r1.text, "lxml")
                data_8 = soup1.find("script",{"type":"application/ld+json"}).text
                a = json.loads(data_8)
                data_9 = a['url']
                if "?id" in data_9:

                    store_number = (data_9.split("=")[1])
                else:
                    store_number = "<MISSING>"
                store = []
                store.append(base_url.encode('ascii', 'ignore').decode('ascii') if base_url else "<MISSING>")
                store.append(a['name'] if a['name'].encode('ascii', 'ignore').decode('ascii') else "<MISSING>") 
                store.append(a['address']['streetAddress'].encode('ascii', 'ignore').decode('ascii') if a['address']['addressRegion'] else "<MISSING>")
                store.append(a['address']['addressLocality'].encode('ascii', 'ignore').decode('ascii') if a['address']['addressLocality'] else "<MISSING>")
                store.append(a['address']['addressRegion'].encode('ascii', 'ignore').decode('ascii') if a['address']['addressRegion'] else "<MISSING>")
                zipp = ''
                if "postalCode" in a['address']:
                    zipp = a['address']['postalCode']
                else:
                    zipp = "<MISSING>"
                store.append( zipp.encode('ascii', 'ignore').decode('ascii') if zipp else "<MISSING>")
                store.append("<MISSING>")
                store.append(store_number.encode('ascii', 'ignore').decode('ascii') if store_number else"<MISSING>") 
                phone = ''
                if "telephone" in a:
                    phone = a['telephone']
                else:
                    phone = "<MISSING>"
                store.append(phone.encode('ascii', 'ignore').decode('ascii') if phone else "<MISSING>")
                store.append(a['@type'].encode('ascii', 'ignore').decode('ascii'))
                latitude = ''
                longitude = ''
                if "geo" in a:
                    if "latitude" in a['geo']:
                        latitude = a['geo']['latitude']
                    else:
                        latitude = "<MISSING>"
                    if "longitude" in a['geo']:
                        longitude = a['geo']['longitude']
                    else:
                        longitude = "<MISSING>"
                else:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                store.append( latitude.encode('ascii', 'ignore').decode('ascii') if latitude else "<MISSING>")
                store.append(longitude.encode('ascii', 'ignore').decode('ascii') if longitude  else "<MISSING>")
                hours = ''
                if "openingHoursSpecification" in a:
                    hours1 = a['openingHoursSpecification']
                    # print(hours1)
                    for i1 in hours1:
                        hours =hours +" "+ i1['dayOfWeek'].replace("http://schema.org/","")+" "+i1['opens']+" - "+i1['closes']
                
                else:
                    hours = "<MISSING>"
                # print(hours)
                store.append(hours.strip().encode('ascii', 'ignore').decode('ascii') if hours else "<MISSING>")
                store.append(a['url'].encode('ascii', 'ignore').decode('ascii') if a['url'] else "<MISSING>")
                
                if store[2] in address :
                    continue
                address.append(store[2])
                yield store 
                # print(json_data)           
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
