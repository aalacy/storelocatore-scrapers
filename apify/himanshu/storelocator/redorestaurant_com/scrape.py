import csv
from bs4 import BeautifulSoup as bs
import re
from sgrequests import SgRequests
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",'page_url'])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = 'https://www.redorestaurant.com/'
    

    soup = bs(session.get(base_url).text, "lxml")

    for url in soup.find("ul",{"class":"sub-menu"}).find_all("a"):
        page_url = url['href']
        if page_url == "https://www.redorestaurant.com/o-lounge/":
            continue
        location_soup = bs(session.get(page_url).text, "lxml")


        row = location_soup.find("div",{"class":"et_pb_row et_pb_row_2"}).find_all("div",{"class":re.compile("et_pb_text_align_left et_pb_bg_layout_light")})
        
        addr = list(row[0].find("div",{"class":"et_pb_text_inner"}).stripped_strings)
        if len(addr) == 14:
            del addr[3]
        
        street_address = addr[3]
        city = addr[4].split(",")[0]
        state = addr[4].split(",")[-1].split()[0]
        zipp = addr[4].split(",")[-1].split()[-1]

        if len(addr) >= 6:
            phone = addr[6]
        else:
            phone = "<MISSING>"
    

        hours = " ".join(list(row[1].stripped_strings))
        
        store = []
        store.append(base_url)
        store.append("<MISSING>")
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours)
        store.append(page_url)     
    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        
        yield store
    

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
