import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
import time


def request_wrapper(url, method, headers, data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = requests.get(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = requests.post(url, headers=headers, data=data)
                else:
                    r = requests.post(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None


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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(include_canadian_fsas=True)
    MAX_RESULTS = 50
    coord = search.next_coord()
    while coord:
        result_coords = []
        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        x = coord[0]
        y = coord[1]
        # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        time.sleep(1)
        # print("https://locator-svc.subway.com/v3/GetLocations.ashx?q=%7B%22InputText%22%3A%22%22%2C%22GeoCode%22%3A%7B%22Latitude%22%3A" + str(x) + "%2C%22Longitude%22%3A" + str(y) + "%2C%22CountryCode%22%3A%22US%22%7D%2C%22DetectedLocation%22%3A%7B%22Latitude%22%3A0%2C%22Longitude%22%3A0%2C%22Accuracy%22%3A0%7D%2C%22Paging%22%3A%7B%22StartIndex%22%3A1%2C%22PageSize%22%3A50%7D%2C%22ConsumerParameters%22%3A%7B%22metric%22%3Afalse%2C%22culture%22%3A%22en-US%22%2C%22country%22%3A%22US%22%2C%22size%22%3A%22D%22%2C%22template%22%3A%22%22%2C%22rtl%22%3Afalse%2C%22clientId%22%3A%2217%22%2C%22key%22%3A%22SUBWAY_PROD%22%7D%2C%22Filters%22%3A%5B%5D%2C%22LocationType%22%3A1%2C%22behavior%22%3A%22%22%2C%22FavoriteStores%22%3Anull%2C%22RecentStores%22%3Anull%7D")
        r = request_wrapper("https://locator-svc.subway.com/v3/GetLocations.ashx?q=%7B%22InputText%22%3A%22%22%2C%22GeoCode%22%3A%7B%22Latitude%22%3A" + str(x) + "%2C%22Longitude%22%3A" + str(y) +
                            "%2C%22CountryCode%22%3A%22US%22%7D%2C%22DetectedLocation%22%3A%7B%22Latitude%22%3A0%2C%22Longitude%22%3A0%2C%22Accuracy%22%3A0%7D%2C%22Paging%22%3A%7B%22StartIndex%22%3A1%2C%22PageSize%22%3A50%7D%2C%22ConsumerParameters%22%3A%7B%22metric%22%3Afalse%2C%22culture%22%3A%22en-US%22%2C%22country%22%3A%22US%22%2C%22size%22%3A%22D%22%2C%22template%22%3A%22%22%2C%22rtl%22%3Afalse%2C%22clientId%22%3A%2217%22%2C%22key%22%3A%22SUBWAY_PROD%22%7D%2C%22Filters%22%3A%5B%5D%2C%22LocationType%22%3A1%2C%22behavior%22%3A%22%22%2C%22FavoriteStores%22%3Anull%2C%22RecentStores%22%3Anull%7D", "get", headers=headers)
        json_data = json.loads(r.text[1:-1])
        location_list = json_data["ResultData"]
        #print(len(location_list))
        html = json_data["ResultHtml"][2:]
        for store_data in location_list:
            lat = store_data["Geo"]["Latitude"]
            lng = store_data["Geo"]["Longitude"]
            address = store_data["Address"]
            result_coords.append((lat, lng))
            if address["CountryCode"] not in ["US", "CA"]:
                continue
            store = []
            store.append("https://www.subway.com")
            store.append("<MISSING>")
            street_address = address["Address1"]
            if address["Address2"]:
                street_address = street_address + " " + address["Address2"]
            if address["Address3"]:
                street_address = street_address + " " + address["Address3"]
            store.append(street_address)

            store.append(address["City"] if address["City"] else "<MISSING>")
            store.append(address["StateProvCode"]
                         if address["StateProvCode"] else "<MISSING>")
            if address["PostalCode"]:
                ca_zip_list = re.findall(
                    r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(address["PostalCode"]))
                us_zip_list = re.findall(re.compile(
                    r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address["PostalCode"]))
                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                elif us_zip_list:
                    zipp = us_zip_list[-1]
                else:
                    continue
                store.append(zipp if zipp else "<MISSING>")
            else:
                zipp = "<MISSING>"
                store.append(zipp)
            store.append(address["CountryCode"])

            store.append("<MISSING>")
            location_soup = BeautifulSoup(html[0], "lxml")
            if location_soup.find("div", {'class': "locationOpen"}) == False:
                continue
            hours = " ".join(list(location_soup.find(
                "div", {'class': 'hoursTable'}).stripped_strings))
            phone = location_soup.find(
                "div", {"class": "locatorPhone"}).text.strip()
            del html[0]
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours if hours else "<MISSING>")
            if hours.count("- - -") > 5:
                continue
            store.append("<MISSING>")
            if (str(store[2]) + str(store[3]) + str(store[4]) + str(store[5])) in addresses:
                continue
            addresses.append(
                str(store[2]) + str(store[3]) + str(store[4]) + str(store[5]))
            # print('data===' + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
        if len(location_list) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
