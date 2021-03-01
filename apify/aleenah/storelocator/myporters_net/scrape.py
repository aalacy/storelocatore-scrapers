import csv
import json
from sgselenium import SgSelenium
import re


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


driver = SgSelenium().chrome()


def fetch_data():
    url = "https://circular.myporters.net/find-your-store/"
    all = []
    driver.get(url)

    stores = json.loads(re.findall("locations = (\[[^]]+\])", driver.page_source)[0])

    for store in stores:
        try:
            phone = store["phone"].strip()
        except:
            phone = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        all.append(
            [
                "https://www.myporters.net",
                store["name"],
                store["address1"],
                store["city"],
                store["state"],
                store["zipCode"],
                "US",
                store["storeID"],  # store #
                phone,  # phone
                "<MISSING>",  # type
                store["latitude"],  # lat
                store["longitude"],  # long
                store["hourInfo"]
                .replace("M-SA", "Monday - Saturday")
                .replace("M-SU", "Monday - Sunday")
                .replace("SUN", "Sunday")
                .replace("SU", "Sunday")
                .replace("\n", " "),  # timing
                "https://circular.myporters.net/find-your-store/",
            ]
        )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
