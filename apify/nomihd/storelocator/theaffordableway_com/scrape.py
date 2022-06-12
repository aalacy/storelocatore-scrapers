# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html

website = "theaffordableway.com"
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

    search_url = "https://www.theaffordableway.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="store"]')

    data_list = []
    latlng_list = stores_req.text.split("latlng = new google.maps.LatLng(")
    for index in range(1, len(latlng_list)):

        lat = latlng_list[index].split(",")[0].strip()
        lng = latlng_list[index].split(",")[1].strip().split(")")[0].strip()
        info_sel = lxml.html.fromstring(
            latlng_list[index].split("var infoWindowText = ")[1].strip()
        )

        temp_address = "".join(
            info_sel.xpath('//span[@class="mapstorename"]/text()')
        ).strip()
        data_list.append(lat + "|" + lng + "|" + temp_address)

    for index in range(0, len(stores)):
        page_url = search_url

        locator_domain = website
        location_name = "".join(stores[index].xpath("h3/text()")).strip()
        if location_name == "":
            location_name = "<MISSING>"
        street_address = data_list[index].split("|")[-1].strip()

        city = location_name.split(",")[0].strip()
        state = location_name.split(",")[1].strip()
        zip = data_list[index].split("|")[-1].strip().split(" ")[-1].strip()

        street_address = (
            street_address.replace(city + ",", "")
            .replace(state, "")
            .replace(zip, "")
            .strip()
        )

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
        phone = "".join(
            stores[index].xpath('h4/a[contains(@href,"tel:")]/text()')
        ).strip()

        location_type = "<MISSING>"

        latitude = ""
        longitude = ""
        latitude = data_list[index].split("|")[0].strip()
        longitude = data_list[index].split("|")[1].strip()

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = "<MISSING>"

        hours_of_operation = "".join(stores[index].xpath("p[3]/text()")).strip()

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
