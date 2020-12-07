# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

website = "ezpawn.com"
domain = "https://stores.ezpawn.com/"
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


def get_selector(url):

    response = session.get(url, headers=headers)
    return lxml.html.fromstring(response.text)


def get_store_data(store_sel, page_url):

    locator_domain = website
    location_name = "".join(
        store_sel.xpath(
            '//span[@class="location-info-details-header-h1-display-address"]' "/text()"
        )
    ).strip()
    street_address = "".join(
        store_sel.xpath(
            '//div[@class="location-info-details-content"]'
            "/div[1]/div[1]"
            '//span[@class="c-address-street-1"]/text()'
        )
    ).strip()
    city = "".join(
        store_sel.xpath(
            '//div[@class="location-info-details-content"]'
            "/div[1]/div[1]"
            '//span[@class="c-address-city"]/span[1]/text()'
        )
    ).strip()

    state = "".join(
        store_sel.xpath(
            '//div[@class="location-info-details-content"]'
            "/div[1]/div[1]"
            '//abbr[@class="c-address-state"]/text()'
        )
    ).strip()

    zip = "".join(
        store_sel.xpath(
            '//div[@class="location-info-details-content"]'
            "/div[1]/div[1]"
            '//span[@class="c-address-postal-code"]/text()'
        )
    ).strip()

    country_code = "".join(
        store_sel.xpath(
            '//div[@class="location-info-details-content"]'
            "/div[1]/div[1]"
            '//abbr[@class="c-address-country-name c-address-country-us"]/text()'
        )
    ).strip()
    store_number = "<MISSING>"
    phone = "".join(
        store_sel.xpath(
            '//div[@class="location-info-details-content"]'
            '//span[@itemprop="telephone"]/text()'
        )
    ).strip()
    location_type = "".join(
        store_sel.xpath(
            '//span[@class="location-info-details-header-h1-brand-name"]/text()'
        )
    ).strip()

    if location_type == "":
        location_type = "<MISSING>"

    latitude = "".join(
        store_sel.xpath(
            '//div[@class="location-info-details-content"]'
            '//meta[@itemprop="latitude"]/@content'
        )
    ).strip()
    longitude = "".join(
        store_sel.xpath(
            '//div[@class="location-info-details-content"]'
            '//meta[@itemprop="longitude"]/@content'
        )
    ).strip()
    hours_of_operation = " ".join(
        store_sel.xpath(
            '//div[@class="location-info-details-content"]'
            '//table[@class="c-location-hours-details"][1]'
            "/tbody/tr//text()"
        )
    ).strip()

    if hours_of_operation == "":
        hours_of_operation = "<MISSING>"

    if street_address == "":
        street_address = "<MISSING>"

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

    return curr_list


def fetch_data():
    # Your scraper here
    loc_list = []

    states_sel = get_selector("https://stores.ezpawn.com/index.html")
    states = states_sel.xpath('//a[@class="c-directory-list-content-item-link"]')
    for state in states:
        if (
            "".join(
                state.xpath(
                    'span[@class="c-directory-list-content-item-count"]' "/text()"
                )
            ).strip()
            == "(1)"
        ):
            store_url = "".join(state.xpath("@href")).strip()
            store_sel = get_selector(domain + store_url)
            curr_list = get_store_data(store_sel, store_url)
            loc_list.append(curr_list)

        else:
            state_url = "".join(state.xpath("@href")).strip()
            cities_sel = get_selector(domain + state_url)
            cities = cities_sel.xpath(
                '//a[@class="c-directory-list-content-item-link"]'
            )

            for city in cities:
                if (
                    "".join(
                        city.xpath(
                            'span[@class="c-directory-list-content-item-count"]'
                            "/text()"
                        )
                    ).strip()
                    == "(1)"
                ):
                    stores = ["".join(city.xpath("@href")).strip()]
                else:
                    city_url = "".join(city.xpath("@href")).strip()
                    stores_sel = get_selector(domain + city_url)
                    stores = stores_sel.xpath(
                        '//div[@class="c-location-grid-item-link-wrapper"]/a[1]/@href'
                    )

                for store_url in stores:
                    page_url = domain + store_url.replace("../", "").strip()
                    store_sel = get_selector(page_url)
                    curr_list = get_store_data(store_sel, page_url)
                    loc_list.append(curr_list)

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
