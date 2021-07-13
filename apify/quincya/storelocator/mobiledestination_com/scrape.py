import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("mobiledestination_com")


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

    base_link = "https://mobiledestination.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="city-name")
    locator_domain = "mobiledestination.com"

    for item in items:

        link = "https://mobiledestination.com" + item.a["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()
        logger.info(link)
        script = base.find_all("script", attrs={"type": "application/ld+json"})[
            -1
        ].contents[0]
        store = json.loads(script)

        street_address = store["address"]["streetAddress"].replace("&#39;", "'")
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        country_code = store["address"]["addressCountry"]["name"]
        store_number = link.split("locations/")[1].split("/")[0]
        location_type = "<MISSING>"
        phone = store["telephone"]

        hours_of_operation = " ".join(
            list(base.find(class_="store-hours").ul.stripped_strings)
        )

        try:
            latitude = store["geo"]["latitude"].strip()
            longitude = store["geo"]["longitude"].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
