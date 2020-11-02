import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('berluti_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    base_url = "https://www.berluti.com"
    # r = session.get("http://store.berluti.com/search?country=us", headers=headers)
    # soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     logger.info(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"

    r_us = session.get("http://store.berluti.com/search?country=us", headers=headers)
    soup_us = BeautifulSoup(r_us.text, "lxml")

    for script_us in soup_us.find_all('div', {'class': 'container'})[1:]:

        page_url = "https://store.berluti.com"+script_us.find("div",{"class":"col-xs-12"}).find("a")["href"]
        r_page = session.get(page_url, headers=headers)
        soup_page = BeautifulSoup(r_page.text, "html5lib")
        jd = json.loads(soup_page.find("script",{"type":"application/ld+json"}).text)
        location_name = jd['name']
        street_address = jd['address']['streetAddress'].replace("754 5th Avenue","754 5th Avenue 2nd floor").replace("3333 Bristol Street","3333 Bristol Street Level 2")
        city = jd['address']['addressLocality']
        temp_state_zip = jd['address']['postalCode'].split(" ")
        if len(temp_state_zip)==2:
            state = temp_state_zip[0]
            zipp = temp_state_zip[1]
        else:
            zipp = temp_state_zip[0]
            ct =["San Francisco","Beverly Hills"]
            if city in ct:
                state = "CA"
            else:
                state = "WA"
            
        phone = jd['telephone'].replace("+1","").strip()
        try:
            hours_of_operation = " ".join(list(soup_page.find("div", {"class": "components-outlet-item-hours-retail"}).stripped_strings)).replace("Opening hours", "").strip()
        except:
            hours_of_operation = "<MISSING>"

        latitude = soup_page.find("meta", {"itemprop": "latitude"})["content"]
        longitude = soup_page.find("meta", {"itemprop": "longitude"})["content"]
        

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
        

    r_ca = session.get("http://store.berluti.com/search?country=ca", headers=headers)
    soup_ca = BeautifulSoup(r_ca.text, "lxml")

    for script_ca in soup_ca.find_all('div', {'class': 'container'})[1:]:
        page_url = "https://store.berluti.com"+script_ca.find("div",{"class":"col-xs-12"}).find("a")["href"]
        r_page = session.get(page_url, headers=headers)
        soup_page = BeautifulSoup(r_page.text, "html5lib")
        jd = json.loads(soup_page.find("script",{"type":"application/ld+json"}).text)
        location_name = jd['name']
        street_address = jd['address']['streetAddress']
        city = jd['address']['addressLocality']
        zipp = jd['address']['postalCode']
        if city == "Toronto":
            state = "ON" 
        if city == "Vancouver":
            state = "BC"
    
        phone = jd['telephone'].replace("+1","").strip()
        try:
            hours_of_operation = " ".join(list(soup_page.find("div", {"class": "components-outlet-item-hours-retail"}).stripped_strings)).replace("Opening hours", "").strip()
        except:
            hours_of_operation = "<MISSING>"

        latitude = soup_page.find("meta", {"itemprop": "latitude"})["content"]
        longitude = soup_page.find("meta", {"itemprop": "longitude"})["content"]
        

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("CA")
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
