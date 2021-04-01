# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape import sgpostal as parser
import lxml.html

website = "mscdirect.com"
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

    search_url = "https://www.mscdirect.com/corporate/locations-branches"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    stores = stores_sel.xpath('//div[@class="state-div"]')
    for store in stores:
        Type = "".join(store.xpath("div/@class")).strip()
        location_type = "<MISSING>"
        if Type == "state-block customer-service ns-p":
            location_type = "customer-service"
        elif Type == "state-block customer-service-fulfillment ns-p":
            location_type = "customer-service-fulfillment"
        else:
            location_type = "branch"

        page_url = search_url

        location_name = "".join(store.xpath("div/strong/text()")).strip()

        locator_domain = website

        raw_info = store.xpath("div/text()")
        add_list = []
        for add in raw_info:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        phone = ""
        raw_address = ""
        for index in range(0, len(add_list)):
            if "Local:" in add_list[index]:
                phone = add_list[index]
                raw_address = ", ".join(add_list[:index])

            if "Toll-Free" in add_list[index]:
                phone = add_list[index]
                raw_address = ", ".join(add_list[:index])
            if "Customer Service:" in add_list[index]:
                phone = add_list[index]
                raw_address = ", ".join(add_list[:index])

            try:
                if "(" in add_list[index]:
                    if (
                        len(
                            "".join(
                                add_list[index]
                                .split(" ")[0]
                                .strip()
                                .replace("(", "")
                                .replace(")", "")
                                .strip()
                            )
                        )
                        == 3
                    ):
                        phone = add_list[index]
                        raw_address = ", ".join(add_list[:index])
            except:
                pass

        if len(raw_address) <= 0:
            raw_address = ", ".join(add_list).strip()

        phone = (
            phone.replace("Local:", "")
            .replace("Toll-Free", "")
            .replace("Customer Service:", "")
            .strip()
        )
        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = "US"

        street_address = (
            street_address.replace("Cardinal Point At Bayside ", "")
            .replace("Msc Metalworking Call Center ", "")
            .replace("Jefferson Business Center ", "")
            .replace("Portland North Business Park", "")
            .replace("Previously Deer Park Ny", "")
            .replace("Eastpointe Business Center ", "")
            .strip()
        )
        if city is None:
            city = location_name.split(",")[0].strip()
            street_address = street_address.replace(city, "").strip()

        hours_of_operation = "<MISSING>"
        store_number = "<MISSING>"

        if location_name == "":
            location_name = "<MISSING>"

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

        map_link = "".join(
            store.xpath('div/a[contains(text(),"Map and Directions")]/@href')
        ).strip()
        latitude = ""
        longitude = ""
        if len(map_link) > 0:
            if "/@" in map_link:
                latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                longitude = map_link.split("/@")[1].strip().split(",")[1]

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
        # break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
