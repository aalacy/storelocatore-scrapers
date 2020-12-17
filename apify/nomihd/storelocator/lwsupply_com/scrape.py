# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "lwsupply.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
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

    search_url = "https://lwsupply.com/locations-map/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="col-sm-12 col-md-4 col-lg-3"]')
    for store in stores:
        page_url = "".join(store.xpath(".//strong/a/@href")).strip()
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//h1[@class="page-title"]/text()')
        ).strip()

        address = store_sel.xpath('//div[@class="content-text-block"]')
        for add in address:
            if "address-block" in "".join(add.xpath("div/@class")).strip():
                temp_text = add.xpath('div[@class="address-block"]/text()')
                raw_text = []
                for t in temp_text:
                    if len("".join(t.strip())) > 0:
                        raw_text.append("".join(t.strip()))

                street_address = raw_text[0].strip()
                city_state_zip = raw_text[1]
                city = city_state_zip.split(",")[0].strip()
                state = city_state_zip.split(",")[1].strip().rsplit(" ", 1)[0].strip()
                zip = city_state_zip.split(",")[1].strip().rsplit(" ", 1)[1].strip()

                if street_address == "":
                    street_address = "<MISSING>"

                if city == "":
                    city = "<MISSING>"

                if state == "":
                    state = "<MISSING>"

                if zip == "":
                    zip = "<MISSING>"

                if us.states.lookup(state):
                    country_code = "US"

                if country_code == "":
                    country_code = "<MISSING>"

                store_number = "<MISSING>"
                phone = "".join(add.xpath('div[@class="address-block"]/a/text()'))

                location_type = "<MISSING>"
                hours_of_operation = (
                    " ".join(add.xpath("p[1]//text()"))
                    .strip()
                    .replace("\xa0", "")
                    .strip()
                    .encode("ascii", errors="replace")
                    .decode()
                    .replace("?", "-")
                    .strip()
                    .replace("\n", "")
                    .strip()
                )
                latitude = (
                    store_req.text.split("lat: ")[1].strip().split(",")[0].strip()
                )

                longitude = (
                    store_req.text.split("lng: ")[1].strip().split("}")[0].strip()
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
