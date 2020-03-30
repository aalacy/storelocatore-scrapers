import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    url1 = "https://cdn.storelocatorwidgets.com/json/b9fb8be18d69e8520c3d2df1717b3b58?callback=slw&_=1581327875153"
    r1 = session.get(url1, headers=headers)
    # print(r)
    soup1 = BeautifulSoup(r1.text, "lxml")
    k = (soup1.text.split('"stores":')[1].split(',"display_order_set":false,"filters":""})')[0])
    json_data = json.loads(k)
    for i in json_data:
        store_number = (i['storeid'])
        location_name = (i['name'])
        if "phone" in i['data']:
            phone = (i['data']['phone'].strip())
        else:
            phone = "<MISSING>"
        state = (i['data']['address'].replace("\n","").replace("\r","").split(",")[-1].split(" ")[1])
        zipp =" ".join(i['data']['address'].replace("\n","").replace("\r","").split(",")[-1].split(" ")[2:])
        try:
            city = (i['data']['address'].replace("\n","").split(",")[0].split("\r")[1])
        except:
            city = (i['data']['address'].replace("\n","").split(",")[0:2][1].split("\r")[-1].replace(" NE B107 Atlanta","Atlanta"))
        street_address = (i['data']['address'].replace("\n","").split(",")[0].split("\r")[0])
        
        latitude = i['data']['map_lat']
        longitude =i['data']['map_lng']
        p = "https://beardpapas.com/locations/"+str(location_name)+"/"
        url1 = (p.lower().replace(" ","-"))
        m = i['data']
        hours_of_operation = "Monday" +" - "+ m['hours_Monday'] +" "+"Tuesday" +" - "+ m['hours_Tuesday']+" "+"Wednesday" +" - "+ m['hours_Wednesday']+" "+"Thursday" +" - "+ m['hours_Thursday']+" "+"Friday" +" - "+ m['hours_Friday']+" "+"Saturday" +" - "+ m['hours_Saturday']+" "+"Sunday" +" - "+ m['hours_Sunday']
        # print(hours_of_operation)
        if zipp in ["90247","77036","V6X 2E3","97005"]:
            city = street_address.split(" ")[-1]
            street_address = " ".join(street_address.split(" ")[:-1])
        if "30092" in zipp:
            city = " ".join(street_address.split(" ")[-2:])
            street_address = " ".join(street_address.split(" ")[:-2])
        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))
        if ca_zip_list:
            zipp = ca_zip_list[-1]
            country_code = "CA"
        if us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"
        store = []
        store.append("https://beardpapas.com/")
        store.append(location_name if  location_name else "<MISSING>" )
        store.append(street_address if  street_address else "<MISSING>" )
        store.append(city if  city else "<MISSING>")
        store.append(state if  state else "<MISSING>" )
        store.append(zipp if  zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>" )
        store.append(store_number if store_number else"<MISSING>")
        store.append(phone if  phone else "<MISSING>" )
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(url1 if  url1 else "<MISSING>" )
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
