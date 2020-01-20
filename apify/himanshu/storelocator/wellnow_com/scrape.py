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
    r1 = requests.get("https://wellnow.com/wp-json/facilities/v2/locations", headers=headers).json()

    for data in r1.keys():
        for data1 in r1[data]:
            name1 = data1["title"]
            state = data1['region']
            lat = data1['lat']
            lng = data1['lng']
            phone =data1['phone']
            state_list = re.findall(r' ([A-Z]{2})', str(data1['address'].split(",")[-1]))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(data1['address'].split(",")[-1]))

            link = data1['link']

            r2 = requests.get(link, headers=headers)
            soup = BeautifulSoup(r2.text,"lxml")
            hours = (" ".join(list(soup.find("div",{"class":"col-md-6 py-5 white-text location-hours"}).stripped_strings)).split("We are open")[0].replace("Hours","").strip())
            
            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"
            if state_list:
                state = state_list[-1]
                country_code = "US"

            city = data1['address'].split(",")[1]
            street_address = data1['address'].split(",")[0]
            # print(name1)
            # print(street_address)
            store = []
            store.append("https://wellnow.com")
            store.append(name1)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours if hours else "<MISSING>")
            store.append(link)
            # store = [x.replace("–", "-") if type(x) ==
            #          str else x for x in store]
            # store = [x.encode('ascii', 'ignore').decode(
            #     'ascii').strip() if type(x) == str else x for x in store]
            # print("data ===" + str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
