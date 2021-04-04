# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html
from sgselenium import SgChrome

website = "ruralking.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(retry_behavior=None, proxy_rotation_failure_threshold=0)
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
        driver.get("https://www.ruralking.com/storelocator/index/index?")
        stores_sel = lxml.html.fromstring(driver.page_source)
        stores = stores_sel.xpath(
            '//li[contains(@class,"show-tag-li store-item store-")]'
        )
        for store in stores:
            page_url = "".join(store.xpath('.//a[@class="title-store"]/@href')).strip()
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            if store_req.url == "https://www.ruralking.com/cms/noroute/":
                page_url = "<MISSING>"
                locator_domain = website
                location_name = "".join(
                    store.xpath('.//a[@class="title-store"]/text()')
                ).strip()

                if location_name == "":
                    location_name = "<MISSING>"

                address = store.xpath('.//p[@class="address-store"]/text()')
                street_address = "; ".join(address[:-1]).strip()
                city = address[-1].strip().split(",")[0].strip()
                state = address[-1].strip().split(",")[1].strip().split(" ")[0].strip()
                zip = address[-1].strip().split(",")[1].strip().split(" ")[1].strip()
                phone = "".join(
                    store.xpath('.//p[@class="phone-store"]/text()')
                ).strip()
                location_type = "<MISSING>"
                hours_of_operation = "".join(
                    store.xpath('.//p[@class="hours-store"]/text()')
                ).strip()
                latitude = "".join(store.xpath("@data-latitude")).strip()
                longitude = "".join(store.xpath("@data-longitude")).strip()
                country_code = "<MISSING>"
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

                store_number = "".join(store.xpath("@data-store-id")).strip()

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
            else:
                store_sel = lxml.html.fromstring(store_req.text)
                locator_domain = website
                location_name = "".join(
                    store_sel.xpath('//h3[@class="store-header__title"]/text()')
                ).strip()

                if location_name == "":
                    location_name = "<MISSING>"

                street_address = ""
                city = ""
                state = ""
                zip = ""
                phone = "".join(
                    store_sel.xpath('//div[@class="store-page-phone"]/a/text()')
                ).strip()
                location_type = "<MISSING>"
                hours_of_operation = ""
                latitude = ""
                longitude = ""
                try:
                    latitude = "".join(
                        store_req.text.split("google.maps.LatLng(")[1]
                        .strip()
                        .split(",")[0]
                        .strip()
                    ).strip()
                except:
                    pass

                try:
                    longitude = "".join(
                        store_req.text.split("google.maps.LatLng(")[1]
                        .strip()
                        .split(",")[1]
                        .strip()
                        .split(")")[0]
                        .strip()
                    ).strip()
                except:
                    pass

                details = store_sel.xpath('//div[@class="detail-box"]')
                for det in details:
                    if "address-label" in "".join(det.xpath("strong/@class")).strip():
                        street_address = "".join(
                            det.xpath('div[@class="detail-content"]/p[1]/text()')
                        ).strip()
                        city_state_zip = "".join(
                            det.xpath('div[@class="detail-content"]/p[2]/text()')
                        ).strip()

                        city = city_state_zip.split(",")[0].strip()
                        state = (
                            city_state_zip.split(",")[1].strip().split(" ")[0].strip()
                        )
                        zip = city_state_zip.split(",")[1].strip().split(" ")[1].strip()

                country_code = "<MISSING>"
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

                store_number = "".join(
                    store_sel.xpath(
                        '//button[@class="store-header__label store-'
                        'header__label--select-store"]/@data-store-number'
                    )
                ).strip()

                hours = store_sel.xpath('//ul[@class="store-hours-details"]/li')
                for hour in hours:
                    hours_of_operation = (
                        hours_of_operation
                        + "".join(hour.xpath("span/text()"))
                        .strip()
                        .replace(":", "")
                        .strip()
                        + ":"
                        + "".join(hour.xpath("td/text()")).strip()
                        + " "
                    )

                hours_of_operation = hours_of_operation.strip()

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

        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
