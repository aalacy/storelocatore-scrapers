# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

website = "benbridge.com"
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

    countries = ["US", "CA"]
    for country in countries:
        search_url = "https://www.benbridge.com/jewelry-stores"
        search_req = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_req.text)
        post_url = "".join(
            search_sel.xpath('//form[@id="dwfrm_storelocator_countrylocator"]/@action')
        ).strip()

        data = {
            "dwfrm_storelocator_countryCode": "",
            "dwfrm_storelocator_country": country,
            "dwfrm_storelocator_findbycountry": "Search",
        }
        stores_req = session.post(post_url, data=data, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)

        stores = stores_sel.xpath('//a[@class="storedetail"]/@href')
        for store_url in stores:
            page_url = "https://www.benbridge.com" + store_url

            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = "".join(
                store_sel.xpath(
                    '//span[@class="c-section-contact-info__subheading"]/text()'
                )
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            address = store_sel.xpath(
                '//p[@class="c-section-contact-info__text"]/text()'
            )
            add_list = []
            for add in address:
                if len("".join(add).strip()) > 0:
                    add_list.append("".join(add).strip())

            street_address = add_list[0].strip()
            city = add_list[1].strip().split(",")[0].strip()
            state = add_list[1].strip().split(",")[1].strip().split(" ", 1)[0].strip()
            zip = add_list[1].strip().split(",")[1].strip().split(" ", 1)[1].strip()

            country_code = country

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if zip == "":
                zip = "<MISSING>"

            store_number = "".join(
                store_sel.xpath('//meta[@itemprop="branchCode"]/@content')
            ).strip()
            phone = "".join(
                store_sel.xpath('//meta[@itemprop="telephone"]/@content')
            ).strip()

            location_type = "<MISSING>"
            brands_list = store_sel.xpath(
                '//div[@class="store-brand-list"]/ul/li//text()'
            )

            if "Pandora" in brands_list:
                location_type = "PANDORA"

            hours = store_sel.xpath('//table[@class="store-hours"]/tr')
            hours_of_operation = ""
            for hour in hours:
                hours_of_operation = (
                    hours_of_operation
                    + "".join(hour.xpath('td[@class="day"]/text()')).strip()
                    + ":"
                    + "".join(hour.xpath('td[@class="time"]/text()')).strip()
                    + " "
                )

            hours_of_operation = hours_of_operation.strip()

            latitude = store_req.text.split("lat:")[1].strip().split(",")[0].strip()
            longitude = store_req.text.split("lng:")[1].strip().split("}")[0].strip()

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
