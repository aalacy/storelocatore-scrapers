import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('checkers_com')





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
    base_url = "https://locations.checkers.com/index.html"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    store_name = []
    store_detail = []
    return_main_object = []

    k = soup.find_all("li", {"class": "c-directory-list-content-item"})
    for i in k:
        link = i.text.split("(")[-1]
        if link != "1)":
            city_link = "https://locations.checkers.com/" + i.find("a")['href']
            r1 = session.get(city_link)
            soup1 = BeautifulSoup(r1.text, "lxml")
            citylink = soup1.find_all(
                "li", {"class": "c-directory-list-content-item"})
            if citylink == []:
                for url in soup1.find_all("a", class_="Teaser-titleLink"):
                    page_url = "https://locations.checkers.com" + \
                        url["href"].replace("..", "").strip()
                    r_loc = session.get(page_url)
                    soup_loc = BeautifulSoup(r_loc.text, "lxml")
                    name = soup_loc.find(
                        "h1", class_="Nap-locationName").text.strip()
                    address = list(soup_loc.find(
                        "address", {"itemprop": "address"}).stripped_strings)
                    streetAddress = address[0]
                    city = address[1]
                    state = address[-3]
                    zip1 = address[-2]
                    country_code = address[-1]
                    phone = soup_loc.find(
                        "span", {"itemprop": "telephone"}).text.strip()
                    hours = " ".join(list(soup_loc.find(
                        "table", class_="c-location-hours-details").stripped_strings)).replace("Day of the Week Hours", "").strip()
                    latitude = json.loads(soup_loc.find(
                        "script", class_="js-map-config").text)["locs"][0]["latitude"]
                    longitude = json.loads(soup_loc.find(
                        "script", class_="js-map-config").text)["locs"][0]["longitude"]
                    tem_var = []
                    tem_var.append("https://checkers.com")
                    tem_var.append(name)
                    tem_var.append(streetAddress)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zip1)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("<MISSING>")
                    tem_var.append(latitude)
                    tem_var.append(longitude)
                    tem_var.append(hours)
                    tem_var.append(page_url)
                    yield tem_var
                    # logger.info("========================================", tem_var)
            for c in citylink:
                link1 = c.text.split("(")[-1]
                if link1 != "1)":
                    sublink = "https://locations.checkers.com/" + \
                        c.find("a")['href']
                    r2 = session.get(sublink)
                    soup2 = BeautifulSoup(r2.text, "lxml")
                    store_link = soup2.find_all("a", class_="Teaser-titleLink")
                    for st in store_link:
                        r3 = session.get(
                            "https://locations.checkers.com" + st['href'].replace("..", ""))
                        page_url = "https://locations.checkers.com" + \
                            st['href'].replace("..", "")
                        soup3 = BeautifulSoup(r3.text, "lxml")
                        streetAddress = soup3.find(
                            "meta", {"itemprop": "streetAddress"})['content']
                        state = soup3.find(
                            "abbr", {"class": "c-address-state"}).text
                        zip1 = soup3.find(
                            "span", {"class": "c-address-postal-code"}).text
                        city = soup3.find(
                            "span", {"class": "c-address-city"}).text
                        name = " ".join(
                            list(soup3.find("h1", {"class": "Nap-locationName"}).stripped_strings))
                        phone = soup3.find(
                            "span", {"class": "c-phone-number-span c-phone-main-number-span"}).text
                        hours = " ".join(list(soup3.find(
                            "table", {"class": "c-location-hours-details"}).find("tbody").stripped_strings))
                        latitude = soup3.find("meta", {"itemprop": "latitude"})[
                            'content']
                        longitude = soup3.find("meta", {"itemprop": "longitude"})[
                            'content']

                        tem_var = []
                        tem_var.append("https://checkers.com")
                        tem_var.append(name)
                        tem_var.append(streetAddress)
                        tem_var.append(city)
                        tem_var.append(state)
                        tem_var.append(zip1)
                        tem_var.append("US")
                        tem_var.append("<MISSING>")
                        tem_var.append(phone)
                        tem_var.append("<MISSING>")
                        tem_var.append(latitude)
                        tem_var.append(longitude)
                        tem_var.append(hours)
                        tem_var.append(page_url)
                        yield tem_var
                        # logger.info("========================================", tem_var)

                else:
                    one_link = "https://locations.checkers.com/" + \
                        c.find("a")['href']
                    page_url = one_link
                    r4 = session.get(one_link)
                    soup4 = BeautifulSoup(r4.text, "lxml")
                    streetAddress = soup4.find(
                        "meta", {"itemprop": "streetAddress"})['content']
                    state = soup4.find(
                        "abbr", {"class": "c-address-state"}).text
                    city = soup4.find("span", {"class": "c-address-city"}).text
                    zip1 = soup4.find(
                        "span", {"class": "c-address-postal-code"}).text
                    name = " ".join(
                        list(soup4.find("h1", {"class": "Nap-locationName"}).stripped_strings))
                    phone = soup4.find(
                        "span", {"class": "c-phone-number-span c-phone-main-number-span"}).text
                    hours = " ".join(list(soup4.find(
                        "table", {"class": "c-location-hours-details"}).find("tbody").stripped_strings))
                    latitude = soup4.find("meta", {"itemprop": "latitude"})[
                        'content']
                    longitude = soup4.find("meta", {"itemprop": "longitude"})[
                        'content']

                    tem_var = []
                    tem_var.append("https://checkers.com")
                    tem_var.append(name)
                    tem_var.append(streetAddress)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zip1)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("<MISSING>")
                    tem_var.append(latitude)
                    tem_var.append(longitude)
                    tem_var.append(hours)
                    tem_var.append(page_url)
                    yield tem_var
                    # logger.info("========================================", tem_var)
        else:
            one_link1 = "https://locations.checkers.com/" + i.find("a")['href']
            page_url = one_link1
            r5 = session.get(one_link1)
            soup5 = BeautifulSoup(r5.text, "lxml")
            streetAddress = soup5.find(
                "meta", {"itemprop": "streetAddress"})['content']
            state = soup5.find("abbr", {"class": "c-address-state"}).text
            city = soup5.find("span", {"class": "c-address-city"}).text
            zip1 = soup5.find("span", {"class": "c-address-postal-code"}).text
            name = " ".join(
                list(soup5.find("h1", {"class": "Nap-locationName"}).stripped_strings))
            phone = soup5.find(
                "span", {"class": "c-phone-number-span c-phone-main-number-span"}).text
            hours = " ".join(list(soup5.find(
                "table", {"class": "c-location-hours-details"}).find("tbody").stripped_strings))
            latitude = soup5.find("meta", {"itemprop": "latitude"})['content']
            longitude = soup5.find("meta", {"itemprop": "longitude"})[
                'content']
            # logger.info(streetAddress)

            tem_var = []
            tem_var.append("https://checkers.com")
            tem_var.append(name)
            tem_var.append(streetAddress)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append(hours)
            tem_var.append(page_url)
            yield tem_var
            # logger.info("========================================", tem_var)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
