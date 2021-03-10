# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "islandsrestaurants.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
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

    search_url = "https://www.islandsrestaurants.com/sitemap"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    sitemap_sections = stores_sel.xpath(
        '//div[@class="col-12 col-md-4"]/ul[@class="sitemap"]'
    )
    for sec in sitemap_sections:
        if "Locations" in "".join(sec.xpath("li[1]/h3/text()")).strip():
            stores = sec.xpath("li[position()>1]/a/@href")
            for store_url in stores:
                store_req = session.get(store_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                location_name = "".join(
                    store_sel.xpath('//div[@class="p-20"]/h2/text()')
                ).strip()
                if len(location_name) > 0:
                    log.info(store_url)
                    locator_domain = website
                    latitude = (
                        store_req.text.split("var lngLat = [")[1]
                        .strip()
                        .split(",")[1]
                        .split("]")[0]
                        .strip()
                    )
                    longitude = (
                        store_req.text.split("var lngLat = [")[1]
                        .strip()
                        .split(",")[0]
                        .strip()
                    )

                    store_number = "<MISSING>"
                    location_type = "".join(
                        store_sel.xpath('//div[@class="hours"]/p/strong/text()')
                    ).strip()

                    street_address = "".join(
                        store_sel.xpath(
                            '//div[@class="location"]/div[@class="address"]/text()'
                        )
                    ).strip()
                    city_state_zip = (
                        "".join(
                            store_sel.xpath(
                                '//div[@class="location"]/div[@class="city-state-zip"]/text()'
                            )
                        )
                        .strip()
                        .replace(",", "")
                        .split("\n")
                    )
                    city = city_state_zip[0].strip()
                    state = city_state_zip[1].strip()
                    zip = city_state_zip[2].strip()
                    phone = "".join(
                        store_sel.xpath('//span/a[@data-name="phone"]/text()')
                    ).strip()
                    hours = store_sel.xpath('//div[@class="hours"]/text()')
                    hours_list = []
                    for hour in hours:
                        if len("".join(hour).strip()) > 0:
                            hours_list.append(
                                ":".join("".join(hour).strip().split("\n"))
                            )

                    hours_of_operation = "; ".join(hours_list).strip()
                    page_url = store_url

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
                    # break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
