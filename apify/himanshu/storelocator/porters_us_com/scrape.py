import csv
from bs4 import BeautifulSoup
import re
import json
import requests
from sgrequests import SgRequests
session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "raw_address", 
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }

    base_url = "https://porters.us.com"
    r =  session.get("https://porters.us.com/visit-porters/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")   
    data = soup.find(lambda tag: (tag.name == "script") and "iwmparam" in tag.text).text.split("var iwmparam = ")[1].split("/* ]]> */")[0].replace(":false}];",":false}").replace('[{"','{"')
    json_data = json.loads(data)
    info = json_data['placestxt'].replace("&#44",'').split(",,#438094;")
    for num in range(len(info)):
        addr = info[num].strip()
        if len(addr.split(",")[0].split(" ")) == 2:
            latitude = addr.split(",")[0].split(" ")[0].strip()
            longitude = addr.split(",")[0].split(" ")[1].strip()
            store_number = addr.split(",")[1].strip()
            state = re.findall(r'([A-Z]{2})', str(addr))[-1]
            zipp_list = re.findall(r'[0-9]{5}',str(addr))
            if zipp_list:
                zipp = zipp_list[-1]
            else:
                zipp = "<MISSING>"
            raw_address = re.sub(r'\s+'," ",addr.split(",")[2].replace('"','').replace("\t","").strip())
            

            
            # if "\t" in addr:
            #     street_address = addr.split(",")[2].split("\t")[0].replace('"',"").strip()
            #     city = addr.split(",")[2].split("\t")[1].strip()
            # else:
            #     raw1 = re.sub(r'\s+'," ",addr)
            #     raw = (raw1.split(",")[2].split(" "))
            #     if raw[-1].isdigit():
            #         del raw[-1]
            #     if len(raw[-1]) == 2:
            #         del raw[-1]
                # street_address = " ".join(raw[:-1])
                # city = raw[-1]
        else:
            continue
   
        store = []
        store.append(base_url)
        store.append("<MISSING>")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append("<MISSING>" )
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store.append(raw_address)
        store.append("<MISSING>")
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        # print("data===="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
