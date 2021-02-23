import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("fusian_com")


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

    base_link = "https://www.fusian.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="intrinsic")
    locator_domain = "fusian.com"

    data = []
    for item in items:
        link = item.a["href"]
        if "http" not in link:
            link = "https://www.fusian.com" + link
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text[1:-1].title()

        fin_script = ""
        all_scripts = base.find_all("script")
        for script in all_scripts:
            if "latitude" in str(script):
                fin_script = str(script)
                break

        store_data = json.loads(fin_script.split(">")[1].split("<")[0])
        street_address = store_data["address"]["streetAddress"]
        city = store_data["address"]["addressLocality"]
        state = store_data["address"]["addressRegion"]
        zip_code = store_data["address"]["postalCode"]
        phone = store_data["telephone"]
        latitude = store_data["geo"]["latitude"]
        longitude = store_data["geo"]["longitude"]

        if "855 W" in street_address and location_name != "Grandview":
            raw_address = base.find(class_="sqs-block map-block sqs-block-map")
            store_data = json.loads(raw_address["data-block-json"])["location"]
            street_address = store_data["addressLine1"]
            city = store_data["addressLine2"].split(",")[0].strip()
            state = store_data["addressLine2"].split(",")[1].strip()
            zip_code = store_data["addressLine2"].split(",")[2].strip()

            phone = "<MISSING>"
            if "Phone" in base.find_all(class_="sqs-block-content")[3].text:
                phone = list(
                    base.find_all(class_="sqs-block-content")[3].stripped_strings
                )[-1]

            latitude = store_data["mapLat"]
            longitude = store_data["mapLng"]

        country_code = "US"
        store_number = "<MISSING>"

        hours_of_operation = base.find_all(class_="sqs-block-content")[3].p.text.strip()
        if "sun-thurs" in hours_of_operation:
            hours_of_operation = (
                hours_of_operation
                + " "
                + base.find_all(class_="sqs-block-content")[3]
                .find_all("p")[1]
                .text.strip()
            )
        hours_of_operation = (
            hours_of_operation.replace("p", "p ").replace("  ", " ").strip()
        )

        if "p" not in hours_of_operation:
            hours_of_operation = " ".join(
                list(base.find_all(class_="sqs-block-content")[3].stripped_strings)[-2:]
            )

        location_type = "<MISSING>"

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
