import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('churchs_com')





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
    addresses = []
    #base_url = "https://mbfinancial.com"
    r = session.get("https://locations.churchs.com", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for states in soup.find_all("a", {'class': "Directory-listLink"}):
        state_request = session.get(
            "https://locations.churchs.com/" + states["href"])
        state_soup = BeautifulSoup(state_request.text, "lxml")
        for city in state_soup.find_all("a", {'class': "Directory-listLink"}):
            #logger.info("https://locations.churchs.com/" + city["href"].replace("../",""))
            city_request = session.get(
                "https://locations.churchs.com/" + city["href"].replace("../", ""))
            city_soup = BeautifulSoup(city_request.text, "lxml")
            for location in city_soup.find_all("a", {'class': "Teaser-titleLink"}):

                # logger.info("https://locations.churchs.com/" +
                #       location["href"].replace("../", ""))
                page_url = "https://locations.churchs.com/" + \
                    location["href"].replace("../", "")
                location_name = location.find(
                    "span", class_="LocationName-brand").text.strip()
                # logger.info(location_name)
                location_request = session.get(
                    "https://locations.churchs.com/" + location["href"].replace("../", ""))
                location_soup = BeautifulSoup(location_request.text, "lxml")
                try:
                    street_address = " ".join(list(location_soup.find(
                        "span", {'class': "c-address-street-1"}).stripped_strings))
                    if location_soup.find("span", {'class': "c-address-street-2"}) != None:
                        street_address = street_address + " " + \
                            " ".join(list(location_soup.find(
                                "span", {'class': "c-address-street-2"}).stripped_strings))

                    city = location_soup.find(
                        "span", {'class': "c-address-city"}).text
                    state = location_soup.find(
                        "abbr", {'class': "c-address-state"}).text

                    store_zip = location_soup.find(
                        "span", {'class': "c-address-postal-code"}).text

                    if location_soup.find("div", {'itemprop': "telephone"}) == None:
                        phone = "<MISSING>"
                    else:
                        phone = location_soup.find(
                            "div", {'itemprop': "telephone"}).text
                    try:
                        hours = " ".join(list(location_soup.find(
                            "table", {'class': "c-hours-details"}).stripped_strings))
                        # logger.info(hours)
                        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    except:
                        hours = "<MISSING>"
                        # logger.info("url ==" + url)

                    lat = location_soup.find(
                        "meta", {'itemprop': "latitude"})["content"]
                    lng = location_soup.find(
                        "meta", {'itemprop': "longitude"})["content"]
                    # logger.info(state, city)
                except:

                    street_address = page_url.split("/")[-1]
                    city = page_url.split("/")[-2]
                    state = page_url.split("/")[-3]
                    store_zip = "<MISSING>"
                    phone = "(254) 616-9271"
                    hours = "<MISSING>"
                    lat = "<MISSING>"
                    lng = "<MISSING>"

                    # logger.info(page_url)
                store = []
                store.append("https://churchs.com")
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(store_zip)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone if phone != "" else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(page_url)
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                # logger.info("data == " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
