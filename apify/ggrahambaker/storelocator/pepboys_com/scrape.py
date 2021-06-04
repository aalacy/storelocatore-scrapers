import csv
import json
import os
import re

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger("scrape_com")

DEFAULT_PROXY_URL = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"


def set_proxies():
    if "PROXY_PASSWORD" in os.environ and os.environ["PROXY_PASSWORD"].strip():

        proxy_password = os.environ["PROXY_PASSWORD"]
        url = (
            os.environ["PROXY_URL"] if "PROXY_URL" in os.environ else DEFAULT_PROXY_URL
        )
        proxy_url = url.format(proxy_password)
        proxies = {
            "http://": proxy_url,
        }
        return proxies
    else:
        return None


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    session.proxies = set_proxies()

    locator_domain = "https://www.pepboys.com"
    to_scrape = "https://stores.pepboys.com"
    page = session.get(to_scrape, headers=headers)
    assert page.status_code == 200
    soup = BeautifulSoup(page.content, "html.parser")
    main = soup.find("div", {"class": "store-locator__home-browse-location"})
    states = main.find_all("a", {"class": "btn-link"})

    state_list = []
    city_list = []
    for state in states:
        link = locator_domain + state["href"]
        state_list.append(link)

    for state in state_list:
        log.info(state)
        session = SgRequests()
        session.proxies = set_proxies()
        page = session.get(state, headers=headers)
        assert page.status_code == 200
        soup = BeautifulSoup(page.content, "html.parser")
        main = soup.find("div", {"class": "store-locator__home-browse-location"})
        cities = main.find_all("a", {"class": "btn-link"})
        for city in cities:
            link = locator_domain + city["href"]
            city_list.append(link)

    for city_link in city_list:
        log.info(city_link)
        session = SgRequests()
        session.proxies = set_proxies()
        page = session.get(city_link, headers=headers)
        assert page.status_code == 200
        soup = BeautifulSoup(page.content, "html.parser")
        js = soup.main.find(id="mapDataArray").text.strip()
        locs = json.loads(js)
        for loc in locs:
            location_name = loc["Name"]
            street_address = loc["addressLine1"]
            city = loc["town"]
            state = loc["isoCodeShort"]
            zip_code = loc["postalCode"]
            country_code = "US"
            phone_number = loc["Phone"]
            store_number = loc["storeNumber"]
            location_type = "<MISSING>"
            lat = loc["Lat"]
            longit = loc["Long"]

            try:
                page_url = (
                    "https://www.pepboys.com/stores/"
                    + state
                    + "/"
                    + city
                    + "/"
                    + street_address.replace(" ", "-")
                    + "?storeCode="
                    + store_number
                )
                page = session.get(page_url, headers=headers)
                assert page.status_code == 200
                soup = BeautifulSoup(page.content, "html.parser")
                hours = (
                    " ".join(
                        list(
                            soup.find(class_="weekly-time")
                            .find_previous("ul")
                            .stripped_strings
                        )
                    )
                    .replace("\xa0", " ")
                    .replace("\t", "")
                    .replace("\n", " ")
                )
                hours = (re.sub(" +", " ", hours)).strip()
            except:
                page_url = city_link
                hours = "<INACCESSIBLE>"

            yield [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone_number,
                location_type,
                lat,
                longit,
                hours,
                page_url,
            ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
