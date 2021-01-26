# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html

website = "emeraldcitysmoothie.com"
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

    search_url = "https://www.emeraldcitysmoothie.com/directory/category/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[contains(text(),"More details")]/@href')

    for store_url in stores:
        page_url = "https://www.emeraldcitysmoothie.com" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//h1[@class="member_title"]/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        address = store_sel.xpath('//div[@class="member_address"]/text()')
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = ", ".join(add_list[:-1]).strip()

        city_state_zip = add_list[-1].strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ")[-1].strip()

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        if state.isdigit():
            state = "<MISSING>"
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
        phone = "<MISSING>"
        try:
            phone = (
                store_req.text.split("</div>Phone<")[0].strip().rsplit(">")[-1].strip()
            )
        except:
            pass

        location_type = "<MISSING>"

        latitude = (
            store_req.text.split("google.maps.LatLng(")[1].strip().split(",")[0].strip()
        )
        longitude = (
            store_req.text.split("google.maps.LatLng(")[1]
            .strip()
            .split(",")[1]
            .strip()
            .split(")")[0]
            .strip()
        )

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = "<MISSING>"
        hours = store_sel.xpath('//span[@class="custom_field_values Hours"]/text()')
        hours_list = []
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()

        if hours_of_operation == "":
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
