import csv
from bs4 import BeautifulSoup
import re
import sgzip
import json
import time
from sgrequests import SgRequests
import unicodedata
from requests.exceptions import RequestException


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    session = SgRequests()
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=["CA"])
    MAX_RESULTS = 5
    MAX_DISTANCE = 1
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

    base_url = "https://secondcup.com"

    while zip_code:
        result_coords = []
        #print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        #print('zip: ', zip_code)
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://secondcup.com',
            'referer': 'https://secondcup.com/find-a-cafe',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        }
        data = {
            "postal_code": str(zip_code),
            "honeypot_time": "pIzl-k4PaWoID2Ll9VBf7TcOMzV2H4x-hCFYLjld9D4",
            "form_build_id": "form-977IeJvoXbzPQq8czQxsGHhb6aFcBY1-y7C3HTufXk0",
            "form_id": "postal_code_form",
            "url": ""
        }
        location_url = "https://secondcup.com/find-a-cafe"
        try:
            r = session.post(location_url, data=data, headers=headers)
        except RequestException as ex:
            #print("--- RequestException-->", ex, 'resetting session')
            # reset the session and try again
            session = SgRequests()
            r = session.post(location_url, data=data, headers=headers)

        #print('search status: ', r.status_code)
        soup = BeautifulSoup(r.text, "lxml")
        # current_results_len = len(soup.find_all("a",{"class":"a-link"}))
        current_results_len = len(soup.select(
            "div.o-location-details__full-details a.a-link"))
        #print('current_results_len: ', current_results_len)
        for link in soup.select("div.o-location-details__full-details a.a-link"):
            if "google" in link['href']:
                continue

            # some locations are apparently closed permanently and return status 403. these have "closed" in the URL
            #   example: https://secondcup.com/location/closed-1405-upper-james-st
            if link['href'].startswith('/location/closed-'):
                continue

            page_url = base_url+link['href']
            #print(page_url)
            r1 = session.get(page_url)
            #print(f'{page_url} : {r1.status_code}')

            # some locations are apparently closed permanently and return status 403, but don't follow the same pattern mentioned above (having 'closed' in the URL)
            #   example: https://secondcup.com/location/shawnessy-town-centre
            if r1.status_code == 403:
                continue

            soup1 = BeautifulSoup(r1.text, "lxml")
            location_name = soup1.find("div", {"class": "l-location__title"}).text.strip()
            #print(location_name)
            #print()
            
            addr = list(soup1.find("div", {"class": "m-location-features__address"}).stripped_strings)
            #print(addr)
            if addr:
                street_address = addr[0]
                city = addr[1].split(",")[0]
                # if "Orlans" == city.strip():
                #     city = "Orleans"
                state = addr[1].split(",")[1]
                zipp = addr[1].split(",")[2].strip()
            else:
                street_address = "<MISSING>"
                city = "<MISSING>"
                state = "<MISSING>"
                zipp = "<MISSING>"
            phone = re.sub(r'\s+', " ", soup1.find("div", {"class": "m-location-features__phone"}).text.replace(
                "ext. 21079", "").split("/")[0].replace("TBD", "<MISSING>").replace("No Phone", "<MISSING>"))
            if phone == " ":
                phone = "<MISSING>"
            else:
                phone = phone

            hours = ""
            # check for closed location
            closed_message = soup1.select(
                "div.l-location__closed-cafe div.m-location-hours__title")
            if len(closed_message) == 1:
                hours = closed_message[0].get_text()
            else:
                hours = " ".join(list(soup1.find("ul", {"class": "m-location-hours__list"}).stripped_strings))
            #print('hours: ', hours)

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
            if (str(store[1])+" "+str(store[2])+" "+str(store[-1])) in addresses:
                continue
            addresses.append(str(store[1])+" " +
                             str(store[2])+" "+str(store[-1]))

            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize(
                        'NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [str(x).replace("\xe2", "-").replace("\xe7", '')
                     if x else "<MISSING>" for x in store]
            store = [str(x).encode('ascii', 'ignore').decode(
                'ascii').strip() if x else "<MISSING>" for x in store]

            yield store

            #print("data == " + str(store))
            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        if current_results_len < MAX_RESULTS:
            #print("max distance update")
            search.max_distance_update(MAX_DISTANCE)

        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
