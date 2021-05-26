import csv
from sgrequests import SgRequests
import json
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("pharmaca_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }
    session = SgRequests()
    r = session.get("https://www.pharmaca.com/store-locator", headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "jsonLocations")]/text()'))
        .split("jsonLocations: ")[1]
        .split('/div>\\n"},')[0]
        + '/div>\\n"}'
    )
    data = json.loads(jsblock)
    for obj in data["items"]:
        page_url = "https://www.pharmaca.com" + obj["website"]
        store_number = "<MISSING>"
        location_name = obj["name"]
        country_code = obj["country"]
        city = obj["city"]
        zip_code = obj["zip"]
        if "Santa" in zip_code:
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            zip_code = (
                "".join(tree.xpath('//p[contains(text(), "530 West")]/text()[3]'))
                .replace("\n", "")
                .strip()
            )
        state = obj["state"]
        street_address = obj["address"]

        lat = obj["lat"]
        longit = obj["lng"]
        phone_number = obj["phone"]
        location_type = "<MISSING>"

        hours1 = json.loads((obj["schedule_string"]))
        hours_of = ""
        for h in hours1:
            hours_of = (
                hours_of
                + " "
                + (
                    h
                    + " open "
                    + hours1[h]["from"]["hours"]
                    + " close "
                    + hours1[h]["to"]["hours"]
                )
            )

        locator_domain = "https://www.pharmaca.com/"

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
            hours_of,
            page_url,
        ]
        yield store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
