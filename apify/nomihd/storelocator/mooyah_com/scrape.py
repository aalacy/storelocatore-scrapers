# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html

website = "mooyah.com"
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

    search_url = "https://www.mooyah.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = []
    stores = stores_sel.xpath('//div[@id="location0"]//h4/a/@href')
    international_stores = stores_sel.xpath(
        '//div[@id="location1"]//div[@class="l-block "]'
    )
    for st in international_stores:
        if "Canada" == "".join(st.xpath('h3[@class="l-location"]/text()')).strip():
            stores.append("".join(st.xpath("h4/a/@href")).strip())

    for store_url in stores:
        page_url = store_url
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//h1[@class="loc-title _fancy_title"]/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        temp_address = store_sel.xpath('//div[@class="locations-info li"]/text()')
        add_list = []
        for add in temp_address:
            if (
                len("".join(add).strip()) > 0
                and "United States" not in "".join(add).strip()
                and "Canada" not in "".join(add).strip()
            ):
                add_list.append("".join(add).strip())

        street_address = add_list[0].strip()
        if "Suite" in "".join(add_list).strip():
            street_address = street_address + ", " + add_list[1].strip()

        city_state_zip = add_list[-1].strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ", 1)[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ", 1)[1].strip()

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"
        else:
            country_code = "CA"

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        store_number = "<MISSING>"
        if "#" in location_name:
            store_number = location_name.split("#")[1].strip()
            if "(" in store_number:
                store_number = store_number.split("(")[0].strip()

        phone = "".join(store_sel.xpath('//div[@class="inline-phone"]/text()')).strip()

        location_type = "<MISSING>"
        hours = store_sel.xpath('//div[@class="hours li"]/p')
        hours_of_operation = ""
        for hour in hours:
            if "Curbside" in "".join(hour.xpath("text()")).strip():
                continue
            elif "Temporarily Closed" in "".join(hour.xpath("text()")).strip():
                location_type = "".join(hour.xpath("text()")).strip()
                continue
            else:
                hours_of_operation = (
                    hours_of_operation
                    + "".join(hour.xpath("text()")).strip()
                    + ":"
                    + "".join(hour.xpath("span/text()")).strip()
                    + " "
                )

        map_link = "".join(
            store_sel.xpath('//li[@class="get-directions"]/a/@href')
        ).strip()

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        try:
            latitude = map_link.split("destination=")[1].strip().split(",")[0].strip()
        except:
            pass

        try:
            longitude = (
                map_link.split("destination=")[1]
                .strip()
                .split(",")[1]
                .strip()
                .replace('"', "")
                .strip()
            )
        except:
            pass

        if latitude == "<MISSING>" or longitude == "<MISSING>":
            latitude = "<MISSING>"
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
