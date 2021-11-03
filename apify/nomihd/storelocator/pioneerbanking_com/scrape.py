# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "pioneerbanking.com"
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

    search_url = "https://www.pioneerny.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    latlng_list = stores_req.text.split("pinLat = parseFloat('")
    latlng_dict = {}
    for index in range(1, len(latlng_list)):
        ID = latlng_list[index].split("number: ")[1].strip().split(",")[0].strip()
        lat = latlng_list[index].split("')")[0].strip()
        lng = (
            latlng_list[index]
            .split("pinLng = parseFloat('")[1]
            .strip()
            .split("')")[0]
            .strip()
        )
        latlng_dict[ID] = lat + "," + lng

    stores = stores_sel.xpath('//ul[@class="locator-listing list no-bullet"]/li')
    for store in stores:
        page_url = (
            "https://www.pioneerny.com"
            + "".join(store.xpath('div[@class="address left"]/h3/a/@href')).strip()
        )
        locator_domain = website

        location_name = "".join(
            store.xpath('div[@class="address left"]/h3/a/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        street_address = "".join(
            store.xpath('div[@class="address left"]/span[@class="street"]/text()')
        ).strip()
        city = "".join(
            store.xpath('div[@class="address left"]/span[@class="city"]/text()')
        ).strip()
        state_zip = (
            "".join(store.xpath('div[@class="address left"]/text()'))
            .strip()
            .replace(",", "")
            .strip()
        )
        state = state_zip.split(" ")[0].strip()
        zip = state_zip.split(" ")[-1].strip()
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

        store_number = "".join(store.xpath("@data-id")).strip()
        phone = "".join(
            store.xpath('div[@class="address left"]/span[@class="phone"]/text()')
        ).strip()
        location_type = "<MISSING>"
        try:
            location_type = location_name.split("-")[1].strip()
        except:
            pass

        hours_of_operation = ""
        hours_list = []
        extra_info = store.xpath('div[@class="extra-info left"]/p')
        for ext in extra_info:
            hours = ext.xpath("text()")
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())

            if len(hours_list) > 0:
                break

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = ""
        longitude = ""
        if store_number in latlng_dict:
            latitude = latlng_dict[store_number].split(",")[0].strip()
            longitude = latlng_dict[store_number].split(",")[1].strip()

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"

        if (
            "This branch is permanently closed." not in hours_of_operation
            and "ATM Only" not in location_name
        ):
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
