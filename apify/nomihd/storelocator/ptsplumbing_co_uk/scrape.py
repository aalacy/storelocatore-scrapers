# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

website = "ptsplumbing.co.uk"
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

    search_url = "https://www.cityplumbing.co.uk/branch-locator"
    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.text.split("stores.push(")
    for index in range(1, len(stores)):
        store_data = stores[index].split("});")[0].strip()

        locator_domain = website
        location_name = (
            store_data.split('description: "')[1].strip().split('",')[0].strip()
        )
        if location_name == "":
            location_name = "<MISSING>"

        store_sel = lxml.html.fromstring(
            store_data.split("popup:")[1]
            .strip()
            .replace("\\u003C", "<")
            .replace("\\u003E", ">")
            .strip()
            .replace("\\n", "")
            .replace("\\t", "")
            .replace('"<', "<")
            .replace('>"', ">")
            .strip()
            .replace('\\"', '"')
            .strip()
            .replace("\\/", "/")
            .strip()
        )

        add_list = []
        address = store_sel.xpath(
            '//div[@class="address"]/span[@class="section_info"]/ul/li/text()'
        )
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = " ".join(add_list[0:-2]).strip()
        city = ""
        if "," in add_list[-2]:
            city = add_list[-2].split(",")[1].strip()
            street_address = street_address + " " + address[-2].split(",")[0].strip()
        else:
            city = add_list[-2]

        state = "<MISSING>"
        zip = add_list[-1].strip()

        country_code = "GB"

        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        store_number = store_data.split('name: "')[1].strip().split('",')[0].strip()
        page_url = "https://www.cityplumbing.co.uk/branch/" + store_number

        location_type = "<MISSING>"

        phone = "".join(
            store_sel.xpath(
                '//div[@class="contact_details"]/span[@class="section_info"]/text()'
            )
        ).strip()
        hours_of_operation = ""
        hours = store_sel.xpath('//div[@class="opening_times"]/ul/li')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath('span[@class="wk_day"]/text()')).strip()
            time = "".join(hour.xpath('span[@class="times"]/text()')).strip()
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        latitude = store_data.split('latitude: "')[1].strip().split('",')[0].strip()
        longitude = store_data.split('longitude: "')[1].strip().split('",')[0].strip()
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
