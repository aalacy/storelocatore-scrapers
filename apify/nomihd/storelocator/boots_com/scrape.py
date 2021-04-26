# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from tenacity import retry, stop_after_attempt

website = "boots.com"
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


@retry(stop=stop_after_attempt(5))
def get_page(page_url):
    session = SgRequests()
    return session.get(page_url, headers=headers)


def fetch_data():
    loc_list = []

    search_url = "https://www.boots.com/store-a-z"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="brand_list_viewer"]//ul/li/a/@href')

    for store_url in stores:
        page_url = "https://www.boots.com" + store_url
        log.info(page_url)
        locator_domain = website

        store_req = get_page(page_url)
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(
            store_sel.xpath('//h2[@class="store_name"]/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"
            continue

        sections = store_sel.xpath('//dl[@class="store_info_list"]')
        for sec in sections:
            if (
                "Address"
                in "".join(
                    sec.xpath('dt[@class="store_info_list_label"]/text()')
                ).strip()
            ):

                street_address = "".join(
                    sec.xpath('dd[@class="store_info_list_item"][1]/text()')
                ).strip()
                city = "".join(
                    sec.xpath('dd[@class="store_info_list_item"][2]/text()')
                ).strip()
                state = "".join(
                    sec.xpath('dd[@class="store_info_list_item"][3]/text()')
                ).strip()
                zip = "".join(
                    sec.xpath('dd[@class="store_info_list_item"][4]/text()')
                ).strip()
            break

        country_code = "".join(
            store_sel.xpath('//input[@id="storeCountryCode"]/@value')
        ).strip()

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        store_number = "".join(
            store_sel.xpath('//input[@name="bootsStoreId"]/@value')
        ).strip()
        phone = "".join(
            store_sel.xpath('//a[@name="Store telephone number"]/text()')
        ).strip()

        location_type = "<MISSING>"
        temp_hours = store_sel.xpath('//table[@class="store_opening_hours "]')
        hours_of_operation = ""
        hours_list = []
        for temp in temp_hours:
            if (
                "Store:"
                in "".join(
                    temp.xpath('thead/tr/th[@class="store_hours_heading"]/text()')
                ).strip()
            ):
                hours = temp.xpath("tbody/tr")
                for hour in hours:
                    day = "".join(
                        hour.xpath('td[@class="store_hours_day"]/text()')
                    ).strip()
                    time = "".join(
                        hour.xpath('td[@class="store_hours_time"]/text()')
                    ).strip()
                    hours_list.append(day + ":" + time)
                break

        hours_of_operation = ";".join(hours_list).strip()

        latitude = "".join(store_sel.xpath('//input[@id="lat"]/@value')).strip()
        longitude = "".join(store_sel.xpath('//input[@id="lon"]/@value')).strip()

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"

        if store_number != "":
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
