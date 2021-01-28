# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "springcreekbarbeque.com"
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

    search_url = "https://www.springcreekbarbeque.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="slide"]/div/a/@href')

    for store_url in stores:
        if "http" not in store_url:
            page_url = "https://www.springcreekbarbeque.com" + store_url
            locator_domain = website
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            location_name = (
                "".join(store_sel.xpath('//meta[@itemprop="name"]/@content'))
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )
            if location_name == "":
                location_name = "<MISSING>"

            street_address = ""
            city = ""
            state = ""
            zip = ""
            country_code = "<MISSING>"
            address = "".join(
                store_sel.xpath('//a[contains(@href,"maps/place/")]/@href')
            ).strip()
            if "/maps/place/" in address:
                address = (
                    address.split("/maps/place/")[1]
                    .strip()
                    .split("/")[0]
                    .strip()
                    .replace("+", " ")
                    .strip()
                )
                if "Spring Creek Barbeque" not in address:
                    street_address = address.split(",")[0].strip()
                    city = address.split(",")[1].strip()
                    state = address.split(",")[2].strip().split(" ")[0].strip()
                    zip = address.split(",")[2].strip().split(" ")[1].strip()
                    if us.states.lookup(state):
                        country_code = "US"

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if zip == "":
                zip = "<MISSING>"

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath('//a[contains(@href,"tel:")]/text()')
            ).strip()

            location_type = "<MISSING>"
            hours = store_sel.xpath(
                "//main/section[2]/div/div/div/div/div[3]/div[1]/div/div/p"
            ) + store_sel.xpath(
                "//main/section[2]/div/div/div/div/div[3]/div[2]/div/div/p"
            )

            hours_of_operation = ""
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("text()")).strip()
                time = "".join(hour.xpath("strong/text()")).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = " ".join(hours_list).strip()

            latitude = ""
            longitude = ""
            map_link = "".join(
                store_sel.xpath('//a[contains(@href,"maps/place/")]/@href')
            ).strip()

            if "/@" in map_link:
                latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                longitude = map_link.split("/@")[1].strip().split(",")[1].strip()

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
