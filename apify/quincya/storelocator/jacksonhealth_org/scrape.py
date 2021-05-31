import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("jacksonhealth_org")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_link = "https://jacksonhealth.org/locations/?locationsFiltersName=&view=map"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="locations-carousel-item")
    locator_domain = "jacksonhealth.org"

    for item in items:
        link = item.a["href"]

        location_name = (
            item.h3.text.replace("–", "-")
            .replace("\u200b", "")
            .replace("’", "'")
            .replace("ñ", "n")
            .strip()
        )
        logger.info(link)

        raw_address = item.p.text.split(",")
        street_address = (
            " ".join(raw_address[:-3]).replace("Deering Medical Plaza", "").strip()
        )
        street_address = (re.sub(" +", " ", street_address)).strip()
        city = raw_address[-3].strip()
        state = raw_address[-2].strip()
        zip_code = raw_address[-1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            phone = (
                item.find(class_="fas fa-phone")
                .find_next_sibling("a")
                .text.replace("(Adult Outpatient Services)", "")
                .replace("\u200b", "")
                .strip()
            )
        except:
            phone = "<MISSING>"

        try:
            hours_of_operation = (
                item.find(class_="fas fa-clock")
                .find_next_sibling("p")
                .text.replace("–", "-")
                .replace("North Dade Health Center is open", "")
                .replace("Varies by service", "<MISSING>")
                .strip()
            )
        except:
            hours_of_operation = "<MISSING>"

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            latitude = base.find(
                class_="simple-map__map location-hero-map-wrapper__map-div"
            )["data-lat"]
            longitude = base.find(
                class_="simple-map__map location-hero-map-wrapper__map-div"
            )["data-lng"]
        except:
            map_link = base.find(class_="location-hero-map-wrapper__map-div").iframe[
                "src"
            ]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()

        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
