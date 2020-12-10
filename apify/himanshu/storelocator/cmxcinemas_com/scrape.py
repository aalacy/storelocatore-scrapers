import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import html5lib
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cmxcinemas_com')



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
    return_main_object = []
    addresses = []
    

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    
        # logger.info("zip_code === "+zip_code)
    locator_domain = "https://www.cmxcinemas.com"
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    location_url = "https://www.cmxcinemas.com/"
    
  
    r = requests.get(location_url,headers=headers)
    soup = BeautifulSoup(r.text, "html5lib")
    
    for data in soup.find_all("aside",{"class":"cinemas-dropdown cinemas-list hidden"}):
        for data1 in data.find_all("li",{"class":"cinema-list-item"}):
            page_url = ''
            location_name= list(data1.stripped_strings)[0]
            full=list(data1.stripped_strings)[-1].replace(", USA","").replace(", USA.","").split(",")
            city='<MISSING>'
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full[-1].replace(".",'')))
            state_list = re.findall(r' ([A-Z]{2})', str(full[-1]))
            street_address = full[0].replace("New York",'')
            city=full[1]
            
            if us_zip_list:
                zipp = us_zip_list[-1]
            else:
                city=full[-1]
            if state_list:
                state = state_list[-1]
            page_url="https://www.cmxcinemas.com"+data1.find("a")['href']
            r2 = requests.get("https://www.cmxcinemas.com"+data1.find("a")['href'])
            soup2 = BeautifulSoup(r2.text, "html5lib")
            try:
                jdata=json.loads(soup2.find("script",{"type":"application/ld+json"}).text)
                phone = jdata['telephone']
                latitude = jdata['geo']['latitude']
                longitude = jdata['geo']['longitude']
            except:
                r3 = requests.get("https://www.cmxcinemas.com/theaters/16/cmx-cinbistro-wheeling")
                soup3 = BeautifulSoup(r3.text, "html5lib")
                latitude = soup3.find("div",{"class":"wheeling-contact"}).find("a")['href'].split("ll=")[1].split(",")[0]
                longitude=soup3.find("div",{"class":"wheeling-contact"}).find("a")['href'].split("ll=")[1].split(",")[1].split("&z")[0]
                phone=list(soup3.find("div",{"class":"wheeling-contact"}).stripped_strings)[-1]

            store_number="<MISSING>"
            location_type="<MISSING>"
            hours_of_operation="<MISSING>"
            
            store = ["https://www.cmxcinemas.com", location_name, street_address.strip(), city.replace("NY 10065",'New York'), state, zipp, country_code,
                        store_number, str(phone).replace("None","<MISSING>").replace(":",''), location_type, latitude, longitude, hours_of_operation, page_url]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
        
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
