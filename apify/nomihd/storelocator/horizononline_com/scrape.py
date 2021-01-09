# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "horizononline.com"
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

    search_url = "https://www.horizononline.com/store-locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[@class="lazy bg"]/@href')
    for store_url in stores:
        page_url = "https://www.horizononline.com" + store_url
        locator_domain = website

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(
            store_sel.xpath('//div[@class="store-details constrain"]//h1/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        address = store_sel.xpath(
            '//div[@class="store-details constrain"]//address/text()'
        )

        add_list = []
        for add in address:
            add_list.append("".join(add).strip())

        street_address = add_list[0]
        city = add_list[1].split(",")[0].strip()
        state = add_list[1].split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[1].split(",")[1].strip().split(" ")[1].strip()
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        store_number = "<MISSING>"
        phone = "".join(
            store_sel.xpath(
                '//div[@class="store-details constrain"]//p/a[contains(@href,"tel:")]/text()'
            )
        ).strip()

        location_type = "<MISSING>"
        temp_hours = store_sel.xpath('//div[@class="store-details constrain"]//p')
        hours_of_operation = ""
        hours_list = []
        for temp in temp_hours:
            text = "".join(temp.xpath("strong/text()")).strip()
            if "Hours" in text:
                day = text
                time = "".join(temp.xpath("text()")).strip()
                hours_list.append(day + time)

        hours_of_operation = ";".join(hours_list).strip()

        map_img = "".join(
            store_sel.xpath('//div[@class="unit1of2 gmap"]/img/@src')
        ).strip()

        latitude = map_img.split("%7C")[1].strip().split(",")[0].strip()
        longitude = (
            map_img.split("%7C")[1].strip().split(",")[1].strip().split("&")[0].strip()
        )

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
