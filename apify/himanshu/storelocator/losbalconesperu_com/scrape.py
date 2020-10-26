import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata



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
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "http://losbalconesperu.com"
    r = session.get("http://losbalconesperu.com", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for location in soup.find_all("div", {'class': 'mc1inlineContent'}):
        try:
            locator_domain = base_url
            hours = location.find("p", class_="font_8").find(
                "span", style="font-family:avenir-lt-w01_35-light1475496,sans-serif;")
            hours_of_operation = " ".join(list(hours.stripped_strings)).replace("|","").replace("â€“","")
            # 
            address = list(location.find("a").stripped_strings)
            # print(address)
            if len(address) > 1:
                street_address = address[0].strip()
                city = address[-1].split(',')[0].strip()
                state = address[-1].split(',')[1].split()[0].strip()
                zipp = address[-1].split(',')[1].split()[-1].strip()
            else:
                address = list(location.find(
                    "div", {"id": "comp-k1b7q28u"}).stripped_strings)
                street_address = address[0].strip()
                city = address[-1].split(',')[0].strip()
                state = address[-1].split(',')[1].split()[0].strip()
                zipp = address[-1].split(',')[1].split()[-1].strip()
            # print(city, state, zipp)
            location_name = city
            phone = location.find_all("h2", class_="font_2")[-1].text.strip()
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            store_number = "<MISSING>"
            page_url = base_url
            location_type = "<MISSING>"
            country_code = "US"
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            # print("data = " + str(store))
            # print(
            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store

        except Exception as e:
            pass
            # print(e)

        # geo_location = location.find("a")["href"]
        # location_request = session.get(
        #     location.find_all("a")[1]["href"], headers=headers)
        # location_soup = BeautifulSoup(location_request.text, "lxml")
        # location_details = list(location_soup.find(
        #     "div", {'class': "contact-location"}).stripped_strings)
        # store = []
        # store.append("http://losbalconesperu.com")
        # store.append(location.find("img")["alt"].replace("logo", ""))
        # store.append(location_details[1])
        # store.append(location_details[2].split(",")[0])
        # store.append(location_details[2].split(",")[1])
        # store.append(location_details[3])
        # store.append("US")
        # store.append("<MISSING>")
        # store.append(location_soup.find("a", {"href": re.compile("tel:")})[
        #              "href"].replace("tel:", ""))
        # store.append("<MISSING>")
        # store.append(geo_location.split("/@")[1].split(",")[0])
        # store.append(geo_location.split("/@")[1].split(",")[1])
        # store.append(" ".join(location_soup.find(
        #     "div", {'class': "hours"}).stripped_strings))
        # store.append(location.find_all("a")[1]["href"])
        # for i in range(len(store)):
        #     if type(store[i]) == str:
        #         store[i] = ''.join((c for c in unicodedata.normalize(
        #             'NFD', store[i]) if unicodedata.category(c) != 'Mn'))
        # store = [x.replace("–", "-") if type(x) == str else x for x in store]
        # store = [x.encode('ascii', 'ignore').decode(
        #     'ascii').strip() if type(x) == str else x for x in store]
        # # print("data== "+str(store))
        # # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
