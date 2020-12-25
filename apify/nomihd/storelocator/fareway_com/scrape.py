# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "fareway.com"
domain = "https://www.fareway.com"
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

    search_url = "https://www.fareway.com/stores/page/1"

    while True:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="cards"]/div')
        for store in stores:
            locator_domain = website
            page_url = (
                domain
                + "".join(store.xpath('.//h3[@class="card-title"]/a/@href')).strip()
            )
            location_name = " ".join(
                store.xpath('.//h3[@class="card-title"]/a/text()')
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            address = "".join(
                store.xpath('.//p[@class="card-subtitle"]/a/text()')
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

            store_number = location_name.split(" ")[0].strip().replace("#", "").strip()
            phone = "".join(
                store.xpath('.//div[@class="store-phone"]/p[1]/span/a/text()')
            ).strip()

            location_type = "<MISSING>"

            hours_of_operation = " ".join(
                store.xpath('.//div[@class="store-hours"]/p//text()')
            ).strip()

            hours_list = []
            if "Floral" in hours_of_operation:

                try:
                    hours = hours_of_operation.split("\n")
                    for hour in hours:
                        if "Floral" not in hour:
                            hours_list.append(hour)
                except:
                    pass

                hours_of_operation = " ".join(hours_list)

            latitude = "".join(store.xpath("@data-latitude")).strip()
            longitude = "".join(store.xpath("@data-longitude")).strip()

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

        next_page = "".join(
            stores_sel.xpath(
                '//div[@class="pagination-next-page pagination-bg"]/a/@href'
            )
        ).strip()
        if len(next_page) > 0:
            search_url = domain + next_page
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
