import csv
from sgrequests import SgRequests
import json
from sglogging import sglog
from bs4 import BeautifulSoup
import lxml.html

website = "martinsfoods.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
    locator_domain = website
    page_url = ""
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zip = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    locations_resp = session.get(
        "https://martinsfoods.com/apis/store-locator/locator/v1/stores/MRTN?storeType=GROCERY&maxDistance=10000&details=true"
    )

    loc_list = []

    locations = json.loads(locations_resp.text)["stores"]

    for l in locations:
        location_name = l["name"]
        street_address = l["address1"]
        if len(l["address2"]) > 0:
            street_address = street_address + "\n" + l["address2"]

        city = l["city"]
        state = l["state"]
        zip = l["zip"]
        store_number = l["storeNo"]
        location_type = l["storeType"]
        if location_type == "":
            location_type = "<MISSING>"
        latitude = l["latitude"]
        longitude = l["longitude"]

        store_url = "https://stores.martinsfoods.com/" + store_number
        store_resp = session.get(store_url)
        store_sel = lxml.html.fromstring(store_resp.text)
        country_code = store_sel.xpath(
            '//span[@itemprop="address"]//abbr[@itemprop="addressCountry"]'
        )
        if len(country_code) > 0:
            country_code = country_code[0].text.strip()

        phone = "".join(
            store_sel.xpath(
                '//div[@class="NAP-info l-container"]//span[@itemprop="telephone"]/text()'
            )
        ).strip()
        if phone == "":
            phone = "<MISSING>"
        page_url = store_url
        hours_of_operation = "\n".join(
            store_sel.xpath(
                '//div[@class="StoreDetails-hours--desktop u-hidden-xs"]//table/tbody/tr/@content'
            )
        ).strip()
        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        curr_list = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        loc_list.append(curr_list)
        # break

    log.info(f"No of records being processed: {len(loc_list)}")

    return loc_list


def scrape():
    data = fetch_data()
    write_output(data)
    log.info(f"Finished")


if __name__ == "__main__":
    scrape()
