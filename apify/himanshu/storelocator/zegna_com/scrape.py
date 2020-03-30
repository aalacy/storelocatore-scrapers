import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.zegna.us"
    r = session.get(
        base_url + "/us-en/store-locator/view-all-stores.html", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for city in soup.find_all("li", {"class": "baa-city"}):
        link = city.find("a")["href"]
        while True:

            city_request = session.get(base_url + link, headers=headers)
            city_soup = BeautifulSoup(city_request.text, "lxml")
            # print(base_url + link)
            if city_soup.find("div", {"class": "baa-list-left"}) == None:
                pass
            else:
                location_list = json.loads(city_soup.find(
                    "div", {"class": "baa-list-left"})["data-stores"])
                for i in range(len(location_list)):
                    store_data = location_list[i]
                    store = []
                    store.append("https://www.zegna.us")
                    store.append(store_data['name'])
                    store.append(store_data["address"])
                    store.append(store_data['city'])
                    store.append(
                        store_data['state'] if store_data['state'] != "" else "<MISSING>")
                    store.append(
                        store_data["postalCode"] if store_data["postalCode"] != "" else "<MISSING>")
                    store.append(store_data["countryCode"])
                    store.append(store_data['storeId'])
                    store.append(store_data['phoneNumber'])
                    store.append("<MISSING>")
                    store.append(store_data["latitude"])
                    store.append(store_data["longitude"])

                    store_hours = store_data["openUntil"]
                    hours = ""
                    hours_object = {"1": "Monday", "2": "Tuesday", "3": "Wednesday",
                                    "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday"}
                    for key in store_hours:
                        hours = hours + hours_object[key] + " open time " + \
                            store_hours[key]["open"] + " close time " + \
                            store_hours[key]["close"] + " "
                    store.append(hours if hours != "" else "<MISSING>")
                    page_url = base_url + store_data["url"]
                    store.append(page_url)
                    # print(store)
                    return_main_object.append(store)
                break
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
