import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import http.client
import json
import  pprint
import time


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    address = []
    base_url = "https://www.cityvet.com/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'method': 'GET',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'max-age=0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
    }
    zipcode = [80209,75201]
    for zipcode in zipcode:
        r = session.get('https://www.cityvet.com/find-a-location.php?zip='+str(zipcode),headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        js_text = soup.find_all("script", {"type":"text/javascript"})[1].text.split("0,0,0,0,0,0,0];")[1].split("for (e = 0; e < locArray")[0].split("locArray")
        for i in js_text:
            temp = i.replace("[0]","").replace("[1]","").replace("[2]","").replace("[3]","").replace("[4]","").replace("[5]","").replace("[6]","").replace("[7]","").replace("[8]","").replace("[9]","").replace("[10]","").replace("[11]","").replace("[12]","")
            
            if len(temp)>200:
                try:
                    page_url = "https://www.cityvet.com/" + temp.split("locWebURL =")[1].split(";")[0].replace("'","").strip()
                except:
                    continue
                
                add = temp.split("locInfoAddr2")[0].split("locInfoID   = '")[0].replace("';\n            ","").replace("    = '","").split(",")
                street_address = add[0]
                zipp = add[-1].strip(" ")
                state = add[-2].strip(" ")
                city = add[1].strip(" ")
                phone = temp.split("locInfoHours")[0].replace("';","").replace("\n            ","").split("locInfoPhone = '")[1].replace(".","")
                hours_of_operation1 = temp.split("locInfoMapURL")[0].replace("';","").replace("\n            ","").replace('<div style="margin:4px 0 0 0;"><b>',", ").replace("</b>","").replace("</div>","").replace("<br>",", ").replace("<br/>"," ").replace("M-F","Mon - Fri").split("locInfoHours = '")[1]
                hours_of_operation = hours_of_operation1.split(', Additional')[0]
                location_name = temp.split("locInfoAddr1")[0].replace("';","").replace("\n            ","").split("locInfoName = '")[1]
                store_number = temp.split("locInfoName")[0].replace("';","").replace("\n            ","").split("locInfoID   = '")[1]
                country_code = "US"
                locator_domain = base_url
                location_type = '<MISSING>'
                coords = temp.split("locInfoMapURL =")[1].split(";")[0]
                if "@" in coords:
                    latitude = coords.split("@")[1].split(",")[0]
                    longitude = coords.split("@")[1].split(",")[1]
                else:
                    latitude = '<MISSING>'
                    longitude = '<MISSING>'


                store = []
                store.append(base_url)
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
                store.append(page_url)
                # if store[2] in address:
                #     continue
                # address.append(store[2])
                yield store

            


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
