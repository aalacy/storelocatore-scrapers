from bs4 import BeautifulSoup
import csv
import time
import json

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("middlesexbank_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    # Your scraper here
    data = []
    res = session.post(
        "https://www.middlesexbank.com/ZagLocationsApi/Locations/Search",
        json={
            "Radius": 500,
            "Latitude": 42.2775281,
            "Longitude": -71.3468091,
            "Connectors": {
                "Website": {"icon": "locations.png", "zIndex": 10000, "selected": True},
                "ATM": {"icon": "locations.png", "zIndex": 9996, "selected": True},
            },
        },
    )
    branches = []
    locations = json.loads(res.json())

    for location in locations:
        if location["LocationType"] == "Branch":
            branches.append(location)

    for branch in branches:
        url = "https://www.middlesexbank.com" + branch["NodeAliasPath"]
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        dat = (
            soup.find("div", {"class": "main"})
            .find_all("div", {"class": "container"})[1]
            .text.split("Lobby")[-1]
            .split("Drive-Thru")[0]
            .split("Get In Touch")[0]
        )
        tim = " ".join(dat.replace("\n", " ").split("\r")).strip()

        data.append(
            [
                "https://www.middlesexbank.com",
                url,
                branch["Name"],
                (branch["Address1"] + " " + branch["Address2"]).strip(),
                branch["City"],
                branch["State"],
                branch["Zip"],
                "US",
                branch["Id"],
                branch["Phone"],
                branch["LocationType"],
                branch["Latitude"],
                branch["Longitude"],
                tim,
            ]
        )

    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
