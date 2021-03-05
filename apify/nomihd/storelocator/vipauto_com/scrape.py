# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "vipauto.com"
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

    search_url = "https://www.vipauto.com/locations"

    is_next_page = True
    while is_next_page is True:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="location"]')

        for store in stores:
            page_url = "".join(store.xpath('.//a[@class="store-link"]/@href')).strip()
            store_number = "".join(store.xpath("@data-location-id")).strip()

            locator_domain = website

            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            location_name = "".join(
                store_sel.xpath('//div[@class="title"]/h1/text()')
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            address = "".join(
                store_sel.xpath('//div[@class="location-map"]/@data-address')
            ).strip()

            street_address = address.split(",")[0].strip()
            city = address.split(",")[1].strip()
            state = address.split(",")[2].strip().split(" ")[0].strip()
            zip = address.split(",")[2].strip().split(" ")[1].strip()
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
            phone = "".join(store_sel.xpath('//div[@class="phone"]/a/text()')).strip()

            location_type = "<MISSING>"
            hours = store_sel.xpath('//div[@class="hours"]/div')
            hours_of_operation = ""
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath('div[@class="day"]/text()')).strip()
                time = "".join(hour.xpath('div[@class="hour"]/text()')).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = ";".join(hours_list).strip()

            latitude = "".join(
                store_sel.xpath('//div[@class="location-map"]/@data-latitude')
            ).strip()
            longitude = "".join(
                store_sel.xpath('//div[@class="location-map"]/@data-longitude')
            ).strip()

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

        next_page = stores_sel.xpath('//li/a[contains(text(),"Next")]/@href')
        if len(next_page) > 0:
            search_url = next_page[0]
        else:
            is_next_page = False

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
