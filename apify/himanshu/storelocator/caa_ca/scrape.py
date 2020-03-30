import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import phonenumbers

session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.caa.ca/"
    page_url = "https://www.atlantic.caa.ca/locations.html"
    r = session.get(page_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for div in soup.find_all("div",{"class":"generic-container"})[1:]:
        location_name = div.find("div",{"class":"Title Title--left"}).text.strip()
        hours = " ".join(list(div.find_all("p")[-1].stripped_strings)).replace("Phone: 902-468-6306","").replace("Fax: 902-468-6303","").strip()
        if len(div.find_all("p")) == 4:
            phone = list(div.find_all("p")[-2].stripped_strings)[0].replace("Phone:","").strip()
        else:
            phone = list(div.find_all("p")[-1].stripped_strings)[0].replace("Phone:","").strip()
        addr = list(div.find_all("p")[0].stripped_strings)
        street_address = " ".join(addr[:-2]).replace("3514 Joseph Howe Drive","3514 Joseph Howe Drive Suite 5")
        if "," in addr[-2]:
            city = addr[-2].split(",")[0]
            state = addr[-2].split(",")[1].replace("N.B.","NB").strip()
            zipp = addr[-1]
        else:
            city = addr[-2].replace("Suite 5","").strip()
            state = addr[-1].split(" ")[0]
            zipp = " ".join(addr[-1].split(" ")[1:])
        
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("CA")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours)
        store.append(page_url)
        # print("data ==="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~````")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
