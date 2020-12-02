# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html
import us

website = "childtime.com"
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
        "https://www.childtime.com/sitemaps/www-childtime-com-schools.xml/",
        headers=headers,
    )
    stores = locations_resp.text.split("<loc>")
    for index in range(1, len(stores)):
        page_url = stores[index].split("</loc>")[0].strip()

        store_resp = session.get(
            page_url,
            headers=headers,
        )
        store_sel = lxml.html.fromstring(store_resp.text)

        json_temp = store_sel.xpath('//script[@type="application/ld+json"]/text()')
        if len(json_temp) > 0:
            json_temp = json_temp[0]

            store_json = json.loads(json_temp)

            location_name = store_json["name"]
            street_address = store_json["address"]["streetAddress"]
            city = store_json["address"]["addressLocality"]
            state = store_json["address"]["addressRegion"]

            zip = store_json["address"]["postalCode"]

            if location_type == "":
                location_type = "<MISSING>"

            latitude = "".join(
                store_sel.xpath(
                    '//a[@class="show-map"]' '/span[@class="addr"]/@data-latitude'
                )
            )
            longitude = "".join(
                store_sel.xpath(
                    '//a[@class="show-map"]' '/span[@class="addr"]/@data-longitude'
                )
            )

            if us.states.lookup(state):
                country_code = "US"
            else:
                country_code = "CA"

            if country_code == "":
                country_code = "<MISSING>"

            store_number = "".join(
                store_sel.xpath('//div[@class="school-info"]' "/@data-school-id")
            ).strip()
            phone = "".join(
                store_sel.xpath('//span[@class="localPhone"]/text()')
            ).strip()
            if phone == "":
                phone = "<MISSING>"

            hours_of_operation = store_json["openingHours"]

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
            # break
        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
