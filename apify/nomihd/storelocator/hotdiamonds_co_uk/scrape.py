# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

website = "hotdiamonds.co.uk"
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

    search_url = "https://hotdiamonds.co.uk/map"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    urls = stores_sel.xpath('//a[@class="store-locator__store__link button"]/@href')

    all_stores = stores_sel.xpath(
        '//div[@class="store-locator__stores"]/div[@class="row"]/div'
    )

    url_dict = {}
    for data in all_stores:
        url = data.xpath('.//div[@class="store-locator__store"]//a/@href')
        if len(url) > 0:
            url = url[0]
        title = "".join(
            data.xpath('.//strong[@class="store-locator__store__title"]/text()')
        ).strip()
        zip_code = data.xpath(
            './/div[@class="row store-locator__store__info"]//p/span/text()'
        )
        title = title.lower()
        url_dict[title + zip_code[-1]] = url

    stores = stores_req.text.split("_content = ")
    latlngs = stores_req.text.split("_marker_latlng = new google.maps.LatLng(")

    for index in range(1, len(stores)):
        locator_domain = website
        location_name = (
            stores[index]
            .split("<strong>")[1]
            .strip()
            .split("<")[0]
            .strip()
            .replace("&amp;", "&")
            .strip()
            .replace("&#039;", "'")
            .strip()
        )
        if location_name == "":
            location_name = "<MISSING>"

        street_address = ""
        try:
            street_address = (
                stores[index]
                .split('branch-address1">')[1]
                .strip()
                .split("<")[0]
                .strip()
            )
        except:
            pass

        if 'branch-address2">' in stores[index]:
            address_2 = (
                stores[index]
                .split('branch-address2">')[1]
                .strip()
                .split("<")[0]
                .strip()
            )
            if len(address_2) > 0:
                street_address = street_address + ", " + address_2

        city = ""
        try:
            city = stores[index].split('branch-city">')[1].strip().split("<")[0].strip()
        except:
            pass

        state = "<MISSING>"

        zip = ""
        try:
            zip = (
                stores[index]
                .split('branch-postcode">')[1]
                .strip()
                .split("<")[0]
                .strip()
            )
        except:
            pass

        page_url = "https://hotdiamonds.co.uk" + url_dict[location_name.lower() + zip]

        country_code = "GB"

        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        store_number = urls[index - 1].split("/")[-1]

        location_type = "<MISSING>"

        phone = ""
        try:
            phone = (
                stores[index]
                .split('branch-telephone">')[1]
                .strip()
                .split("<")[0]
                .strip()
                .replace("Tel:", "")
                .strip()
            )
        except:
            pass

        hours_of_operation = "<MISSING>"

        latitude = latlngs[index].split(",")[0].strip()
        longitude = latlngs[index].split(",")[1].strip().split(")")[0].strip()
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
        loc_list.append(curr_list)

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
