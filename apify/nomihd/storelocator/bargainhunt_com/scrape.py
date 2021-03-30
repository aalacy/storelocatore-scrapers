# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html
import ast

website = "bargainhunt.com"
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

    search_url = "https://www.bargainhunt.com/store-locator"
    stores_req = session.get(search_url, headers=headers)
    stores = ast.literal_eval(
        stores_req.text.split("var infoWindowContent = ")[1]
        .strip()
        .split(";")[0]
        .strip()
    )
    markers = ast.literal_eval(
        stores_req.text.split("var markers = ")[1].strip().split(";")[0].strip()
    )
    for index in range(0, len(stores)):
        store_sel = lxml.html.fromstring("".join(stores[index]))
        location_name = (
            "".join(store_sel.xpath('//div[@class="info_content"]/p/strong[1]/text()'))
            .strip()
            .replace(":", "")
            .strip()
        )
        page_url = "<MISSING>"
        locator_domain = website
        if location_name == "":
            location_name = "<MISSING>"

        street_address = "".join(
            store_sel.xpath('//div[@class="info_content"]/p/text()[1]')
        ).strip()

        city_state_zip = "".join(
            store_sel.xpath('//div[@class="info_content"]/p/text()[2]')
        ).strip()
        if ", " not in city_state_zip:
            city_state_zip = "".join(
                store_sel.xpath('//div[@class="info_content"]/p/text()[3]')
            ).strip()

            phone = "".join(
                store_sel.xpath('//div[@class="info_content"]/p/text()[4]')
            ).strip()
            hours_of_operation = "".join(
                store_sel.xpath('//div[@class="info_content"]/p/text()[6]')
            ).strip()
        else:
            phone = "".join(
                store_sel.xpath('//div[@class="info_content"]/p/text()[3]')
            ).strip()
            hours_of_operation = "".join(
                store_sel.xpath('//div[@class="info_content"]/p/text()[5]')
            ).strip()

        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ")[1].strip()

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

        location_type = "<MISSING>"

        latitude = "".join(str(markers[index])).split(",")[1].strip()
        longitude = (
            "".join(str(markers[index])).split(",")[2].strip().replace("]", "").strip()
        )

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        if phone == "":
            phone = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

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
