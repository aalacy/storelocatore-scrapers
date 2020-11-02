import csv
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('multi-specialty_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "http://www.multi-specialty.com"
    # addresses = []

    r = session.get("http://www.multi-specialty.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for i in soup.find_all("area"):
        page_url = base_url+i['href']
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        for j in soup1.find_all("div",{"class":"map_info"}):
            page_url = page_url
            if "baltimore-city" in page_url:
                hours_of_operation = "Saturday : From 9AM-12PM for New Patients"
            else:
                hours_of_operation = "<MISSING>"
            location_name = j.find("h6").text.strip()
            data = " ".join(list(j.find_all("p")[1].stripped_strings))
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), data)
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}\b"), data)
            state_list = re.findall(r', ([A-Z]{2})', data)
            state = state_list[-1]
            phone = phone_list[0]
            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"

            if state_list:
                state = state_list[-1]
            info = (list(j.find_all("p")[1].stripped_strings))
            if len(info)> 4 and "Fax:" in info[4] :
                del info[4:]
            if "-" in info[-1] and len(info)>1:
                del info[-1]
            if "-" in info[-1] and len(info)>1:
                del info[-1]
            if   len(info)>1 and "Fax(Suite 200)" in info[1]:
                del info[1]
            if len(info)>2 and "-" in info[1]:
                del info[1:]
            if len(info)>6 and "-" in info[2]:
                del info[2:]
            if len(info)>1 and "(Sat. Hrs. 9-12)" in info[0]:
                del info[0]
    
            if len(info) == 1:
                street_address = " ".join(info[-1].split(",")[0].split(" ")[:-1])
                city = info[-1].split(",")[0].split(" ")[-1]
            else:
                street_address = " ".join(info[:-1])
                city = info[-1].split(",")[0]

            
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append("<MISSING>") 
            store.append(phone)
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours_of_operation)
            store.append(page_url)
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


    r1 = session.get("http://www.multi-specialty.com/locations/", headers=headers)
    soup1 = BeautifulSoup(r1.text, "lxml")
    location_name = soup1.find_all("div",{"class":"title"})[1].text
    raw_address = list(soup1.find("div",{"class":"addr"}).stripped_strings)
    street_address = " ".join(raw_address[:2])
    city = raw_address[2].split(",")[0]
    state = raw_address[2].split(",")[1].split(" ")[1]
    zipp = raw_address[2].split(",")[1].split(" ")[2]
    phone = raw_address[3]

    store = []
    store.append(base_url)
    store.append(location_name)
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
    store.append("<MISSING>")
    store.append("http://www.multi-specialty.com/locations/")
    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
    # logger.info("data = " + str(store))
    # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    yield store



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
