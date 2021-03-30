# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html

website = "caferio.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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

    stores_req = session.get(
        "https://www.caferio.com/locations",
        headers=headers,
    )
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//li[@class="Location"]')
    for store in stores:
        locator_domain = website
        store_number = "".join(
            store.xpath('div[contains(@id,"location")]/button/@value')
        ).strip()
        page_url = "".join(store.xpath('div[contains(@id,"location")]/a/@href')).strip()
        s_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(s_req.text)
        location_name = "".join(store_sel.xpath("//div/h1/text()")).strip()
        temp_address = store_sel.xpath('//div[@class="Location-col"][1]/div[1]/text()')
        address_list = []
        for temp in temp_address:
            if len("".join(temp).strip()) > 0:
                address_list.append("".join(temp).strip())

        street_address = address_list[0].strip()
        city = address_list[1].split(",")[0].strip()
        state = address_list[1].split(",")[1].strip().split(" ")[0].strip()
        zip = address_list[1].split(",")[1].strip().split(" ")[1].strip()
        country_code = ""
        phone = ""
        location_type = ""
        latitude = s_req.text.split("latitude:")[1].strip().split(",")[0].strip()
        longitude = s_req.text.split("longitude:")[1].strip().split("}")[0].strip()

        phone = "".join(
            store_sel.xpath('//div[@class="Location-col"][1]/div[2]/text()')
        ).strip()
        if location_type == "":
            location_type = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"

        if us.states.lookup(state):
            country_code = "US"

        if country_code == "":
            country_code = "<MISSING>"

        hours_of_operation = ""
        days = store_sel.xpath('//div[@class="Location-days"]')
        hours = store_sel.xpath('//div[@class="Location-hours"]')

        for index in range(0, len(days)):
            day = "".join(days[index].xpath("text()")).strip()
            hour = "".join(hours[index].xpath("text()")).strip()
            hours_of_operation = hours_of_operation + day + hour + " "

        hours_of_operation = hours_of_operation.strip()
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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
