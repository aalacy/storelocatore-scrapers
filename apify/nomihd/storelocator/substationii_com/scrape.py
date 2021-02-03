# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html

website = "substationii.com"
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

    search_url = "https://substationii.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="col-sm-6 single"]/b/a/@href')

    latlng_dict = {}
    latlng_list = stores_req.text.split("var myLatLng")
    for index in range(1, len(latlng_list)):
        ID = latlng_list[index].split("=")[0].strip()
        if ID not in latlng_dict:
            latlng_dict[ID] = (
                latlng_list[index].split("lat:")[1].strip().split(",")[0].strip()
                + ","
                + latlng_list[index].split("lng:")[1].strip().split("}")[0].strip()
            )

    new_lat_lng_dict = {}
    latlng_list = stores_req.text.split("var marker = new google.maps.Marker(")
    for index in range(1, len(latlng_list)):
        position = (
            latlng_list[index]
            .split("position:")[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace("myLatLng", "")
            .strip()
        )

        ID = (
            latlng_list[index]
            .split("title: '")[1]
            .strip()
            .split("-")[1]
            .strip()
            .split("'")[0]
            .strip()
        )

        if ID not in new_lat_lng_dict:
            if position in latlng_dict:
                new_lat_lng_dict[ID] = latlng_dict[position]

    for store_url in stores:
        page_url = "https://substationii.com/locations/" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//div[@class="col-sm-5"]/h7/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        street_address = "".join(
            store_sel.xpath('//div[@class="col-sm-5"]/text()[2]')
        ).strip()

        city_state_zip = "".join(
            store_sel.xpath('//div[@class="col-sm-5"]/text()[3]')
        ).strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ")[-1].strip()

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

        store_number = page_url.split("?location=")[1].strip()
        phone = (
            "".join(
                store_sel.xpath('//div[@class="col-sm-5"]/b[@class="element"]/text()')
            )
            .strip()
            .replace("-", ".")
            .strip()
            .replace("(", "")
            .replace(")", "")
            .strip()
        )

        location_type = "<MISSING>"

        latitude = ""
        longitude = ""
        if phone in new_lat_lng_dict:
            latitude = new_lat_lng_dict[phone].split(",")[0].strip()
            longitude = new_lat_lng_dict[phone].split(",")[1].strip()

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = "<MISSING>"

        hours = "\n".join(store_sel.xpath('//div[@class="col-sm-5"]//text()')).strip()
        try:
            hours = hours.split("Hours:")[1].strip().split("Owner")[0].strip()

        except:
            pass

        try:
            hours = hours.split("About")[0].strip()

        except:
            pass

        try:
            hours = hours.split("HOLIDAY")[0].strip()

        except:
            pass

        hours_of_operation = (
            "; ".join(hours.split("\n"))
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "")
            .strip()
        )

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
