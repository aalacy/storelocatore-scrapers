import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('haircuttery_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # zips = sgzip.coords_for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    # it will used in store data.
    locator_domain = "https://www.haircuttery.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "<MISSING>"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"
    # skip = 0
    # while True:
    #     logger.info(skip)
    r = session.get("https://locations.haircuttery.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for li in soup.find_all("li", class_="c-directory-list-content-item"):
        if "/" not in li.a["href"]:
            link1 = "https://locations.haircuttery.com/" + li.a["href"]
            r_loc = session.get(link1, headers=headers)
            soup_loc = BeautifulSoup(r_loc.text, "lxml")
            for li in soup_loc.find_all("li", class_="c-directory-list-content-item"):
                link2 = li.a["href"].split("/")
                if len(link2) < 3:
                    link2 = "https://locations.haircuttery.com/" + \
                        li.a["href"]
                    # logger.info(link2)
                    r_loc1 = session.get(link2, headers=headers)
                    soup_loc1 = BeautifulSoup(r_loc1.text, "lxml")
                    if soup_loc1.find_all(
                            "h5", class_="c-location-grid-item-title") != []:
                        for h5 in soup_loc1.find_all("h5", class_="c-location-grid-item-title"):
                            page_url = "https://locations.haircuttery.com" + \
                                h5.a["href"].replace("..", "").strip()
                            # logger.info(page_url)
                            details_r = session.get(page_url, headers=headers)
                            details_soup = BeautifulSoup(
                                details_r.text, "lxml")
                            try:
                                location_name = " ".join(list(details_soup.find(
                                    "h1", {"itemprop": "name"}).stripped_strings))
                            except:
                                location_name = "<MISSING>"
                            try:
                                latitude = details_soup.find(
                                    "meta", {"itemprop": "latitude"})["content"]
                                longitude = details_soup.find(
                                    "meta", {"itemprop": "longitude"})["content"]
                            except:
                                latitude = "<MISSING>"
                                longitude = "<MISSING>"
                            try:
                                street_address = details_soup.find(
                                    "span", {"itemprop": "streetAddress"}).text.strip()
                            except:
                                street_address = "<MISSING>"
                            try:
                                city = details_soup.find(
                                    "span", {"itemprop": "addressLocality"}).text.strip()
                            except:
                                city = "<MISSING>"
                            try:
                                state = details_soup.find(
                                    "abbr", {"itemprop": "addressRegion"}).text.strip()
                            except:
                                state = "<MISSING>"
                            try:
                                zipp = details_soup.find(
                                    "span", {"itemprop": "postalCode"}).text.strip()
                            except:
                                zipp = "<MISSING>"
                            try:
                                country_code = details_soup.find(
                                    "span", {"itemprop": "addressCountry"}).text.strip()
                            except:
                                country_code = "US"
                            try:
                                phone = list(details_soup.find(
                                    "div", class_="location-info-phone").stripped_strings)[0]
                            except:
                                phone = "<MISSING>"
                            try:
                                hours_of_operation = " ".join(list(details_soup.find(
                                    "table", class_="c-location-hours-details").stripped_strings)).replace("Day of the Week", "").replace("Hours", "").strip()
                            except:
                                hours_of_operation = "<MISSING>"
                            # logger.info(phone)
                            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                            store = ["<MISSING>" if x ==
                                     "" else x for x in store]
                            store = [str(x).encode('ascii', 'ignore').decode(
                                'ascii').strip() if x else "<MISSING>" for x in store]
                            # logger.info("data = " + str(store))
                            # logger.info(
                            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                            yield store

                else:
                    # pass
                    page_url = "https://locations.haircuttery.com/" + \
                        li.a["href"]
                    # logger.info(link2)
                    r_loc2 = session.get(page_url, headers=headers)
                    soup_loc2 = BeautifulSoup(r_loc2.text, "lxml")

                    try:
                        location_name = " ".join(list(soup_loc2.find(
                            "h1", {"itemprop": "name"}).stripped_strings))
                    except:
                        location_name = "<MISSING>"
                    try:
                        latitude = soup_loc2.find(
                            "meta", {"itemprop": "latitude"})["content"]
                        longitude = soup_loc2.find(
                            "meta", {"itemprop": "longitude"})["content"]
                    except:
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                    try:
                        street_address = soup_loc2.find(
                            "span", {"itemprop": "streetAddress"}).text.strip()
                    except:
                        street_address = "<MISSING>"
                    try:
                        city = soup_loc2.find(
                            "span", {"itemprop": "addressLocality"}).text.strip()
                    except:
                        city = "<MISSING>"
                    try:
                        state = soup_loc2.find(
                            "abbr", {"itemprop": "addressRegion"}).text.strip()
                    except:
                        state = "<MISSING>"
                    try:
                        zipp = soup_loc2.find(
                            "span", {"itemprop": "postalCode"}).text.strip()
                    except:
                        zipp = "<MISSING>"
                    try:
                        country_code = soup_loc2.find(
                            "span", {"itemprop": "addressCountry"}).text.strip()
                    except:
                        country_code = "US"
                    try:
                        phone = list(soup_loc2.find(
                            "div", class_="location-info-phone").stripped_strings)[0]
                    except:
                        phone = "<MISSING>"
                    try:
                        hours_of_operation = " ".join(list(soup_loc2.find(
                            "table", class_="c-location-hours-details").stripped_strings)).replace("Day of the Week", "").replace("Hours", "").strip()
                    except:
                        hours_of_operation = "<MISSING>"
                    # logger.info(phone)
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                    store = ["<MISSING>" if x ==
                             "" else x for x in store]
                    store = [str(x).encode('ascii', 'ignore').decode(
                        'ascii').strip() if x else "<MISSING>" for x in store]
                    # logger.info("data = " + str(store))
                    # logger.info(
                    #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store
                    # logger.info(link2)
        else:
            pass
            page_url = "https://locations.haircuttery.com/" + li.a["href"]

            r_loc3 = session.get(page_url, headers=headers)
            soup_loc3 = BeautifulSoup(r_loc3.text, "lxml")

            try:
                location_name = " ".join(list(soup_loc3.find(
                    "h1", {"itemprop": "name"}).stripped_strings))
            except:
                location_name = "<MISSING>"
            try:
                latitude = soup_loc3.find(
                    "meta", {"itemprop": "latitude"})["content"]
                longitude = soup_loc3.find(
                    "meta", {"itemprop": "longitude"})["content"]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            try:
                street_address = soup_loc3.find(
                    "span", {"itemprop": "streetAddress"}).text.strip()
            except:
                street_address = "<MISSING>"
            try:
                city = soup_loc3.find(
                    "span", {"itemprop": "addressLocality"}).text.strip()
            except:
                city = "<MISSING>"
            try:
                state = soup_loc3.find(
                    "abbr", {"itemprop": "addressRegion"}).text.strip()
            except:
                state = "<MISSING>"
            try:
                zipp = soup_loc3.find(
                    "span", {"itemprop": "postalCode"}).text.strip()
            except:
                zipp = "<MISSING>"
            try:
                country_code = soup_loc3.find(
                    "span", {"itemprop": "addressCountry"}).text.strip()
            except:
                country_code = "US"
            try:
                phone = list(soup_loc3.find(
                    "div", class_="location-info-phone").stripped_strings)[0]
            except:
                phone = "<MISSING>"
            try:
                hours_of_operation = " ".join(list(soup_loc3.find(
                    "table", class_="c-location-hours-details").stripped_strings)).replace("Day of the Week", "").replace("Hours", "").strip()
            except:
                hours_of_operation = "<MISSING>"
            # logger.info(phone)
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            store = ["<MISSING>" if x ==
                     "" else x for x in store]
            store = [str(x).encode('ascii', 'ignore').decode(
                'ascii').strip() if x else "<MISSING>" for x in store]
            # logger.info("data = " + str(store))
            # logger.info(
            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
