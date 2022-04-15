# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import ssl

website = "joevsmartshop.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    search_url = "https://www.joevsmartshop.com/locations"
    with SgChrome() as driver:

        driver.get(search_url)
        stores_sel = lxml.html.fromstring(driver.page_source)
        stores = json.loads(
            "".join(stores_sel.xpath('//script[@id="__NEXT_DATA__"]/text()')).strip()
        )["props"]["pageProps"]["pageSections"][1]["data"]["articles"]
        for store in stores:
            page_url = search_url
            location_type = "<MISSING>"
            locator_domain = website

            location_name = store["fields"]["storeName"]

            raw_address = store["fields"]["storeAddress"].split(",")
            street_address = ", ".join(raw_address[:-2]).strip()
            city = raw_address[-2].strip()
            state = raw_address[-1].strip().split(" ")[0].strip()
            zip = raw_address[-1].strip().split(" ")[-1].strip()
            country_code = "US"

            phone = store["fields"]["storePhoneNumber"]
            location_type = "<MISSING>"

            hours_of_operation = store["fields"]["storeHours"].replace(",", ":").strip()

            store_number = "<MISSING>"
            map_link = store["fields"]["urlslug"]
            latitude, longitude = get_latlng(map_link)

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
