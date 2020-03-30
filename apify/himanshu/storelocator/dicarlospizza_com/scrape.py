import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import phonenumbers



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
  
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    base_url = "https://www.dicarlospizza.com"
    r =  session.get("https://www.dicarlospizza.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")    
    data = json.loads(soup.find(lambda tag: (tag.name == "script") and "window.siteData =" in tag.text).text.split("window.siteData = ")[1].split(";")[0])
    h = []
    for k in range(0,4):
        for i in data['page']['properties']['contentAreas']['userContent']['content']['cells'][k]['content']['properties']['detailsConfig']['content']['quill']['ops']:
            info  = i['insert'].replace("\n","").replace("> PICK UP","").replace("(",'').replace(")",'').replace(">\ufeff PICK UP","").replace("\ufeff","")
            if info:
                h.append(info)

    location_name = []
    street_address = []
    city = []
    zipp = []
    phone = []
    for i in range(0,len(h),3):
        location_name.append(h[i])
        street_address.append(h[i+1].split("/")[0])
        city.append(h[i])
        zipp.append(h[i+1].split("/")[1])
        phone.append(phonenumbers.format_number(phonenumbers.parse(str(h[i+2].replace(" ","").replace("-",'')), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL))
        # print(phone)

    region = ['OH','OH','OH','OH','OH','PA','SC','WA','WA','WA','WA']
    for index,states in enumerate(region):
        state = states


        store = []
        store.append(base_url)
        store.append(location_name[index])
        store.append(street_address[index])
        store.append(city[index])
        store.append(state)
        store.append(zipp[index])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[index])
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()




