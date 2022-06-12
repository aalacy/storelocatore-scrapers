# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "rosatispizza.com"
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

    search_url = "https://www.rosatispizza.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores = (
        stores_req.text.split("var locations = [")[1].strip().split("},];")[0].strip()
        + "},"
    )
    stores = stores.split("{")
    for index in range(1, len(stores)):
        store_data = stores[index].split("},")[0].strip()
        locator_domain = website
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        store_number = (
            store_data.split('"id":')[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace('"', "")
            .strip()
        )
        location_name = (
            store_data.split('"name":')[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace('"', "")
            .strip()
        )
        location_type = (
            store_data.split('"comingSoon":')[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace('"', "")
            .strip()
        )

        address = (
            store_data.split('"fulladdr":')[1]
            .strip()
            .split('",')[0]
            .strip()
            .replace('"', "")
            .strip()
            .split(",")
        )
        add_list = []
        for add in address:
            if len("".join(add)) > 0:
                add_list.append("".join(add).strip())

        street_address = ""
        city = ""
        state = ""
        zip = ""
        if len(add_list) == 3:
            street_address = add_list[0]
            city = add_list[-2].strip()
            state = add_list[-1].split(" ")[0].strip()
            zip = add_list[-1].split(" ")[-1].strip()
        elif len(add_list) == 4:
            street_address = ", ".join(add_list[:-2]).strip()
            city = add_list[-2].strip()
            state = add_list[-1].split(" ")[0].strip()
            zip = add_list[-1].split(" ")[-1].strip()
        elif len(add_list) == 2:
            street_address = add_list[0]
            city = " ".join(add_list[-1].split(" ")[:-2]).strip()
            state = add_list[-1].split(" ")[-2].strip()
            zip = add_list[-1].split(" ")[-1].strip()

        if "suite" in city.lower():
            street_address = (
                street_address + ", " + " ".join(city.split(" ")[:2]).strip()
            )
            city = " ".join(city.split(" ")[2:]).strip()

        if zip.isdigit() is not True:
            zip = "<MISSING>"

        phone = (
            store_data.split('"phone":')[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace('"', "")
            .strip()
        )
        if phone == "000-000-0000":
            phone = "<MISSING>"

        page_url = (
            store_data.split('"permalink":')[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace('"', "")
            .strip()
        )

        if location_type == "1":
            location_type = "COMING SOON"
            phone = "<MISSING>"

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        hours = store_sel.xpath('//div[@class="hours"]/text()')
        hours_list = []
        for hour in hours:
            if (
                len("".join(hour).strip()) > 0
                and "Bar Open Late For Sporting Events!" not in hour
                and "NOW OPEN!" not in hour
            ):
                hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()

        if store_number == "":
            store_number = "<MISSING>"

        if location_name == "":
            location_name = "<MISSING>"

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

        if phone == "" or phone is None:
            phone = "<MISSING>"

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if location_type == "":
            location_type = "<MISSING>"

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
