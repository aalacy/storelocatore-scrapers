# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

website = "solsticesunglasses.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
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
    loc_list = []

    search_url = "https://solsticesunglasses.com/apps/store-locator"
    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.text.split("markersCoords.push(")
    for index in range(1, len(stores)):
        store_data = stores[index].split(");")[0].strip()
        latitude = store_data.split("lat:")[1].strip().split(",")[0].strip()
        longitude = store_data.split("lng:")[1].strip().split(",")[0].strip()

        store_number = store_data.split("id:")[1].strip().split(",")[0].strip()
        if latitude == "data.you.lat":
            break
        API_url = (
            "https://stores.boldapps.net/front-end/get_store_info.php?shop=solsticesunglasses.myshopify.com&data=detailed&store_id="
            + store_number
        )
        page_url = search_url
        locator_domain = website
        log.info(f"Pulling data for store ID: {store_number}")
        store_req = session.get(API_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.json()["data"])

        location_name = "".join(store_sel.xpath('//span[@class="name"]/text()')).strip()

        if location_name == "":
            location_name = "<MISSING>"

        street_address = "".join(
            store_sel.xpath('//span[@class="address"]/text()')
        ).strip()
        address_2 = "".join(store_sel.xpath('//span[@class="address2"]/text()')).strip()
        if len(address_2) > 0:
            street_address = street_address + ", " + address_2

        city = "".join(store_sel.xpath('//span[@class="city"]/text()')).strip()
        state = "".join(store_sel.xpath('//span[@class="prov_state"]/text()')).strip()
        zip = "".join(store_sel.xpath('//span[@class="postal_zip"]/text()')).strip()

        country_code = "".join(
            store_sel.xpath('//span[@class="country"]/text()')
        ).strip()

        if country_code == "":
            country_code = "<MISSING>"

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        phone = "".join(store_sel.xpath('//span[@class="phone"]/text()')).strip()

        location_type = "<MISSING>"
        hours = store_sel.xpath('//span[@class="hours"]/text()')
        hours_list = []
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                hours_list.append("".join(hour).strip())

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

        if (
            "Store hours vary subject to daily flight schedule. Please contact the store directly."
            in hours_of_operation
        ):
            hours_of_operation = "<MISSING>"

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"

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
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
