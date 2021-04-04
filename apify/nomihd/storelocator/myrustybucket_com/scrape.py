# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us
import json

website = "myrustybucket.com"
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

    search_url = "https://www.myrustybucket.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    gmap = json.loads(
        stores_req.text.split("jQuery.extend(Drupal.settings, ")[1]
        .strip()
        .split("}});")[0]
        .strip()
        + "}}"
    )["gmap"]

    stores = stores_sel.xpath(
        '//div[@class="locations"]/div/div[@class="view-content"]/div[contains(@class,"views-row views-row-")]'
    )

    store_dict = {}
    for store in stores:
        address = store.xpath(
            './/div[@class="store-details-collapse-container"]/div[3]/text()'
        )
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        store_number = (
            "".join(
                store.xpath(
                    './/a[@class="gtm-set-my-bucket-link btn btn-set-bucket"]/@href'
                )
            )
            .strip()
            .replace("?store=", "")
            .strip()
        )

        add_list.append(store_number)

        tel = "".join(
            store.xpath(
                'div[@class="store-ordering-group"]/a[contains(@href,"tel:")]/text()'
            )
        ).strip()
        store_dict[tel] = add_list

    for key, value in gmap.items():
        markers = gmap[key]["markers"]
        for marker in markers:
            store_sel = lxml.html.fromstring(marker["text"])
            page_url = search_url
            locator_domain = website

            location_name = "".join(
                store_sel.xpath('//h5/span[@class="heading-7"]/text()')
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            street_address = ""
            city = ""
            state = ""
            zip = ""
            store_number = ""
            phone = "".join(
                store_sel.xpath('//a[contains(@href,"tel:")]/text()')
            ).strip()

            if phone in store_dict:
                add_list = store_dict[phone]
                store_number = add_list[-1].strip()

                street_address = add_list[0].strip()
                city = add_list[1].split(",")[0].strip()
                state = add_list[1].split(",")[1].strip().split(" ")[0].strip()
                zip = add_list[1].split(",")[1].strip().split(" ")[-1].strip()

            country_code = "<MISSING>"
            if us.states.lookup(state):
                country_code = "US"

            if store_number == "":
                store_number = "<MISSING>"

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if zip == "":
                zip = "<MISSING>"

            location_type = "<MISSING>"

            hours_of_operation = ""
            hours_list = []
            try:
                hours_sel = lxml.html.fromstring(
                    marker["text"].split("<h5>Hours</h5>")[1].strip()
                )
                hours = hours_sel.xpath("p")
                for hour in hours:
                    if (
                        "happy hour"
                        not in "".join(hour.xpath(".//text()")).strip().lower()
                    ):
                        if len("".join(hour.xpath(".//text()")).strip()) > 0:
                            hours_list.append("".join(hour.xpath(".//text()")).strip())
            except:
                pass
            hours_of_operation = "; ".join(hours_list).strip()
            latitude = marker["latitude"]
            longitude = marker["longitude"]

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
