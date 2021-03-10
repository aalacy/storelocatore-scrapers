# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "marylandfriedchicken.com"
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

    search_url = "https://www.marylandfriedchicken.net/directory/"

    while True:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = json.loads(
            stores_req.text.split("'#sabai-content .sabai-directory-map',")[1]
            .strip()
            .split("}],")[0]
            .strip()
            + "}]"
        )
        for store in stores:
            locator_domain = website
            store_content_sel = lxml.html.fromstring(store["content"])
            page_url = "".join(
                store_content_sel.xpath('//div[@class="sabai-directory-title"]/a/@href')
            ).strip()
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            location_name = " ".join(
                store_sel.xpath('//h1[@class="title"]/text()')
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            street_address = "".join(
                store_sel.xpath(
                    '//div[@itemprop="address"]/span[@itemprop="streetAddress"]/text()'
                )
            ).strip()
            city = "".join(
                store_sel.xpath(
                    '//div[@itemprop="address"]/span[@itemprop="addressLocality"]/text()'
                )
            ).strip()
            state = "".join(
                store_sel.xpath(
                    '//div[@itemprop="address"]/span[@itemprop="addressRegion"]/text()'
                )
            ).strip()
            zip = "".join(
                store_sel.xpath(
                    '//div[@itemprop="address"]/span[@itemprop="postalCode"]/text()'
                )
            ).strip()
            country_code = "".join(
                store_sel.xpath(
                    '//div[@itemprop="address"]/span[@itemprop="addressCountry"]/text()'
                )
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

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath(
                    '//div[@class="sabai-col-sm-8 sabai-directory-main"]//div[@class="sabai-directory-contact-tel"]/span[@itemprop="telephone"]/text()'
                )
            ).strip()

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"

            latitude = store["lat"]
            longitude = store["lng"]

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

        next_page = stores_sel.xpath(
            '//div[@class="sabai-pagination sabai-btn-group"]/a'
        )

        if len(next_page) > 0:
            search_url = "".join(next_page[-1].xpath("@href")).strip()
            if len(search_url) <= 0:
                break

        else:
            break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
