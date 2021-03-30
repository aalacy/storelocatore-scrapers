# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json
import usaddress

website = "peiwei.com"
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

    search_url = "https://www.peiwei.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(
        stores_req.text.split("const locations=")[1]
        .strip()
        .split("</script>")[0]
        .strip()
    )
    for store in stores:
        page_url = store["link"]
        locator_domain = website
        location_name = store["title"].replace("&#8211;", "-").strip()
        if location_name == "":
            location_name = "<MISSING>"

        address = store["address"]
        parsed_address = usaddress.parse(address)
        city = ""
        state = ""
        zip = ""
        for index, tuple in enumerate(parsed_address):
            if tuple[1] == "PlaceName":
                city = city + tuple[0].strip() + " "
            if tuple[1] == "StateName":
                state = tuple[0].replace(",", "").strip()
            if tuple[1] == "ZipCode":
                zip = tuple[0].replace(",", "").strip()

        city = city.strip()
        street_address = address.split(",")[0].strip() + ","
        street_address = street_address.replace(city, "").strip()
        city = city.replace(",", "").strip()
        country_code = "US"

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        if country_code == "":
            country_code = "<MISSING>"

        store_number = str(store["id"])
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_type = "<MISSING>"

        hours_of_operation = ""
        hours = store_sel.xpath('//div[@class="hours-table"]/table/tbody/tr')
        for hour in hours:
            day = "".join(hour.xpath("td[1]/text()")).strip()
            time = "".join(hour.xpath("td[2]/text()")).strip()
            hours_of_operation = hours_of_operation + day + ":" + time + " "

        hours_of_operation = hours_of_operation.strip()
        if "Temporarily Closed" in hours_of_operation:
            hours_of_operation = "<MISSING>"
            location_type = "Temporarily Closed"

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
