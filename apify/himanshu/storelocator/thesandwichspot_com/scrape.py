import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as BS
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thesandwichspot_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url1="https://www.powr.io/plugins/map/wix_view.json?cacheKiller=1565172087400&compId=comp-jcccswek&deviceType=desktop&height=462&instance=yHGw_8WbCn7m6c6pR2XU186ZyTI_PDlSOhco9oNrjxk.eyJpbnN0YW5jZUlkIjoiN2IwNWYwOWYtMjE1NC00YTQxLTlmYmQtODc4Yzg5YTU4MWQ2IiwiYXBwRGVmSWQiOiIxMzQwYzVlZC1hYWM1LTIzZWYtNjkzYy1lZDIyMTY1Y2ZkODQiLCJzaWduRGF0ZSI6IjIwMTktMDgtMDdUMTA6NDE6NDAuNzQzWiIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlwQW5kUG9ydCI6IjEyMy4yMDEuMjI2LjEyOC8zMzQ5NCIsInZlbmRvclByb2R1Y3RJZCI6ImJ1c2luZXNzIiwiZGVtb01vZGUiOmZhbHNlLCJhaWQiOiI1N2Q5YjhmMS1jYmIzLTRmNGMtOWJmZC0zMTI3YTZkMGQ2ZWIiLCJzaXRlT3duZXJJZCI6IjkxOGU5NTAxLTQwMGMtNDcwNS1iM2VlLTc2ZDI5NWYxM2Y2ZiJ9&locale=en&pageId=e97g9&siteRevision=349&viewMode=site&width=733"
    json_data = session.get(base_url1).json()['content']['locations']
    lat_lng = {}
    for coords in json_data:
       
        lat_lng[coords['name'].replace("<p>","").replace("</p>","").replace("65th","65th Street").replace("Gateways Oaks","Gateway Oaks").replace("Elsie Ave","Elsie").replace("Stevens Creek","Steven's Creek")] = {"lat":coords['lat'],"lng":coords['lng']}
    lat_lng['Rocklin'] = {"lat":"<MISSING>","lng":"<MISSING>"}
    lat_lng['Stevenson Ranch'] = {"lat":"<MISSING>","lng":"<MISSING>"}
    base_url= "https://www.thesandwichspot.com/"
    soup= BS(session.get("https://www.thesandwichspot.com/locations").text,"lxml")
    for div in soup.find_all("div",{"id":re.compile("inlineContent-gridContainer")})[2:35]:
        location_name = div.find("h4").text
        # logger.info(location_name)
        addr = list(div.find_all("div",{"data-packed":"false"})[1].stripped_strings)
        street_address = addr[0].replace("\xa0"," ")
        if len(addr[1].split(",")) == 3:
            street_address+= " " + addr[1].split(",")[0]
            city = addr[1].split(",")[1]
            state = addr[1].split(",")[2].split()[0]
            zipp = addr[1].split(",")[2].split()[1]
        else:
            city = addr[1].split(",")[0]
            state = addr[1].split(",")[1].split()[0]
            zipp = addr[1].split(",")[1].split()[1]
        phone = addr[-1].replace("Phone:","").strip()
        try:
            lat = lat_lng[location_name]['lat']
            lng = lat_lng[location_name]['lng']
        except:
            # logger.info(location_name)
            lat = "<MISSING>"
            lng = "<MISSING>"
        page_url = div.find_all("a")[-1]['href']
        location_soup = BS(session.get(page_url).text, "lxml")
        hours = " ".join(list(location_soup.find_all("div",{"class":"txtNew"})[4].stripped_strings)).split("HOURS:")[1]
        store = [base_url, location_name, street_address, city, state, zipp, "US","<MISSING>", phone, "<MISSING>", lat, lng, hours.strip(), page_url]
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
