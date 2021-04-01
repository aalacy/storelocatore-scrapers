# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

website = "krispykreme.co.uk"
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

    search_url = (
        "https://www.krispykreme.co.uk/find-store?store-search={}&store-search-type="
    )

    search = DynamicZipSearch(country_codes=[SearchableCountries.BRITAIN])

    for zipcode in search:
        log.info(f"{zipcode} | remaining: {search.items_remaining()}")
        stores_req = session.get(search_url.format(zipcode), headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//a[@class="storefinder-item__link storefinder-button--secondary"]/@href'
        )

        for store_url in stores:
            page_url = store_url
            log.info(page_url)
            locator_domain = website

            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            location_name = "".join(
                store_sel.xpath('//h1[@class="page-title"]/span/text()')
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            sections = store_sel.xpath('//section[@class="storeview-info__block"]')

            address = ""
            hours_list = []
            for sec in sections:
                if "Address" in "".join(sec.xpath("h4/text()")).strip():
                    address = "".join(sec.xpath("text()")).strip()
                if "Opening Times" in "".join(sec.xpath("h4/text()")).strip():
                    hours_list = sec.xpath("p//text()")

            street_address = address.split(", GB", 1)[0].strip()

            city = "<MISSING>"
            state = "<MISSING>"
            zip = address.split(", GB", 1)[1].strip().replace(",", "").strip()

            country_code = "GB"
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

            store_number = "<MISSING>"

            if store_number == "":
                store_number = "<MISSING>"

            phone = "<MISSING>"

            location_type = "<MISSING>"
            hours_of_operation = ";".join(hours_list).strip()

            direction_link = "".join(
                store_sel.xpath('//a[@class="storefinder-button--ghost"]/@href')
            ).strip()

            latitude = ""
            longitude = ""
            if len(direction_link) > 0:
                latitude = (
                    direction_link.split("&query=")[1].strip().split(",")[0].strip()
                )
                longitude = (
                    direction_link.split("&query=")[1].strip().split(",")[1].strip()
                )

                search.found_location_at(latitude, longitude)

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
            yield curr_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
