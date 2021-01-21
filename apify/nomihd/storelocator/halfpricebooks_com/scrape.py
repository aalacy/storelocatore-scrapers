# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "halfpricebooks.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "hpb.com",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
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
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)

        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    loc_list = []

    search_url = "https://hpb.com/all-stores-list"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@id="stores-list"]//ul/li/a/@href')
    for store_url in stores:
        if len(store_url) > 0:
            page_url = "https://hpb.com" + store_url
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//h1[@class="store-details-name"]/text()')
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            address = "".join(
                store_sel.xpath('//div[@class="font-large font-pn-reg"]/div[1]/text()')
            ).strip()

            street_address = ""
            city = ""
            state = ""
            zip = ""
            if len(address.split(",")) == 3:
                street_address = address.split(",")[0].strip()
                city = address.split(",")[1].strip()
                state = address.split(",")[2].strip().split(" ")[0].strip()
                zip = address.split(",")[2].strip().split(" ")[1].strip()
            elif len(address.split(",")) == 4:
                street_address = ", ".join(address.split(",")[:2]).strip()
                city = address.split(",")[2].strip()
                state = address.split(",")[3].strip().split(" ")[0].strip()
                zip = address.split(",")[3].strip().split(" ")[1].strip()

            elif len(address.split(",")) == 2:
                street_address = "<MISSING>"
                city = address.split(",")[0].strip()
                state = address.split(",")[1].strip()
                zip = "<MISSING>"

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

            store_number = page_url.split("/")[-1].strip()
            phone = "".join(
                store_sel.xpath(
                    '//div[@class="font-large font-pn-reg"]/div[@class="mts"]/text()'
                )
            ).strip()

            location_type = "<MISSING>"
            hours_of_operation = (
                " ".join(
                    store_sel.xpath('//ul[@class="store-details-hours mts"]/li/text()')
                )
                .strip()
                .replace("Outlets do not buy merchandise from the public.", "")
                .strip()
                .replace("Outlets are unable to buy merchandise from the public.", "")
                .strip()
            )

            if "Not Open to the Public" in hours_of_operation:
                hours_of_operation = "<MISSING>"
                location_type = "Not Open to the Public"
            elif (
                "This HPB store is closed. Shop online at HPB.com."
                in hours_of_operation
            ):

                hours_of_operation = "<MISSING>"
                location_type = "This HPB store is closed. Shop online at HPB.com."
            else:
                if len(hours_of_operation) > 0:
                    location_type = "Open"

            latitude = "".join(
                store_sel.xpath('//div[@id="embed-map-store"]/@data-lat')
            ).strip()
            longitude = "".join(
                store_sel.xpath('//div[@id="embed-map-store"]/@data-lng')
            ).strip()

            if latitude == "":
                latitude = "<MISSING>"
            if longitude == "":
                longitude = "<MISSING>"

            if hours_of_operation == "":
                hours_of_operation = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"

            if page_url == store_req.url:
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
