import csv
import json
import os
import re

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger("pepboys.com")

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"

headers = {"User-Agent": user_agent}

DEFAULT_PROXY_URL = "https://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"


def set_proxies():
    if "PROXY_PASSWORD" in os.environ and os.environ["PROXY_PASSWORD"].strip():

        proxy_password = os.environ["PROXY_PASSWORD"]
        url = (
            os.environ["PROXY_URL"] if "PROXY_URL" in os.environ else DEFAULT_PROXY_URL
        )
        proxy_url = url.format(proxy_password)
        proxies = {
            "https://": proxy_url,
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

    locator_domain = "https://www.pepboys.com"
    to_scrape = "https://pepboys.com/stores"
    session = SgRequests()
    session.proxies = set_proxies()
    page = session.get(to_scrape, headers=headers)
    session.close()
    assert page.status_code == 200
    soup = BeautifulSoup(page.content, "html.parser")
    main = soup.find("div", {"class": "store-locator__home-browse-location"})
    states = main.find_all("a", {"class": "btn-link"})

    state_list = []
    city_list = []
    page_list = []
    for state in states:
        link = locator_domain + state["href"]
        state_list.append(link)

    for state in state_list:
        log.info(f"State: {state}")
        session = SgRequests()
        session.proxies = set_proxies()
        page = session.get(state, headers=headers)
        session.close()
        assert page.status_code == 200
        soup = BeautifulSoup(page.content, "html.parser")
        main = soup.find("div", {"class": "store-locator__home-browse-location"})
        cities = main.find_all("a", {"class": "btn-link"})
        for city in cities:
            link = locator_domain + city["href"]
            city_list.append(link)

    for city_link in city_list:
        log.info(f"City: {city_link}")
        session = SgRequests()
        session.proxies = set_proxies()
        page = session.get(city_link, headers=headers)
        session.close()
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
            page_links = (
                "https://www.pepboys.com/stores/"
                + state
                + "/"
                + city.replace(" ", "-")
                + "/"
                + street_address.replace(" ", "-").replace("#", "-")
                + "?storeCode="
                + store_number
            )
            page_list.append(
                {
                    "page_url": page_links,
                    "location_name": location_name,
                    "street_address": street_address,
                    "city": city,
                    "state": state,
                    "zip_code": zip_code,
                    "country_code": country_code,
                    "phone_number": phone_number,
                    "store_number": store_number,
                    "latitude": lat,
                    "longitude": longit,
                }
            )

    for pl in page_list:
        location_name = pl["location_name"]
        street_address = pl["street_address"]
        city = pl["city"]
        state = pl["state"]
        zip_code = pl["zip_code"]
        country_code = pl["country_code"]
        phone_number = pl["phone_number"]
        store_number = pl["store_number"]
        page_url = pl["page_url"]
        lat = pl["latitude"]
        longit = pl["longitude"]
        log.info(f"Fetching data from: {page_url}")
        session = SgRequests()
        session.proxies = set_proxies()
        page = session.get(page_url, headers=headers)
        session.close()
        assert page.status_code == 200
        soup = BeautifulSoup(page.content, "html.parser")
        hours = (
            " ".join(
                list(
                    soup.find(class_="weekly-time").find_previous("ul").stripped_strings
                )
            )
            .replace("\xa0", " ")
            .replace("\t", "")
            .replace("\n", " ")
        )
        hours = (re.sub(" +", " ", hours)).strip()

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
    log.info(f"Total Locations: {len(page_list)}")


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished grabbing locations")


if __name__ == "__main__":
    scrape()
