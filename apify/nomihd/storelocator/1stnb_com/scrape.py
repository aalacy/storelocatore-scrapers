# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "1stnb.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "referer": "http://validate.perfdrive.com/",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
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

    url = (
        "https://www.1stnb.com/locator?field_locator_type_tid[]=21"
        "&field_city_value=&field_state_tid=All&field_zip_code_value=&page=0"
    )
    while True:
        stores_req = session.get(url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath("//table/tbody/tr/td[1]/strong/a/@href")
        for store in stores:
            page_url = "https://www.1stnb.com" + store
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//h2[@class="node-title"]/text()')
            ).strip()

            street_address = "".join(
                store_sel.xpath(
                    '//div[@class="section field field-name-field-'
                    "address field-type-text "
                    'field-label-hidden"]/div[1]/div[1]/text()'
                )
            ).strip()
            city = "".join(
                store_sel.xpath(
                    '//div[@class="section field field-name-field-'
                    "city field-type-text "
                    'field-label-hidden"]/div[1]/div[1]/text()'
                )
            ).strip()
            state = "".join(
                store_sel.xpath(
                    '//div[@class="field field-name-field-state '
                    "field-type-taxonomy-term-reference field-label-hidden "
                    'clearfix"]/ul/li/text()'
                )
            ).strip()
            zip = "".join(
                store_sel.xpath(
                    '//div[@class="section field field-name-field-'
                    "zip-code field-type-text "
                    'field-label-hidden"]/div[1]/div[1]/text()'
                )
            ).strip()

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if len(zip) <= 0:
                zip = "".join(
                    store_sel.xpath('//span[@itemprop="postalCode"]/text()')
                ).strip()

            if zip == "":
                zip = "<MISSING>"

            country_code = ""
            if us.states.lookup(state):
                country_code = "US"

            if country_code == "":
                country_code = "<MISSING>"

            store_number = "<MISSING>"
            phone = "<MISSING>"

            location_type = "Branch"
            hours = store_sel.xpath(
                '//div[@class="section field '
                "field-name-field-operating-hours field-type-text-"
                "long "
                'field-label-above"]/div[1]/div[1]/p/text()'
            )

            final_hours = []
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    final_hours.append(
                        "".join(hour).strip().replace("\xa0", "").strip()
                    )
            hours_of_operation = " ".join(final_hours)

            map_link = "".join(
                store_sel.xpath('//div[@class="location map-link"]/a/@href')
            ).strip()

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            if map_link:
                latitude = map_link.split("?q=")[1].strip().split("+")[0].strip()
                longitude = (
                    map_link.split("?q=")[1]
                    .strip()
                    .split("+", 1)[1]
                    .strip()
                    .split("+")[0]
                    .strip()
                )

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
        next_page = "".join(stores_sel.xpath('//li[@class="pager-next last"]/a/@href'))
        if len(next_page) > 0:
            url = "https://www.1stnb.com" + next_page
        else:
            break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
