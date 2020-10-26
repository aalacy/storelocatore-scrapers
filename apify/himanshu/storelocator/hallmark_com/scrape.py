import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import http.client
import sgzip
import json
import pprint



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # conn = http.client.HTTPSConnection("maps.hallmark.com")
    base_url = 'https://www.hallmark.com'
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
        # 'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        # 'cache-control': "no-cache",
        # 'postman-token': "13913a57-e466-50b2-ee2b-c6d50ead7e1f"
    }
    search = sgzip.ClosestNSearch()
    search.initialize(include_canadian_fsas=True)
    addresses = []
    MAX_RESULTS = 80
    MAX_DISTANCE = 30
    current_results_len = 0
    coords = search.next_zip()
    while coords:
        result_coords = []
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = ""
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        hours_of_operation = ""
        page_url = ''
        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        try:
            r = session.get("https://maps.hallmark.com/api/getAsyncLocations?template=searchResultsMap&level=search&radius=" + str(MAX_DISTANCE) + "&search=" + str(search.current_zip),
                             headers).json()
        except:
            continue

        if r['markers'] != None:
            current_results_len = len(r['markers'])
            for x in r['markers']:
                soup = BeautifulSoup(x['info'], "lxml")
                locator_domain = base_url
                div_data = soup.find(
                    'div', {'class': 'rio-popupItem-addr'}).find_all('div')
                street_address = div_data[1].text.strip()
                city = div_data[2].text.strip().split(',')[0]
                state = div_data[2].text.strip().split(
                    ',')[1].strip().split(' ')[0].strip()
                # print(div_data[1])
                # zip  =  div_data[2].text.strip().split(',')[1].strip().split(' ')[1].strip()
                # print(div_data[2].text)
                ca_zip_list = re.findall(
                    r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(div_data[2].text))
                us_zip_list = re.findall(re.compile(
                    r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(div_data[2].text))
                state_list = re.findall(r' ([A-Z]{2})', str(div_data[2].text))

                # country_code = 'US'
                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                    country_code = "CA"
                if us_zip_list:
                    zipp = us_zip_list[-1]
                    country_code = "US"

                if state_list:
                    state = state_list[-1]

                store_number = x['locationId']
                location_type = '<MISSING>'
                latitude = x['lat']
                longitude = x['lng']
                kk = soup.find('a', {'class': 'gaq-link'})['href']
                r1 = session.get(
                    soup.find('a', {'class': 'gaq-link'})['href'])
                soup1 = BeautifulSoup(r1.text, "lxml")
                location_name = soup1.find(
                    'div', {'class': 'rio-locationName is-bold gutter-bottom-tiny'}).text.strip()
                # print("==============",)
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(
                    soup1.find("div", {"class": "rio-phone"}).find("a").text))
                if phone_list:
                    phone = phone_list[-1]
                else:
                    phone = ''
                # print(phone)

                hours_of_operation = ''
                if soup1.find('div', {'class': 'hours'}) != None:
                    sentence = soup1.find(
                        'div', {'class': 'hours'}).text.strip()
                    pattern = re.compile(r'\s+')
                    hours_of_operation = re.sub(pattern, ' ', sentence)

                if street_address in addresses:
                    continue
                addresses.append(street_address)
                page_url = kk

                store = []
                result_coords.append((latitude, longitude))
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zipp if zipp else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')
                store.append(
                    hours_of_operation if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else '<MISSING>')
                # print("data=====", str(store))
                yield store

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        coords = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
