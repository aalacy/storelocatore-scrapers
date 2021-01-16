# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html
from sgselenium import SgChrome

website = "gloriajeans.com"
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

    with SgChrome() as driver:
        driver.get("https://www.gloriajeans.com/pages/store-locator")
        stores_sel = lxml.html.fromstring(driver.page_source)
        stores = stores_sel.xpath('//div[@class="item thumbnail"]')
        for store in stores:
            page_url = "".join(
                store.xpath(
                    'div/div[@class="item-content"]/a[@class="linkdetailstore"]/@href'
                )
            ).strip()
            locator_domain = website
            location_name = "".join(
                store.xpath('div/div[@class="item-content"]/label/strong/text()')
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            address = "".join(
                store.xpath(
                    'div/div[@class="item-content"]/div[@class="address"]/text()'
                )
            ).strip()

            country_code = ""
            if "USA" in address or "United States" in address:
                country_code = "US"

            street_address = address.split(",")[0].strip()
            city = "<MISSING>"
            state = address.split(",")[-3].strip()
            zip = address.split(",")[-2].strip()
            phone = "".join(
                store.xpath(
                    'div/div[@class="item-content"]/a[contains(@href,"tel:")]/text()'
                )
            ).strip()

            location_type = "<MISSING>"

            if country_code == "":
                if us.states.lookup(state):
                    country_code = "US"

            if country_code == "":
                country_code = "<MISSING>"

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if zip == "":
                zip = "<MISSING>"

            store_number = "<MISSING>"

            if phone == "":
                phone = "<MISSING>"

            hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            if len(page_url) > 0:
                page_url = "https://www.gloriajeans.com" + page_url
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                latitude = store_req.text.split("lat:")[1].strip().split(",")[0].strip()
                longitude = (
                    store_req.text.split("lng:")[1].strip().split("}")[0].strip()
                )

                if latitude == "":
                    latitude = "<MISSING>"

                if longitude == "":
                    longitude = "<MISSING>"

                hours = store_sel.xpath('//table[@class="work-time table"]/tr')
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath('th[@class="dayname"]/text()')).strip()
                    time = "".join(hour.xpath("td/text()")).strip()
                    hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"

            else:
                page_url = "<MISSING>"

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
