# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

website = "clarks.co.uk"
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

    sitemap_url = "https://www.clarks.co.uk/sitemap.xml"
    sitemap_req = session.get(sitemap_url, headers=headers)
    urls = sitemap_req.text.split("<loc>")
    search_url = ""
    for index in range(1, len(urls)):
        url = urls[index].split("</loc>")[0].strip()
        if "Store-en-GB-GBP-" in url:
            search_url = url
            break

    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.text.split("<loc>")
    for index in range(1, len(stores)):
        page_url = stores[index].split("</loc>")[0].strip()
        log.info(page_url)
        locator_domain = website

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = "".join(
            store_sel.xpath('//h1[@class="store-name"]/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        street_address = "".join(
            store_sel.xpath('//input[@id="storeAddressLine1"]/@value')
        ).strip()

        address_2 = "".join(
            store_sel.xpath('//input[@id="storeAddressLine2"]/@value')
        ).strip()

        if len(address_2) > 0:
            street_address = street_address + ", " + address_2

        city = "".join(store_sel.xpath('//input[@id="city"]/@value')).strip()
        state = "".join(store_sel.xpath('//input[@id="state"]/@value')).strip()
        zip = "".join(store_sel.xpath('//input[@id="postalCode"][1]/@value')).strip()
        country_code = "".join(store_sel.xpath('//input[@id="country"]/@value')).strip()
        if country_code == "":
            country_code = "<MISSING>"

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        store_number = "".join(store_sel.xpath('//input[@id="storeId"]/@value')).strip()

        if store_number == "":
            store_number = "<MISSING>"

        phone = "".join(store_sel.xpath('//p[@itemprop="telephone"]/text()')).strip()

        location_type = "<MISSING>"
        hours = store_sel.xpath(
            '//div[contains(@class,"booked-details time-listings")]/p[@class="value"]'
        )
        hours_of_operation = ""
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("span[1]/text()")).strip()
            time = "".join(hour.xpath("span[2]/text()")).strip()
            hours_list.append(day + ":" + time)

        hours_of_operation = ";".join(hours_list).strip()

        latitude = "".join(store_sel.xpath('//input[@id="latitude"]/@value')).strip()
        longitude = "".join(store_sel.xpath('//input[@id="longitude"]/@value')).strip()

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"

        if location_name != "<MISSING>":
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
