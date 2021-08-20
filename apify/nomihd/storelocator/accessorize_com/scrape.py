# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "accessorize.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.accessorize.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
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

    session.get("https://www.accessorize.com/")
    search_url = "https://www.accessorize.com/us/stores?country=GB"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@data-component="stores/storeDetails"]/@data-component-store'
    )
    for store in stores:
        store_data = json.loads(
            store.replace("&quot;", '"')
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .strip()
        )

        locator_domain = website
        latitude = store_data["latitude"]
        longitude = store_data["longitude"]
        store_number = store_data["ID"]
        location_name = store_data["name"]
        location_type = "<MISSING>"
        street_address = store_data["address1"]
        if store_data["address2"] is not None and len(store_data["address2"]) > 0:
            street_address = street_address + ", " + store_data["address2"]

        city = store_data["city"]
        if city is not None:
            city = city.strip()
        state = "<MISSING>"
        if "stateCode" in store_data:
            state = store_data["stateCode"].strip()
        zip = store_data["postalCode"]
        country_code = store_data["countryCode"]
        phone = store_data["phoneFormatted"]
        page_url = "<MISSING>"

        hours_sel = lxml.html.fromstring(store_data["workingHours"])
        hours = hours_sel.xpath(".//text()")
        hours_list = []
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                if "Opening hours:" not in hour:
                    hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()
        if store_number == "":
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

    """ US Stores """
    search_url = "https://www.accessorize.com/us/stores"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = (
        stores_sel.xpath('//table[@class="table b-stores-disabled__table"]')[-1]
        .xpath("tbody")[-1]
        .xpath("tr")
    )
    for store in stores:
        page_url = search_url
        locator_domain = website
        location_name = "".join(store.xpath("td[2]/text()")).strip()
        address = "".join(store.xpath("td[3]/text()")).strip()
        street_address = ", ".join(address.split(",")[:-3]).strip()
        city = address.split(",")[-3]
        state = address.split(",")[-2].strip().split(" ")[0].strip()
        zip = address.split(",")[-2].strip().split(" ")[-1].strip()
        country_code = "US"
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
