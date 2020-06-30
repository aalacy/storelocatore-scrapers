import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.margs.com"
    r = session.get("https://www.margs.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for link in soup.find_all("a",{"class":"ca1link"}):
        if base_url == link["href"]:
            continue
        state_request = session.get(link["href"],headers=headers)
        state_soup = BeautifulSoup(state_request.text,'lxml')
        geo_locations = []
        for geo in state_soup.find_all("a",{"href":re.compile("/@")}):
            geo_locations.append(geo["href"])
        for location in state_soup.find_all("div",{"data-width":"247"}):
            location_link = location.find("a")["href"]
            if "https://www.margs.com/ellsworth" == location_link:
                continue
           
            location_request = session.get(location_link,headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            try:
                phone = location_soup.find("a",{"data-type":"phone"})['data-content']
            except:
                phone = location_soup.find(lambda tag: (tag.name == "span") and "Phone:" in tag.text).text.replace("Phone:","").strip()

            if location_soup.find("span",text=re.compile("OPENING")):
                continue
            if location_soup.find("span",text=re.compile("Coming Soon")):
                continue
            location_details = []
            for details in location_soup.find_all("h2",{"class":"font_2"}):
                location_details.extend(list(details.stripped_strings))
            for i in range(len(location_details)):
                if location_details == "ONLINE ORDERING" or location_details[i] == "LOCATION DETAILS":
                    location_details = location_details[:i]
                    break
            location_details[3] = location_details[3].replace("\xa0"," ")
            if "We are\xa0open for" in location_details[2]:
                del location_details[2:4]
            store = []
            store.append("https://www.margs.com")
            store.append(location_details[1])
            store.append(location_details[2])
            store.append(location_details[3].split(",")[0])
            store.append(" ".join(location_details[3].split(",")[1].split(" ")[1:-1]))
            store.append(location_details[3].split(",")[1].split(" ")[-1])
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(geo_locations[0].split("/@")[1].split(",")[0])
            store.append(geo_locations[0].split("/@")[1].split(",")[1])
            del geo_locations[0]
            store.append(" ".join(location_details[7:]).replace("\xa0"," ").replace("–","-").split("ONLINE ORDERING")[0].split("Kitchen hours")[0].split("ORDER TAKEOUT")[0].split("DELIVERY SERVICES")[0])
            if store[-1] == "":
                store[-1] = "<MISSING>"
            store.append(location_link)
            yield store
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
