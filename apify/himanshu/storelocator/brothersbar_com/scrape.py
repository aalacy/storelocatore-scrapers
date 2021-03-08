import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
import lxml.html

logger = SgLogSetup().get_logger("brothersbar_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    base_url = "https://www.brothersbar.com"
    r = session.get("https://www.brothersbar.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "brothersbar"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    stores_sel = lxml.html.fromstring(r.text)
    stores = stores_sel.xpath('//li[@id="comp-ikmnfi1c1"]/ul/li/a/@href')
    for location_url in stores:
        logger.info(location_url)
        r_location = session.get(location_url, headers=headers)
        soup_location = BeautifulSoup(r_location.text, "lxml")

        tag_hours = soup_location.find(
            lambda tag: tag.name == "span" and "hours:" in tag.text.lower()
        )
        if tag_hours is None:
            continue
        tag_hours = tag_hours.parent.parent
        hours_of_operation = (
            ",".join(list(tag_hours.stripped_strings))
            .replace(",CLOSING HOURS SUBJECT TO CHANGE", "")
            .replace("HOURS:,", "")
            .replace(",:,", ":")
            .strip()
        )

        tag_address = soup_location.find(
            lambda tag: tag.name == "span"
            and "brothers bar & grill" in tag.text.lower()
        )
        tag_address = tag_address.parent.parent
        list_address = list(tag_address.stripped_strings)

        street_address = list_address[1]
        city = list_address[2].split(",")[0]
        state = list_address[2].split(",")[1].strip().split(" ")[0]
        zipp = list_address[2].split(",")[1].strip().split(" ")[-1]
        phone = list_address[-1]

        location_name = city

        store = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zipp,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
            location_url,
        ]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
