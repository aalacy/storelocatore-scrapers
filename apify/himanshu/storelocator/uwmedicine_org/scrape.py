import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.uwmedicine.org"
    page = 0
    while True:
        r = session.get("https://www.uwmedicine.org/search/locations?l=98104&page="+str(page),headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        if soup.find("div",{"class":"clinic-card__street-address"}):
            for link in soup.find_all("div",{"class":"clinic-card__cta uwm-accent-color__purple"}):
                if "locations" not in link.find("a")['href']:
                    continue
                page_url = link.find("a")['href']
                try:
                    r1 = session.get(page_url)
                    soup1 = BeautifulSoup(r1.text, "lxml")
                    data = json.loads(soup1.find(lambda tag: (tag.name == "script") and '"address"' in tag.text).text)['@graph'][-1]
                    location_name = data['name']
                    addr = data['address']['streetAddress'].split(",")
                    if len(addr) == 3 or len(addr) == 4:
                        street_address = addr[1]+" "+ addr[2]
                    else:
                        street_address = data['address']['streetAddress']
                        
                    city = data['address']['addressLocality']
                    state = data['address']['addressRegion']
                    zipp = data['address']['postalCode']
                    try:
                        phone = data['telephone']
                    except:
                        phone = "<MISSING>"
                    location_type = "UW Medicine"
                    try:
                        hours = " ".join(list(soup1.find("table",{"class":"clinic-page__hours-table"}).find("tbody").stripped_strings))
                    except:
                        if soup1.find("div",{"class":"clinic-page__open-current"}):
                            hours = soup1.find("div",{"class":"clinic-page__open-current"}).find("span").text
                        else:
                            hours = "<MISSING>"
                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address.replace("Main Hospital,","").replace("West Clinic","").replace("East Clinic,","").replace("Emergency Department","").replace("McMurray Medical Building,","").replace("Center on Human Development and Disability Center,","").strip())
                    store.append(city)
                    store.append(state)
                    store.append(zipp)
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone )
                    store.append(location_type)
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append(hours)
                    store.append(page_url)
                    store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
                    if str(store[2])+str(store[1]) in addresses:
                        continue
                    addresses.append(str(store[2])+str(store[1]))
                    # print("data===="+str(store))
                    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                    yield store
                except:
                    pass

            

            page+=1
        else:
            break
        
        

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
