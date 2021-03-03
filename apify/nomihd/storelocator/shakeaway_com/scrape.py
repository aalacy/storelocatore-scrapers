# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape import sgpostal as parser

website = "shakeaway.com"
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
                "raw_address",
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
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[7].strip(),
                row[9].strip(),
                row[11].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)

        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    loc_list = []

    search_url = "https://www.shakeaway.com/index.php/all-stores/item/bournemouth"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="customuk_title"]/form/select/option[position()>1]/@value'
    )
    for store in stores:
        if "#" == store:
            break

        page_url = "https://www.shakeaway.com/index.php/all-stores/item/" + store
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//h1[@class="pos-title"]/text()')
        ).strip()

        if location_name == "":
            location_name = "<MISSING>"

        sections = store_sel.xpath("//p")

        raw_address = ""
        phone = ""
        for index in range(0, len(sections)):
            if "Address" in "".join(sections[index].xpath(".//text()")).strip():
                raw_address = " ".join(sections[index + 1].xpath("span/text()")).strip()
                if len(raw_address) <= 0:
                    raw_address = " ".join(sections[index + 1].xpath("text()")).strip()
                    if len(raw_address) <= 0:
                        raw_address = " ".join(
                            sections[index + 1].xpath("span/span/text()")
                        ).strip()
            if "Phone Number" in "".join(sections[index].xpath(".//text()")).strip():
                phone = "".join(sections[index + 1].xpath("span/text()")).strip()
                if phone == "TBC":
                    phone = ""

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = formatted_addr.country

        if country_code == "" or country_code is None:
            country_code = "<MISSING>"

        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        location_type = "<MISSING>"
        if "our stores are temporarily closed" in store_req.text:
            location_type = "temporarily closed"

        store_number = "<MISSING>"
        hours = store_sel.xpath("//table//tr/td[1]/p[2]/span")
        hours_list = []
        if len(hours) > 0:
            for hour in hours:
                hours_list.append(
                    "".join(hour.xpath(".//text()")).strip().replace(" - ", ":").strip()
                )
        else:
            hours = store_sel.xpath("//table//tr/td[1]/p[2]/text()")
            for hour in hours:
                hours_list.append("".join(hour).strip())

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
        ).strip()
        if len(map_link) > 0:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"

        curr_list = [
            locator_domain,
            page_url,
            location_name,
            raw_address,
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
