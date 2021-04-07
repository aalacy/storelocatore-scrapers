# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

website = "k1speed.ca"
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

    search_url = "https://www.k1speed.ca/locations.html"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//li[@class="menu-item menu-item-type-post_type menu-item-object-page "]/a[contains(@href,"-location.html")]/@href'
    )
    for store_url in list(set(stores)):
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_type = "".join(
            store_sel.xpath(
                '//*[@id="bodyloc"]/div[1]/div/div/div/div/div/div[3]/section/div/div/div/div/div/div[1]/div/span/text()'
            )
        ).strip()
        locator_domain = website
        location_name = store_sel.xpath("//h1/text()")
        if len(location_name) > 0:
            location_name = (
                location_name[0]
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "'")
                .strip()
            )

        if location_name == "":
            location_name = "<MISSING>"

        street_address = "".join(
            store_sel.xpath('//span[@itemprop="streetAddress"]/text()')
        ).strip()
        street_address = street_address[:-1]
        city = "".join(
            store_sel.xpath('//span[@itemprop="addressLocality"]/text()')
        ).strip()
        state = "".join(
            store_sel.xpath('//span[@itemprop="addressRegion"]/text()')
        ).strip()
        zip = "".join(store_sel.xpath('//span[@itemprop="postalCode"]/text()')).strip()
        phone_list = store_sel.xpath('//span[@itemprop="telephone"]')
        phone = ""
        hours_list = []
        for ph in phone_list:
            hours_list.append("".join(ph.xpath("a/text()")).strip())

        if len(hours_list) > 0:
            phone = hours_list[-1].strip()

        country_code = "CA"

        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        store_number = "<MISSING>"

        if location_type == "":
            location_type = "<MISSING>"

        hours_of_operation = "; ".join(
            list(set(store_sel.xpath('//time[@itemprop="openingHours"]/@datetime')))
        ).strip()

        map_link = "".join(store_sel.xpath('//a[@itemprop="address"]/@href')).strip()
        latitude = ""
        longitude = ""
        if len(map_link) > 0:
            if "/@" in map_link:
                latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                longitude = map_link.split("/@")[1].strip().split(",")[1].strip()

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if phone == "" or phone is None:
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
        if street_address != "<MISSING>":
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
