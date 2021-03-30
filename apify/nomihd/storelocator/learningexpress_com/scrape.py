# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html

website = "learningexpress.com"
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

    search_url = "https://learningexpress.com/stores/state-m2.php?url=https://learningexpress.com/locator/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[contains(text(),"Store Details")]/@href')
    for store_url in stores:
        page_url = store_url
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = (
            "".join(store_sel.xpath('//h1[@class="sp_storename"]/text()'))
            .strip()
            .replace("Store Info", "")
            .strip()
        )
        if location_name == "":
            location_name = "<MISSING>"

        street_address = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]/div/span[@itemprop="streetAddress"]/text()'
            )
        ).strip()
        city = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]/div/span[@itemprop="addressLocality"]/text()'
            )
        ).strip()
        state = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]/div/span[@itemprop="addressRegion"]/text()'
            )
        ).strip()
        zip = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]/div/span[@itemprop="postalCode"]/text()'
            )
        ).strip()

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
        phone_temp = store_sel.xpath('//div[@itemprop="address"]/span')
        phone = "<MISSING>"
        for ph in phone_temp:
            if "Phone :" in "".join(ph.xpath("text()")).strip():
                phone = "".join(ph.xpath("a/text()")).strip()

        location_type = "<MISSING>"
        hours = store_sel.xpath(
            '//div[@class="block_contact_text single-store-schemahours"]/dl/div'
        )
        hours_of_operation = ""
        for hour in hours:
            day = "".join(hour.xpath('span[@class="schemaWeekday"]/text()')).strip()
            if len(day) <= 0:
                day = "".join(
                    hour.xpath('strong/span[@class="schemaWeekday"]/text()')
                ).strip()

            time = "".join(hour.xpath("text()")).strip()
            if len(time) <= 0:
                time = "".join(hour.xpath("strong/text()")).strip()

            hours_of_operation = hours_of_operation + day + ":" + time + " "

        hours_of_operation = hours_of_operation.strip()

        latitude = "<MISSING>"
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
