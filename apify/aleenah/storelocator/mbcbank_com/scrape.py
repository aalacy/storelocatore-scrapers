import csv
import re
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("arhaus_com")
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
    # Your scraper here
    all = []
    res = session.get(
        "https://www.mbcbank.com/_/api/branches/36.8299114/-84.8483121/500"
    )
    stores = res.json()["branches"]

    logger.info(len(stores))

    for store in stores:
        description = store["description"]
        timing = (
            re.findall("Lobby Hours:(.*)Drive-Thru", description)[0]
            .replace("</div><div>", " ")
            .replace("</b>", "")
            .replace("</div>", "")
            .replace("<div>", "")
            .replace("<br>", "")
            .replace("<b>", "")
        )

        all.append(
            [
                "https://www.mbcbank.com",
                store["name"],
                store["address"],
                store["city"],
                store["state"],
                store["zip"],
                "US",
                "<MISSING>",
                store["phone"],
                "Branch",
                store["lat"],
                store["long"],
                timing.strip(),
                "<MISSING>",
            ]
        )
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
