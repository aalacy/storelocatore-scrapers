import csv
from bs4 import BeautifulSoup
import re
import sgzip
import json
import time
from sgrequests import SgRequests
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'content-type':'application/x-www-form-urlencoded',
            'origin':'https://secondcup.com',
            'referer':'https://secondcup.com/find-a-cafe',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        }
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes= ["CA"])
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0  
    zip_code = search.next_zip()
    base_url = "https://secondcup.com"
    # payload = BeautifulSoup(session.get("https://secondcup.com/find-a-cafe",headers=headers).text,'lxml')
    # honeypot_time = payload.find("input",{"name":"honeypot_time"})['value']
    # print(honeypot_time)
    # form_build_id = payload.find("input",{"name":"form_build_id"})['value']
    # print(form_build_id)

    while zip_code:
        result_coords = []
        data = {
            "postal_code":str(zip_code),
            "honeypot_time":"XfwYJFceyauI_LWXAGtAZPzQNUHEkxkD_SXyuC2NPCA",
            "form_build_id":"form-qtm5jslnAllOaNjqPRPi4TDu_P4PXkpT0rfhVqU2CLQ",
            "form_id": "postal_code_form"
        }
        location_url = "https://secondcup.com/find-a-cafe"

        soup = BeautifulSoup(session.post(location_url, data=data, headers=headers).text, "lxml")
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
                    hours = "CLOSED"
            except:
                continue
            result_coords.append((0, 0))
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
            store.append("Cafe")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [x.replace("é","e") if type(x) == str else x for x in store] 
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)
scrape()



