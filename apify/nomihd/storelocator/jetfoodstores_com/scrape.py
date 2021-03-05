# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "jetfoodstores.com"
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

    search_url = "https://www.jetfoodstores.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    coord_dict = {}
    markers = stores_sel.xpath('//div[@class="marker"]')
    for marker in markers:
        coord_dict["".join(marker.xpath("@data-loc-id")).strip()] = (
            "".join(marker.xpath("@data-lat")).strip()
            + ","
            + "".join(marker.xpath("@data-lng")).strip()
        )

    stores = stores_sel.xpath('//li[@class="location-listing"]')
    for store in stores:
        page_url = search_url

        locator_domain = website
        location_name = (
            "".join(store.xpath('span[@class="loc-address"]/strong/text()'))
            .strip()
            .replace(":", "")
            .strip()
        )
        if location_name == "":
            location_name = "<MISSING>"

        address = "".join(store.xpath('span[@class="loc-address"]/text()')).strip()

        street_address = address.split(",")[0].strip()
        city = ""
        state = ""
        zip = ""
        if len(address.split(",")) == 3:
            city = address.split(",")[-2].strip()
            state = address.split(",")[-1].strip()
        elif len(address.split(",")) == 2:
            city = address.split(" ")[-2].strip()
            state = address.split(" ")[-1].strip()
        else:
            if address.split(" ")[-1].isdigit():
                zip = address.split(" ")[-1].strip()
                state = address.split(" ")[-2].strip()
                city = address.split(" ")[-3].strip()
                street_address = " ".join(address.split(" ")[:-2]).strip()
            else:
                city = address.split(" ")[-2]
                state = address.split(" ")[-1]
                street_address = " ".join(address.split(" ")[:-2]).strip()

        if len(state.split(" ")) == 2:
            zip = state.split(" ")[-1].strip()
            state = state.split(" ")[0].strip()

        if zip.isdigit() is False:
            zip = "<MISSING>"

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

        if country_code == "" or country_code is None:
            country_code = "<MISSING>"

        store_number = "<MISSING>"
        if "#" in location_name:
            store_number = location_name.split("#")[1].strip().replace(":", "").strip()

        phone = "".join(
            store.xpath(
                'div[@class="all_fuel_prices_contain"]/div[1]/div[2]/a[contains(@href,"tel:")]/text()'
            )
        ).strip()

        location_type = (
            "".join(store.xpath('i[contains(@class,"loc_brand")][1]/@class'))
            .strip()
            .replace("loc_brand", "")
            .strip()
        )

        if location_type == "":
            location_type = "<MISSING>"

        ID = "".join(store.xpath("@data-loc-id")).strip()
        latitude = ""
        longitude = ""
        if ID in coord_dict:
            latitude = coord_dict[ID].split(",")[0].strip()
            longitude = coord_dict[ID].split(",")[1].strip()

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = "<MISSING>"

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
