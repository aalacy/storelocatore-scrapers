import csv
from sgrequests import SgRequests
import json
from sglogging import sglog
import lxml.html

website = "giantfood.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)

        log.info(f"No of records being processed: {len(temp_list)}")


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
    store_types = ["GROCERY", "GAS_STATION"]
    loc_list = []

    for s in store_types:
        locations_resp = session.get(
            "https://giantfood.com/apis/store-locator/locator/v1/stores/GNTL?storeType="
            + s.strip()
            + "&maxDistance=10000&details=true",
            headers=headers,
        )

        locations = json.loads(locations_resp.text)["stores"]

        for loc in locations:
            location_name = loc["name"]
            street_address = loc["address1"]
            if len(loc["address2"]) > 0:
                street_address = street_address + "\n" + loc["address2"]

            city = loc["city"]
            state = loc["state"]
            zip = loc["zip"]
            store_number = loc["storeNo"]
            location_type = loc["storeType"]
            if location_type == "":
                location_type = "<MISSING>"
            latitude = loc["latitude"]
            longitude = loc["longitude"]

            store_url = "https://stores.giantfood.com/" + store_number
            store_resp = session.get(store_url, headers=headers)
            store_sel = lxml.html.fromstring(store_resp.text)
            country_code = "".join(
                store_sel.xpath(
                    '//span[@itemprop="address"]'
                    '//abbr[@itemprop="addressCountry"]/text()'
                )
            ).strip()
            if country_code == "":
                country_code = "<MISSING>"

            phone = "".join(
                store_sel.xpath(
                    '//div[@class="NAP-info l-container"]'
                    '//span[@itemprop="telephone"]/text()'
                )
            ).strip()
            if phone == "":
                phone = "<MISSING>"
            page_url = store_url
            hours_of_operation = "\n".join(
                store_sel.xpath(
                    '//div[@class="StoreDetails-hours--desktop u-hidden-xs"]'
                    "//table/tbody/tr/@content"
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

    return loc_list


def scrape():
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
