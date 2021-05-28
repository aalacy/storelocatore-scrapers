import csv
from sgrequests import SgRequests
import json
import re
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("speedycash_com")


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
all = []


def fetch_data():
    # Your scraper here

    res = session.get("https://www.speedycash.com/api/enabled-stores.json")

    jso = res.json()

    for js in jso:
        url = "https://www.speedycash.com/find-a-store/" + js["url"]
        if not js["temporarilyClosed"]:
            types = "Open"
        else:
            types = "Temporarily closed"

        if js["hours"] is not None:
            timi = js["hours"]["days"]
            tim = ""
            for i in timi:
                tim += i + ": "
                tim += (
                    str(timi[i]["openHour"])
                    + ":"
                    + str(timi[i]["openMin"])
                    + " - "
                    + str(timi[i]["closeHour"])
                    + ":"
                    + str(timi[i]["closeMin"])
                    + " "
                )
        else:
            tim = "<MISSING>"

        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        data = re.findall(
            r"({.*})", str(soup.find("script", {"type": "application/ld+json"}))
        )[0]
        data = json.loads(data)

        if tim == "<MISSING>":
            tim = (
                re.findall(r"Sunday.*pm", soup.text)[0]
                .replace("M", " M")
                .replace("S", " S")
                .replace("W", " W")
                .replace("T", " T")
                .replace("F", " F")
                .strip()
            )

        all.append(
            [
                "https://www.speedycash.com",
                js["crossStreets"],  # loc
                data["address"]["streetAddress"],  # street
                data["address"]["addressLocality"],  # city
                data["address"]["addressRegion"],  # state
                data["address"]["postalCode"],  # zip
                "US",
                js["storeId"],  # store #
                data["telephone"],  # phone
                types,  # type
                data["geo"]["latitude"],  # lat
                data["geo"]["longitude"],  # long
                tim,  # timing
                url,
            ]
        )
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
