import csv
from bs4 import BeautifulSoup
import re
import sgzip
from sgzip import DynamicZipSearch, SearchableCountries
import json
from sgrequests import SgRequests
from sgselenium import SgChrome

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    addresses = []
    store_data = []

    search = sgzip.DynamicZipSearch(country_codes=[SearchableCountries.CANADA])

    search.initialize()
    zip_code = search.next()

    base_url = "https://secondcup.com"
    location_url = "https://secondcup.com/find-a-cafe"

    driver = SgChrome().chrome()

    driver.get(location_url)
    base = BeautifulSoup(driver.page_source,"lxml")
    
    # payload = BeautifulSoup(session.get(location_url,headers=HEADERS).text,'lxml')
    honeypot_time = base.find("input",{"name":"honeypot_time"})['value']
    # print(honeypot_time)
    form_build_id = base.find("input",{"name":"form_build_id"})['value']
    # print(form_build_id)

    while zip_code:
        pay_data = {
            "postal_code":str(zip_code),
            "honeypot_time":honeypot_time,
            "form_build_id":form_build_id,
            "form_id": "postal_code_form"
        }

        # result_coords = []

        soup = BeautifulSoup(session.post(location_url, data=pay_data, headers=HEADERS).text, "lxml")
        current_results_len = len(soup.find_all("a",{"class":"a-link"}))
        for link in soup.find_all("a",{"class":"a-link"}):
            if "google" in link['href']:
                continue
            page_url = base_url+link['href']
            if "closed" in link['href']:
                continue
            soup1 = BeautifulSoup(session.get(page_url).text, "lxml")
            try:
                addr = list(soup1.find("div",{"class":"m-location-features__address"}).stripped_strings)
                location_name = soup1.find("div",{"class":"l-location__title"}).text.strip()
                street_address = addr[0]
                city = addr[1].split(",")[0]
                state = addr[1].split(",")[1]
                zipp = addr[1].split(",")[2].strip()
                phone = re.sub(r'\s+'," ",soup1.find("div",{"class":"m-location-features__phone"}).text.replace("ext. 21079","").split("/")[0].replace("TBD","<MISSING>").replace("No Phone","<MISSING>"))
                if phone == " ":
                    phone = "<MISSING>"
                else:
                    phone = phone
                try:
                    hours = " ".join(list(soup1.find("ul",{"class":"m-location-hours__list"}).stripped_strings))
                except:
                    hours = "TEMPORARILY CLOSED"
            except:
                continue
            # result_coords.append(zipp)
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("CA")
            store.append("<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [x.replace("é","e") if type(x) == str else x for x in store] 
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            store_data.append(store)
        # if current_results_len > 0:
        #     search.update_with(result_coords)
        zip_code = search.next()

    driver.close()
    return store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
