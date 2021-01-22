# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "ewm.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
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

    search_url = "https://www.ewm.co.uk/store-finder/"
    stores_req = session.get(search_url, headers=headers)
    stores_json = json.loads(
        stores_req.text.split("storelocator.sources = ")[1]
        .strip()
        .split("}}];")[0]
        .strip()
        + "}}]"
    )

    cord_dict = {}
    for data in stores_json:
        cord_dict[data["id"]] = data["lat"] + "," + data["lng"]

    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@id="storelocator_scroll"]/div[@class="source GB"]'
    )

    for store in stores:
        store_number = "".join(store.xpath('div[@class="go-to-source"]/@id')).strip()
        page_url = (
            "https://www.ewm.co.uk/storelocator/store/index?source_code=" + store_number
        )

        locator_domain = website
        location_name = "".join(
            store.xpath('div[@class="go-to-source"]/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        address = "".join(
            store.xpath(
                './/div[@class="store-info container"]/div[1]/div[1]/p[1]/text()'
            )
        ).strip()

        city = ""
        if "," in location_name:
            city = location_name.split(",")[-1].strip()

        street_address = ""
        add_list = []
        try:
            temp_addr = address.split(",")
            for add in temp_addr:
                if len("".join(add).strip()) > 0:
                    if add.strip() == city:
                        break
                    else:
                        add_list.append("".join(add).strip())

        except:
            pass

        street_address = ", ".join(add_list).strip()
        state = "<MISSING>"
        zip = address.split(",")[-2].strip()
        country_code = "GB"

        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        if country_code == "" or country_code is None:
            country_code = "<MISSING>"

        if store_number == "":
            store_number = "<MISSING>"

        phone = "".join(
            store.xpath(
                './/div[@class="store-info container"]/div[1]/div[1]/p[2]/text()'
            )
        ).strip()

        location_type = "<MISSING>"

        latitude = ""
        longitude = ""

        if store_number in cord_dict:
            latlng = cord_dict[store_number]
            latitude = latlng.split(",")[0].strip()
            longitude = latlng.split(",")[1].strip()

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = ""
        hours = store.xpath(
            './/div[@class="store-info container"]/div[1]/div[2]/p/text()'
        )
        hours_list = []
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if phone == "" or phone is None:
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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
