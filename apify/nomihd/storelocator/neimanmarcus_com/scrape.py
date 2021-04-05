# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html

website = "neimanmarcus.com"
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

    search_url = "https://www.neimanmarcus.com/stores/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="store-info nmResult-store-info"]')
    for store in stores:
        page_url = (
            "https://www.neimanmarcus.com"
            + "".join(store.xpath('div[@class="store-name"]/a/@href')).strip()
        )

        locator_domain = website
        location_name = (
            "".join(store.xpath('div[@class="store-name"]/a/text()'))
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", " ")
            .strip()
        )
        if location_name == "":
            location_name = "<MISSING>"

        street_address = "".join(
            store.xpath('.//span[@itemprop="streetAddress"]/text()')
        ).strip()
        city = (
            "".join(store.xpath('.//span[@itemprop="addressLocality"]/text()'))
            .strip()
            .replace(",", "")
            .strip()
        )
        state = "".join(
            store.xpath('.//span[@itemprop="addressRegion"]/text()')
        ).strip()
        zip = "".join(store.xpath('.//span[@itemprop="postalCode"]/text()')).strip()

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
            store.xpath('.//span[@class="block_display telephoneNumber"]/a/text()')
        ).strip()

        location_type = "<MISSING>"
        hours = store.xpath(
            './/div[@class="grid-40 tablet-grid-50 grid-parent store-hours directory"]/table/tr'
        )
        hours_of_operation = ""
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("td[1]/text()")).strip()
            time = "".join(hour.xpath("td[2]/text()")).strip()
            hours_list.append((day + time).replace(".-", ":").strip())

        hours_of_operation = ";".join(hours_list).strip()

        map_link = "".join(
            store.xpath('.//div[@class="map-directions"]/a/@onclick')
        ).strip()

        latitude = ""
        try:
            latitude = map_link.split("sll=")[1].strip().split(",")[0].strip()
        except:
            try:
                latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
            except:
                try:
                    latitude = map_link.split("&ll=")[1].strip().split(",")[0].strip()
                except:
                    pass

        longitude = ""
        try:
            longitude = (
                map_link.split("sll=")[1]
                .strip()
                .split(",")[1]
                .strip()
                .split("&")[0]
                .strip()
            )
        except:
            try:
                longitude = map_link.split("/@")[1].strip().split(",")[1].strip()
            except:
                try:
                    longitude = (
                        map_link.split("&ll=")[1]
                        .strip()
                        .split(",")[1]
                        .strip()
                        .split("&")[0]
                        .strip()
                    )
                except:
                    pass

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
