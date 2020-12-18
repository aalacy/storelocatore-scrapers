# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgzip.static import static_zipcode_list

website = "floorstogo.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "Origin": "https://www.floorstogo.com",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://www.floorstogo.com/StoreLocator.aspx",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
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
    zips = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=75,
        max_search_results=5,
    )
    zips = ["94010"]
    zips = static_zipcode_list(radius=200, country_code=SearchableCountries.USA)
    # for zip_code in zips:
    if True:
        for zip_code in zips:
            log.info(f"{zip_code} | remaining: {zips.items_remaining()}")

        search_url = (
            "https://www.floorstogo.com/StoreLocator.aspx?&searchZipCode=" + zip_code
        )
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//table[@class="MasterTable_Default"]/tbody/tr')
        for store in stores:
            temp_text = store.xpath(
                ".//div[@class='search-store__results-address col-xs-12 col-sm-4']/p"
            )
            if store.xpath(
                ".//div[@class='search-store__results-address col-xs-12 col-sm-4']"
            ):
                raw_text = []
                for t in temp_text:
                    raw_text.append("".join(t.xpath("text()")).strip())

                locator_domain = website
                location_name = raw_text[-4]
                street_address = raw_text[-3]
                city_state_zip = raw_text[-2]
                city = city_state_zip.split(",")[0].strip()
                state = city_state_zip.split(",")[1].strip().rsplit(" ", 1)[0].strip()
                zip = city_state_zip.split(",")[1].strip().rsplit(" ", 1)[1].strip()

                if street_address == "":
                    street_address = "<MISSING>"

                if city == "":
                    city = "<MISSING>"

                if state == "":
                    state = "<MISSING>"

                if zip == "":
                    zip = "<MISSING>"

                country_code = "US"

                store_number = "<MISSING>"
                phone = raw_text[-1].strip()
                location_type = "<MISSING>"
                hours_of_operation = ""
                web = "".join(
                    store.xpath('.//a[contains(text(),"view website")]/@href')
                ).strip()
                if len(web) > 0:
                    latitude = "<INACCESSIBLE>"
                    longitude = "<INACCESSIBLE>"

                    url = "https://www.floorstogo.com" + web
                    store_req = session.get(url, headers=headers)
                    store_sel = lxml.html.fromstring(store_req.text)
                    page_url = store_req.url
                    locations = store_sel.xpath('//div[@class="multi-location"]')
                    if len(locations) <= 0:
                        locations = store_sel.xpath('//div[@class="single-location"]')
                    hours_of_operation = ""
                    for loc in locations:
                        if (
                            phone
                            == "".join(
                                loc.xpath('a[@class="footer-phone"]/text()')
                            ).strip()
                        ):
                            hours_of_operation = "".join(
                                loc.xpath('p[@class="hours"]/text()')
                            ).strip()
                            if not hours_of_operation:
                                hours_of_operation = "".join(
                                    store_sel.xpath('.//p[@class="hours"]/text()')
                                ).strip()
                            break
                else:
                    page_url = search_url
                    latitude = "<MISSING>"
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
