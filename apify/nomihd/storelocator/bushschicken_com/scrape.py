# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "bushschicken.com"
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

    search_url = "http://www.bushschicken.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    tables = stores_sel.xpath('//div[@class="content"]/table')
    table_headers = stores_sel.xpath('//div[@class="content"]/h3/text()')
    for index in range(0, len(table_headers)):
        location_type = table_headers[index].strip()
        stores = tables[index].xpath(".//tr")
        for store in stores:
            if len("".join(store.xpath("td[1]/text()")).strip()) > 0:
                page_url = search_url
                locator_domain = website
                location_name = "BUSH'S CHICKEN"
                if location_name == "":
                    location_name = "<MISSING>"

                street_address = "".join(store.xpath("td[2]/text()")).strip()
                city = "".join(store.xpath("td[1]/text()")).strip()
                state = "".join(store.xpath("td[3]/text()")).strip()
                zip = "".join(store.xpath("td[4]/text()")).strip()

                country_code = "<MISSING>"
                if us.states.lookup(state):
                    country_code = "US"

                if street_address == "" or street_address is None:
                    street_address = "<MISSING>"

                if city == "" or city is None:
                    city = "<MISSING>"

                if state == "" or state is None:
                    state = "<MISSING>"

                if zip == "" or zip is None:
                    zip = "<MISSING>"

                store_number = "<MISSING>"
                phone = "".join(store.xpath("td[5]/text()")).strip()

                if location_type == "":
                    location_type = "<MISSING>"
                hours_of_operation = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"

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

        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
