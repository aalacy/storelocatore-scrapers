import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('patioenc_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
   
    base_url= "https://www.patioenclosures.com"

    
    headers = {           
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    
    }
    r = session.get("https://www.patioenclosures.com/sitemap.aspx", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("li", {"class":"AspNet-TreeView-Root AspNet-TreeView-Leaf"})[-1].find("ul").find_all("li",{"class":"AspNet-TreeView-Leaf"})[3].find("ul")
    for i in data.find_all("li"):
        links = i.find("a")['href']
        if "directions" in links or "photos" in links or "ideas" in links:
            continue
        page_url = base_url+links
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        location_name = soup1.find("h2").text

        if "canada" in page_url:
            country_code = "CA"
        else:
            country_code = "US"
        details = soup1.find("div",{"class":"branch-intro-copy"})
        if details:
            info = list(soup1.find("div",{"class":"branch-address"}).stripped_strings)
            location_name = soup1.find("h2").text
            if "Location coming soon!" in info:
                continue
        
            if "By Appointment Only" in info or "By Appointment Only!" in info:
                street_address = "<MISSING>"
                city = "<MISSING>"
                state = "<MISSING>"
                zipp = "<MISSING>"
            else:
                street_address = "".join(info[:-1])
                city = info[-1].split(",")[0]
                state = info[-1].split(",")[1].split(" ")[1]
                zipp = info[-1].split(",")[1].split(" ")[2]
            phone = details.find_all("li")[1].text.replace("Local:","").replace("Phone:","").strip()
            hour = " ".join(list(soup1.find("ul",{"class":"two-column-list"}).stripped_strings))
            if "Monday" in hour:
                hours_of_operation = hour
            else:
                hours_of_operation = "<MISSING>"


        else:
            location_name = soup1.find("h1").text.capitalize()
            row_adr = soup1.find("div",{"class":"branch-details"})
            street_address = "".join(list(row_adr.find_all("p")[0].stripped_strings)[:-1])
            city = list(row_adr.find_all("p")[0].stripped_strings)[-1].split(",")[0]
            state = list(row_adr.find_all("p")[0].stripped_strings)[-1].split(",")[1].split(" ")[1]
            zipp = " ".join(list(row_adr.find_all("p")[0].stripped_strings)[-1].split(",")[1].split(" ")[2:])
            
            if "colorado" in page_url or "tampa" in page_url:
                phone = list(row_adr.find_all("p")[2].stripped_strings)[1].replace("Local:","813-620-0931")
                hours_of_operation = " ".join(list(row_adr.find_all("p")[1].stripped_strings))
            else:
                phone = list(row_adr.find_all("p")[3].stripped_strings)[1]
                hours_of_operation = " ".join(list(row_adr.find_all("p")[2].stripped_strings))

                
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append("<MISSING>")
        store.append(phone )
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours_of_operation)
        store.append(page_url)
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        # logger.info("data =="+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        yield store

            
       
        
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
