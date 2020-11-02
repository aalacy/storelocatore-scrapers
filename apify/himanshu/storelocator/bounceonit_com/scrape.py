import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url = "https://www.bounceonit.com/"
    req = session.get(base_url)
    soup = BeautifulSoup(req.text, "lxml")
    title = soup.title.text
    #locator_domain
    locator_domain = base_url
    data = []
    #location name
    locations = soup.findAll("div", {"class": "uabb-adv-accordion-item"})
    len(locations)
    for location in locations:
        city = location.findAll("div")[0].text.strip().split(",")[0].strip().lower()
        state= location.findAll("div")[0].text.strip().split(",")[1].strip().lower()
        country_code = "US"
        store_number = "<MISSING>"
        address = location.findAll("div")[2]
        location_type = '<MISSING>'
        if "Coming Soon!" not in address.text:
            row = []
            row.append(locator_domain)
            state1 = state.upper()
            row.append(city+","+state1)
            location_link = address.findAll("a")[0]["href"]
            phoneNo = address.findAll("a")[1].text
            addr_split = address.text.split("Website")[0].replace(",","").strip().split(" ")
            zipcode = addr_split[len(addr_split) - 1]
            street_Addr = " ".join(addr_split[:-3])
            row.append(street_Addr)
            row.append(city)
            row.append(state)
            row.append(zipcode)
            row.append(country_code)
            row.append(store_number)
            row.append(phoneNo)
            row.append(location_type)
            hours_of_operation = "<INACCESSIBLE>"
            req2 = session.get(location_link)
            soup2 = BeautifulSoup(req2.text, "lxml")
            long = ""
            lat = ''
            if city != "syosset":
                try:
                    maplink = soup2.find("a", {"rel": "noopener noreferrer"})["href"]
                    maplink_split = maplink.split("@")[1].strip().split(",")
                    lat = maplink_split[0]
                    long = maplink_split[1]
                except:
                    lat = "41.64401"
                    long = "-73.92398"   
            else:
                maplink = soup2.find("div", {"class": "location-wrap"}).find("a")["href"]
                maplink_split = maplink.split("@")[1].strip().split(",")
                lat = maplink_split[0]
                long = maplink_split[1]
            if "01104" in zipcode:
                lat = lat.replace("41.64401","42.14062")
                long = long.replace("-73.92398","-72.5758")
            row.append(lat)
            row.append(long)
            row.append(hours_of_operation)
            row.append(location_link)
            data.append(row)
    return data
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
