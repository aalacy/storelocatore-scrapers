# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

website = "premierinn.com"
domain = "https://www.premierinn.com/gb/en/"
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

    search_url = "https://www.premierinn.com/gb/en/hotels/england.html"
    counties_req = session.get(search_url, headers=headers)
    counties_sel = lxml.html.fromstring(counties_req.text)
    counties = counties_sel.xpath(
        '//ul[@class="pi-list pi-list--icon   push-double--bottom  "]/li/a'
    )

    done_url = []
    for county in counties:
        county_url = domain + "".join(county.xpath("@href")).strip()

        county = "".join(county.xpath("text()")).strip()

        stores_req = session.get(county_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//article[@class="seo-hotel-card"]')
        for store in stores:
            store_url = "".join(store.xpath("a/@href")).strip()
            if store_url == "https://www.premierinn.com/gb/en/hotels.html":
                # fetch from this page
                page_url = "<MISSING>"
                locator_domain = website
                location_name = "".join(
                    store.xpath('.//h3[@class="seo-hotel-card-title"]/text()')
                ).strip()

                if location_name == "":
                    location_name = "<MISSING>"

                address = "".join(
                    store.xpath('.//address[@itemprop="address"]/text()')
                ).strip()

                street_address = address.split("\n")[0].strip()

                city = "<MISSING>"
                state = county.replace("Hotels", "").strip()
                zip = address.split("\n")[1].strip()

                country_code = "GB"

                if street_address == "":
                    street_address = "<MISSING>"

                if city == "":
                    city = "<MISSING>"

                if state == "":
                    state = "<MISSING>"

                if zip == "":
                    zip = "<MISSING>"

                store_number = "<MISSING>"

                phone = "<MISSING>"
                location_type = "<MISSING>"
                hours_of_operation = "<MISSING>"

                latitude = "<MISSING>"
                longitude = "<MISSING>"

                hours_of_operation = "<MISSING>"

                if "https://www.premierinn.com/gb/en/hotels/england/" in page_url:

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
                if "https://www.premierinn.com" not in store_url:
                    page_url = domain + store_url
                else:
                    page_url = store_url

                locator_domain = website
                if page_url not in done_url:
                    done_url.append(page_url)
                    store_req = session.get(page_url, headers=headers)
                    store_sel = lxml.html.fromstring(store_req.text)

                    sub_stores = store_sel.xpath(
                        '//article[@class="seo-hotel-card"]/a/@href'
                    )

                    if len(sub_stores) > 0:
                        continue

                    location_name = "".join(
                        store_sel.xpath(
                            '//h1[@class="hotel-title__heading hotel-details__title"]/text()'
                        )
                    ).strip()
                    if location_name == "":
                        location_name = "<MISSING>"

                    street_address = "".join(
                        store_sel.xpath('//span[@itemprop="streetAddress"]/text()')
                    ).strip()
                    add_2 = "".join(
                        store_sel.xpath('//span[@itemprop="addressLocality"][1]/text()')
                    ).strip()
                    if len(add_2) > 0:
                        street_address = street_address + ", " + add_2

                    city = "".join(
                        store_sel.xpath('//span[@itemprop="addressLocality"][2]/text()')
                    ).strip()
                    state = county.replace("Hotels", "").strip()
                    zip = "".join(
                        store_sel.xpath('//span[@itemprop="postalCode"]/text()')
                    ).strip()

                    country_code = "GB"

                    if street_address == "":
                        street_address = "<MISSING>"

                    if city == "":
                        city = "<MISSING>"

                    if state == "":
                        state = "<MISSING>"

                    if zip == "":
                        zip = "<MISSING>"

                    store_number = "".join(
                        store_sel.xpath('//meta[@itemprop="hotelCode"]/@content')
                    ).strip()

                    if store_number == "":
                        store_number = "<MISSING>"

                    phone = "".join(
                        store_sel.xpath(
                            "//contact-module-responsive/@hotel-phone-number"
                        )
                    ).strip()
                    location_type = "<MISSING>"
                    hours_of_operation = "<MISSING>"

                    latitude = "".join(
                        store_sel.xpath(
                            '//div[@itemprop="geo"]/meta[@itemprop="latitude"]/@content'
                        )
                    ).strip()
                    longitude = "".join(
                        store_sel.xpath(
                            '//div[@itemprop="geo"]/meta[@itemprop="longitude"]/@content'
                        )
                    ).strip()

                    if latitude == "":
                        latitude = "<MISSING>"
                    if longitude == "":
                        longitude = "<MISSING>"

                    if hours_of_operation == "":
                        hours_of_operation = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"

                    if "https://www.premierinn.com/gb/en/hotels/england/" in page_url:
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
