import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json


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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    adressess = []
    base_url = "http://sevabeauty.com/"
    get_url = "http://sevabeauty.com/location/"
    r = session.get(get_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    loc = soup.find("div",{"class":"page-content"})
    for i in loc.find_all("p")[1:]:
        locator_domain = base_url
        location = i.text.split("\n")
        location_name = location[0]
        street_address = location[1].split("(")[0].strip()
        temp_ad = location[2].split(" ")
        if len(temp_ad) == 3:
            city = temp_ad[0].replace(",","")
            state = temp_ad[1]
            if city == "Cayey":
                zipp = "00" + temp_ad[2]
            else:
                zipp = temp_ad[2]
        else:
            city = temp_ad[0] +" "+temp_ad[1]
            state = temp_ad[2]
            zipp = temp_ad[3]

        phone = location[3]

        store = []
        store.append(locator_domain)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("SEVA BEAUTY")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        if store[2] in adressess:
            continue
        adressess.append(store[2])
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store
def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)
scrape()
