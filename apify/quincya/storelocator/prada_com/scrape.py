import csv
import json

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger(logger_name="prada.com")


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

    base_link = "https://www.prada.com/us/en/store-locator.html"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="d-none")[-1].find_all("a")
    locator_domain = "prada.com"

    for item in items:
        link = item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        js = base.find(id="jsonldLocalBusiness").contents[0].replace("\r\n", " ")
        store = json.loads(js)

        country_code = store["address"]["addressCountry"]
        log.info(link)
        location_name = store["name"]
        street_address = (
            store["address"]["streetAddress"]
            .replace("Bal Harbour FL 33154", "")
            .replace("W. Montreal, QC H3G 1P7", "")
            .replace("New York City, New York 10022", "")
            .strip()
            .replace("  ", " ")
        )
        street_address = (
            street_address.split(", Houston")[0]
            .split(", New York")[0]
            .split(", Manchester")[0]
            .strip()
        )
        city = store["address"]["addressLocality"]
        state = "<MISSING>"
        zip_code = store["address"]["postalCode"]
        if not zip_code:
            zip_code = "<MISSING>"
        store_number = link.split(".")[-2]
        location_type = "<MISSING>"
        phone = store["telephone"]
        if not phone:
            phone = "<MISSING>"
        hours_of_operation = (
            store["openingHours"].strip().replace("  ", " ").replace("--", "Closed")
        )
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"
        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

        yield [
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
