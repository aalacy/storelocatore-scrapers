# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "leonardusa.com"
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
    loc_list = []

    locations_resp = session.get(
        "https://www.leonardusa.com/sitemap-xml.xml",
        headers=headers,
    )
    stores = locations_resp.text.split("<loc>")
    for index in range(1, len(stores)):
        locator_domain = website
        page_url = stores[index].split("</loc>")[0].strip()

        if "https://www.leonardusa.com/preowned-" in page_url:
            page_url = page_url.replace("preowned-", "").strip()
            store_resp = session.get(
                page_url,
                headers=headers,
            )
            store_sel = lxml.html.fromstring(store_resp.text)

            location_name = "".join(
                store_sel.xpath(
                    '//div[@class="direction-content"]//div[@class="row mb-lg-2 mb-1"]/div/h2/text()'
                )
            ).strip()
            if len(location_name) > 0:
                address = "".join(
                    store_sel.xpath(
                        '//div[@class="row align-items-center mb-lg-2 mb-1"]//p[@class="font-weight-bold mb-0"]/text()'
                    )
                ).strip()

                street_address = address.split(",")[0].strip()
                city = location_name.split(",")[0].strip()
                state = location_name.split(",")[1].strip()

                zip = address.split(",")[-1].strip().split(" ")[-1].strip()

                location_type = "<MISSING>"

                latitude = "<MISSING>"
                longitude = "<MISSING>"

                if us.states.lookup(state):
                    country_code = "US"
                else:
                    country_code = "CA"

                if country_code == "":
                    country_code = "<MISSING>"

                store_number = "<MISSING>"
                phone = "".join(
                    store_sel.xpath(
                        '//div[@class="row align-items-center mb-lg-5 mb-2"]//p[@class="font-weight-bold mb-0"]/text()'
                    )
                ).strip()
                if phone == "":
                    phone = "<MISSING>"

                hours = store_sel.xpath('//div[@class="store-item"]')
                hours_list = []
                for hour in hours:
                    day = "".join(
                        hour.xpath('div[@class="row"]/div[1]/p/text()')
                    ).strip()
                    hour = "".join(
                        hour.xpath('div[@class="row"]/div[2]/p/text()')
                    ).strip()
                    hours_list.append(day + ":" + hour)

                hours_of_operation = "; ".join(hours_list).strip()

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
