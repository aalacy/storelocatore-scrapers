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
    base_url = "https://www.trunkclub.com"
    r = session.get("https://www.trunkclub.com/contact",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    data =  soup.find("div",{"class":'container display-flex flex-wrap'})
    link1 = data.find_all("a")
    for i in link1:
        link = (i['href'])
        data5 = base_url + link
        location_request = session.get(base_url + link)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        hours_of_operation = (" ".join(list(location_soup.find("div",{"class":"u-sizeFull u-lg-size3of4 margin-H--auto display-flex justify-content-center margin-T--xl flex-column flex-md-row"}).stripped_strings)))
        store_data = json.loads(location_soup.find("script",{"type":"application/ld+json"}).text)
        # hours_of_operation = (store_data['openingHoursSpecification'])
        # hours =''
        # for h in hours_of_operation:
        #     if type( h['dayOfWeek'])==list:
        #         for day in h['dayOfWeek']:
        #             hours = hours + ' '+day+' ' + h['opens']+' '+h['closes']
        #     else:
        #         hours = hours +' '+(h['dayOfWeek'] + ' '+ h['opens']+ ' '+h['closes'])
        #         if "60654" in store_data["address"]["postalCode"]:
        #             hours = hours.replace("Sunday 11:00","Sunday 11:00 18:00")
        store = []
        addresses = store_data["address"]["streetAddress"].replace("<br /> "," ").replace('Stylist Lounge at Nordstrom NorthPark 8687 N Central Expy | Suite 2000','8687 N Central Expy Suite 2000')
        # if "501 Boylston Street" in store_data["address"]["addressLocality"]:
        #     addresses =  store_data["address"]["addressLocality"]+ ' '+ "Suite 3102"
        # if "525 9th Street NW" in store_data["address"]["addressLocality"]:
        #     addresses =  store_data["address"]["addressLocality"]+ ' '+ "Suite 700"
        #print(addresses)
        store.append("https://www.trunkclub.com")
        store.append(store_data["address"]["addressLocality"].replace("Culver City","Los Angeles").replace("New York","New York City").replace("Washington","Washington D.C."))
        store.append(addresses.replace("525 9th Street NW","525 9th Street NW Suite 700").replace("501 Boylston Street","501 Boylston Street Suite 3102"))
        store.append(store_data["address"]["addressLocality"])
        store.append(store_data["address"]["addressRegion"])
        store.append(store_data["address"]["postalCode"].replace("10002",'10022'))
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data["telephone"])
        store.append(store_data['@type'])
        store.append(store_data["geo"]["latitude"])
        store.append(store_data["geo"]["longitude"])
        store.append(hours_of_operation)
        store.append(data5)
        #print(store)
        return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
