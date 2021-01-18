import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("lendnation_com")


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    locator_domain = "https://www.lendnation.com/"
    ext = "location/index.html"

    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    states = base.find_all(class_="Directory-listItem")
    state_links = []
    for state in states:
        link = "https://www.lendnation.com/location/" + state.a["href"]
        state_links.append(link)

    url_list = []
    for link in state_links:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        script = base.find(class_="js-directoryHierarchy")
        if not script:
            continue

        logger.info(link)
        loc_json = json.loads(script.text)

        for loc in loc_json:
            for location in loc_json[loc]["children"]:
                location = loc_json[loc]["children"][location]
                lat = location["latitude"]
                longit = location["longitude"]
                url = location["url"]

                url_list.append([url, lat, longit])

    link_list = []
    for url_ext in url_list:
        url = "https://www.lendnation.com/location/" + url_ext[0]
        link_list.append(url)

    all_store_data = []

    logger.info("Getting data ..")
    for link in link_list:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()

        lat = base.find("meta", attrs={"itemprop": "latitude"})["content"]
        longit = base.find("meta", attrs={"itemprop": "longitude"})["content"]

        city = base.find("meta", attrs={"itemprop": "addressLocality"})["content"]
        street_address = base.find("meta", attrs={"itemprop": "streetAddress"})[
            "content"
        ]
        state = base.find("abbr", attrs={"itemprop": "addressRegion"}).text
        zip_code = base.find("span", attrs={"itemprop": "postalCode"}).text
        phone_number = base.find("span", attrs={"itemprop": "telephone"}).text

        hours = (
            base.find(class_="c-location-hours-details")
            .get_text(" ")
            .replace("Day of the Week Hours", "")
            .replace("PM", "PM ")
            .replace("  ", " ")
            .strip()
        )

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        country_code = "US"
        page_url = link

        store_data = [
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

        all_store_data.append(store_data)
    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
