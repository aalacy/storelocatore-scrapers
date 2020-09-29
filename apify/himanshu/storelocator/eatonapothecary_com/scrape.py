import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url = "http://eatonapothecary.com/locations/stores.php"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text ,"lxml")
    return_main_object = []
    contentcenter = soup.find("div",{"id": "contentcenter"}).find('table').find_all('tr')
    for tr in contentcenter:
        name=tr.find_all(attrs={'class':"locations"})
        mainadd=tr.find_all('h4')
        del mainadd[1]
        for j in range(len(mainadd)):
            ard=list(mainadd[j].stripped_strings)
            if ard!=[]:
                store = []
                store.append("http://eatonapothecary.com")
                store.append(name[j].text.strip())
                store.append(re.sub(' +', ' ',ard[0]).replace('\r\n',' ').replace("CVS @","").strip())
                store.append(name[j].text.strip())
                store.append("Massachusetts")
                store.append("<MISSING>")
                store.append("US")
                store.append("<MISSING>")
                store.append(ard[1].split('(')[0].strip())
                store.append("eatonapothecary")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("http://eatonapothecary.com/locations/stores.php")
                return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
