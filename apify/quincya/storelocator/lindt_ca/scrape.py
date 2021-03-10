import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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

    session = SgRequests()

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    locator_domain = "lindt.ca"

    base_link = "https://www.lindt.ca/en/stores"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "locationItems" in str(script):
            script = script.contents[0].strip()
            res_json = json.loads(script)["*"]["Magento_Ui/js/core/app"]["components"][
                "locationList"
            ]["locationItems"]
            break

    for loc in res_json:

        location_name = loc["title"].strip()

        store_number = loc["location_id"]
        phone_number = loc["phone"]
        if not phone_number:
            phone_number = "<MISSING>"

        lat = loc["latitude"]
        longit = loc["longitude"]

        street_address = loc["street"].strip()
        city = loc["city"].strip()
        if city == "Bloomington":
            continue
        try:
            state = loc["region"].replace("Bacău", "BC").replace("Alba", "AB").strip()
        except:
            state = "<MISSING>"
        try:
            zip_code = loc["zip"].strip()
        except:
            zip_code = "<MISSING>"
        location_type = "Open"

        country_code = loc["country_id"]
        hours = (
            loc["opening_hours_monday"]
            + " "
            + loc["opening_hours_tuesday"]
            + " "
            + loc["opening_hours_wednesday"]
            + " "
            + loc["opening_hours_thursday"]
            + " "
            + loc["opening_hours_friday"]
            + " "
            + loc["opening_hours_saturday"]
            + " "
            + loc["opening_hours_sunday"]
        ).strip()

        if "Temporarily closed" in location_name:
            location_type = "Temporarily Closed"

        location_name = location_name.split("(")[0].strip()

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
            base_link,
        ]

        yield store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
