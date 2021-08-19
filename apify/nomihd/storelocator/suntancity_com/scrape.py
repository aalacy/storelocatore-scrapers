# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "suntancity.com"
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

    search_url = "https://www.suntancity.com/find-a-salon"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[@class="city-link"]/@href')
    for store_url in stores:
        locator_domain = website
        page_url = "https://www.suntancity.com" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        if len("".join(store_sel.xpath('//h1[@class="h3"]/text()')).strip()) <= 0:
            sub_stores = store_sel.xpath(
                '//div[@class="stc-content-line-content "]/a[@class="btn btn-small"]/@href'
            )
            for sub in sub_stores:
                page_url = "https://www.suntancity.com" + sub
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                if (
                    len("".join(store_sel.xpath('//h1[@class="h3"]/text()')).strip())
                    > 0
                ):

                    location_name = "".join(
                        store_sel.xpath('//h1[@class="h3"]/text()')
                    ).strip()
                    address = "".join(
                        store_sel.xpath('//div[@class="salon-address"]/text()')
                    ).strip()

                    street_address = ", ".join(address.split(",")[:-2]).strip()
                    city = address.rsplit(",")[-2].strip()
                    state = address.rsplit(",")[-1].strip().split(" ")[0].strip()
                    zip = address.rsplit(",")[-1].strip().split(" ")[-1].strip()

                    if street_address == "":
                        street_address = "<MISSING>"

                    if city == "":
                        city = "<MISSING>"

                    if state == "":
                        state = "<MISSING>"

                    if zip == "" or zip.isdigit() is False:
                        zip = "<MISSING>"

                    country_code = "<MISSING>"
                    if us.states.lookup(state):
                        country_code = "US"

                    store_number = "<MISSING>"
                    phone = "".join(
                        store_sel.xpath('//div[@class="salon-phonenumber"]/a/text()')
                    ).strip()
                    location_type = "<MISSING>"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"

                    hours_of_operation = "; ".join(
                        store_sel.xpath(
                            '//div[@class="salon-hours font-body1"]/div/text()'
                        )
                    ).strip()

                    if phone == "":
                        phone = "<MISSING>"

                    page_url = store_req.url
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

        else:
            location_name = "".join(store_sel.xpath('//h1[@class="h3"]/text()')).strip()
            address = "".join(
                store_sel.xpath('//div[@class="salon-address"]/text()')
            ).strip()

            street_address = ", ".join(address.split(",")[:-2]).strip()
            city = address.rsplit(",")[-2].strip()
            state = address.rsplit(",")[-1].strip().split(" ")[0].strip()
            zip = address.rsplit(",")[-1].strip().split(" ")[-1].strip()

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if zip == "" or zip.isdigit() is False:
                zip = "<MISSING>"

            country_code = "<MISSING>"
            if us.states.lookup(state):
                country_code = "US"

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath('//div[@class="salon-phonenumber"]/a/text()')
            ).strip()
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            hours_of_operation = "; ".join(
                store_sel.xpath('//div[@class="salon-hours font-body1"]/div/text()')
            ).strip()

            if phone == "":
                phone = "<MISSING>"

            page_url = store_req.url
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
