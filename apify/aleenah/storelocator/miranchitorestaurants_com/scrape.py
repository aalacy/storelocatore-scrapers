import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup
import cloudscraper

logger = SgLogSetup().get_logger("miranchitorestaurants_com")


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


session = SgRequests()
scraper = cloudscraper.create_scraper(sess=session, debug=False)


def fetch_data():
    # Your scraper here
    all = []
    res = scraper.get("http://www.miranchitorestaurants.com/")
    logger.info(f"Status Code: {res.status_code}")
    soup = BeautifulSoup(res.text, "html.parser")
    scripts = soup.find_all("script", {"type": "application/ld+json"})
    for script in scripts:
        jso = json.loads(re.findall(r"{.*}", str(script))[0])
        tim = (
            " ".join(jso["openingHours"])
            .replace("Mo", "Monday")
            .replace("Tu", "Tuesday")
            .replace("We", "Wednesday")
            .replace("Th", "Thursday")
            .replace("Fr", "Friday")
            .replace("Sa", "Saturday")
            .replace("Su", "Sunday")
            .strip()
        )
        loc = jso["address"]["addressLocality"]
        lat, long = re.findall(
            r'"lat":(-?[\d\.]+),"lng":(-?[\d\.]+),"menuLandingPageUrl":null,"name":"'
            + loc.strip(),
            str(soup),
        )[0]

        all.append(
            [
                "https://www.miranchitorestaurants.com/",
                loc,  # name
                jso["address"]["streetAddress"],
                jso["address"]["addressLocality"],
                jso["address"]["addressRegion"],
                jso["address"]["postalCode"],
                "US",
                "<MISSING>",  # store #
                jso["address"]["telephone"],  # phone
                jso["@type"],  # type
                lat,  # lat
                long,  # long
                tim,  # timing
                "https://www.miranchitorestaurants.com/"
                + loc.strip().lower().replace(" ", "-"),
            ]
        )

    return all


def scrape():
    logger.info("Start Scraping")
    data = fetch_data()
    write_output(data)
    logger.info(f"Finished Grabbing data and got {len(data)} locations")


scrape()
