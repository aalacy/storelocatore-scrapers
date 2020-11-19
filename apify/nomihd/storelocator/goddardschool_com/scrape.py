# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
import json
from sglogging import sglog
import lxml.html

website = "goddardschool.com"
domain = "https://www.goddardschool.com"
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
    locator_domain = website
    page_url = ""
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zip = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    loc_list = []

    locations_resp = session.get(
        "https://www.goddardschool.com/preschool-locations",
        headers=headers,
    )
    locations_sel = lxml.html.fromstring(locations_resp.text)
    state_links = locations_sel.xpath(
        '//div[@class="locations-list"]' "/div/strong/a/@href"
    )
    for state in state_links:
        state_url = domain + state.strip()
        state_resp = session.get(state_url, headers=headers)
        state_sel = lxml.html.fromstring(state_resp.text)

        city_links = state_sel.xpath(
            '//div[@class="locations-list"]' "//strong/a/@href"
        )
        for city in city_links:
            city_url = domain + city.strip()
            city_resp = session.get(city_url, headers=headers)
            city_sel = lxml.html.fromstring(city_resp.text)

            school_links = city_sel.xpath(
                '//div[@class="locations-list"]' "/div/address/strong/a/@href"
            )
            for school in school_links:
                page_url = domain + school
                school_resp = session.get(page_url, headers=headers)
                school_sel = lxml.html.fromstring(school_resp.text)

                location_name = "".join(
                    school_sel.xpath(
                        '//div[@class="desktop-school-header"]' "/h1/a/span/text()"
                    )
                ).strip()
                street_address = "".join(
                    school_sel.xpath(
                        '//div[@class="desktop-school-header-contact"]'
                        '/address/a/span[@itemprop="streetAddress"]/text()'
                    )
                ).strip()
                city = "".join(
                    school_sel.xpath(
                        '//div[@class="desktop-school-header-contact"]'
                        '/address/a/span[@itemprop="addressLocality"]/text()'
                    )
                ).strip()
                state = "".join(
                    school_sel.xpath(
                        '//div[@class="desktop-school-header-contact"]'
                        '/address/a/span[@itemprop="addressRegion"]/text()'
                    )
                ).strip()
                zip = "".join(
                    school_sel.xpath(
                        '//div[@class="desktop-school-header-contact"]'
                        '/address/a/span[@itemprop="postalCode"]/text()'
                    )
                ).strip()
                store_number = "".join(
                    school_sel.xpath(
                        '//div[@id="mobile-school-header"]'
                        '//span[@class="Location_Number"]/text()'
                    )
                ).strip()

                location_type = ""
                if location_type == "":
                    location_type = "<MISSING>"

                latitude = "".join(
                    school_sel.xpath('//meta[@itemprop="latitude"]/@content')
                ).strip()
                longitude = "".join(
                    school_sel.xpath('//meta[@itemprop="longitude"]/@content')
                ).strip()

                country_code = "US"
                if country_code == "":
                    country_code = "<MISSING>"

                phone = "".join(
                    school_sel.xpath(
                        '//div[@class="desktop-school-header-contact"]'
                        '/address/span[@itemprop="telephone"]//text()'
                    )
                ).strip()
                if phone == "":
                    phone = "<MISSING>"

                hours_of_operation = "".join(
                    school_sel.xpath(
                        '//div[@class="desktop-school-header-contact"]'
                        '//span[@itemprop="hours"]/text()'
                    )
                ).strip()
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
        #         break
        #     break
        # break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
