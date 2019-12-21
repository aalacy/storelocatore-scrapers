import csv
import requests
from bs4 import BeautifulSoup
import re
import json


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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    return_main_object = []
    base_url = "https://wellnow.com"
    r = requests.get("https://wellnow.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for script in soup.find_all("script"):
        if "var activeLocations =" in script.text:
            location_list = json.loads(script.text.split(
                "var activeLocations =")[1].split("];")[0] + "]")
            for store_data in location_list:
                if store_data["open_status"] != "open":
                    continue
                page_url = store_data["link"]
                location_request = requests.get(page_url, headers=headers)
                location_soup = BeautifulSoup(location_request.text, "lxml")
                try:
                    address = location_soup.find(
                        "address").find("a").text.strip()
                    state_split = re.findall("([A-Z]{2})", address)
                    if state_split:
                        state = state_split[-1]
                    else:
                        state = "<MISSING>"
                    store_zip_split = re.findall(
                        r"\b[0-9]{5}(?:-[0-9]{4})?\b", address)
                    if store_zip_split:
                        store_zip = store_zip_split[-1]
                    else:
                        store_zip = "<MISSING>"
                    city = address.split(",")[1]
                    street_address = address.split(",")[0]

                    phone = location_soup.find(
                        "a", {'href': re.compile("tel:")}).text.strip()
                    try:
                        hours = location_soup.find("address").find("h5").text.strip().replace(
                            'Accepting walk-in patients and online check-ins ', "")
                    except:
                        hours = location_soup.find("address").find("p").text.strip().replace(
                            'Accepting walk-in patients and online check-ins', "")
                        # print(page_url)
                        # print("---------------------")
                    name = location_soup.find(
                        "p", {"class": "h2"}).text.strip()
                except:
                    pass
                    # print(page_url)
                    # print("*******************")

                store = []
                store.append("https://wellnow.com")
                store.append(name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(store_zip)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(store_data["lat"])
                store.append(store_data["lng"])
                store.append(hours if hours else "<MISSING>")
                store.append(page_url)
                store = [x.replace("–", "-") if type(x) ==
                         str else x for x in store]
                store = [x.encode('ascii', 'ignore').decode(
                    'ascii').strip() if type(x) == str else x for x in store]
                # print("data ===" + str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~")
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
