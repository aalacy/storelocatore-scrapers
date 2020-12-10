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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation" ,"page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    
    address = []
    
    base_url= "https://lovinghut.us/"
    r= session.get(base_url, headers=headers)
    soup=BeautifulSoup(r.text, "lxml")
    states=soup.find_all("ul",{"class":"sub-menu"})
    for i in states:
        for j in i.find_all("li"):
            links = j.find("a")['href']
            if links =="#":
                continue
            else:
                r1 = session.get(links, headers=headers)
                soup1 = BeautifulSoup(r1.text, "lxml")
                location_name = soup1.find("h1",{"class":"page-title h1 intro-title"}).text
                temp_add = list(soup1.find("address",{"class":"text-white"}).stripped_strings)
                if location_name == "Loving Hut Claremont":
                    street_address = " ".join(temp_add[0:2])
                    city = temp_add[2].split(",")[0]
                    state = temp_add[2].split(" ")[-2]
                    zipp = temp_add[2].split(" ")[-1]
                    phone = temp_add[3]
                else:
                    street_address = temp_add[0]
                    city = temp_add[1].split(",")[0]
                    state = temp_add[1].split(" ")[-2]
                    zipp = temp_add[1].split(" ")[-1]
                    phone = temp_add[2]
                hoo = list(soup1.find("div",{"class":"textwidget openhours"}).stripped_strings)
                hours_of_operation = " ".join(hoo)
                

                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(hours_of_operation.replace('TEMPORARY NEW HOURS : ',''))
                store.append(links)
                store = [x.replace("–","-") if type(x) == str else x for x in store]
                store = [x.strip() if type(x) == str else x for x in store]
                if store[2] in address:
                    continue
                address.append(store[2])
                yield store


def scrape():
   
    data = fetch_data()
    write_output(data)


scrape()
