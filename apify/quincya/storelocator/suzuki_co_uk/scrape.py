import csv
import json

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests


log = sglog.SgLogSetup().get_logger(logger_name="suzuki.co.uk")


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

    base_link = "https://cars.suzuki.co.uk/find-a-dealer/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    get_headers = {"User-Agent": user_agent}

    session = SgRequests()

    dup_tracker = []

    locator_domain = "suzuki.co.uk"

    req = session.get(base_link, headers=get_headers)
    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "allDealers" in str(script):
            script = str(script)
            break

    stores = json.loads(script.split("allDealers =")[1].split(";\r\n")[0])

    for store in stores:
        final_link = store["visitDealerPageLink"]
        location_name = store["name"]
        raw_address = store["address"].split(",")
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        try:
            state = raw_address[2].strip()
            if not state:
                state = "<MISSING>"
        except:
            state = "<MISSING>"
        zip_code = store["postcode"]
        country_code = "GB"
        store_number = store["dealerCode"]
        if store_number in dup_tracker:
            continue
        dup_tracker.append(store_number)
        location_type = ", ".join(store["serviceTypes"])
        phone = store["phone"]

        try:
            hours_of_operation = ""
            raw_hours = store["openingHours"]

            for row in raw_hours:
                hours_of_operation = (
                    hours_of_operation + " " + row["day"] + " " + row["times"]
                ).strip()
        except:
            hours_of_operation = "<MISSING>"

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        latitude = store["location"]["lat"]
        longitude = store["location"]["lng"]

        yield [
            locator_domain,
            final_link,
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
