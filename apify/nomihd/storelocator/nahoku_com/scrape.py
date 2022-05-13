# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "nahoku.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}


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
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://www.nahoku.com/pages/store-locations"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[@class="store"]')

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = "".join(store.xpath(".//a[./u/text()]/@href"))
            log.info(page_url)

            store_res = session.get(page_url, headers=headers)

            store_sel = lxml.html.fromstring(store_res.text)

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//text()")],
                )
            )

            location_name = store_info[0]

            location_type = "<MISSING>"

            raw_address = " ".join(store_info[1:-1]).split("Phone:")[0].strip()

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city

            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "US"

            store_number = "<MISSING>"
            phone = store_info[-2]
            if "Phone" in phone:
                phone = phone.split("Phone:")[1].strip()

            else:
                phone = "<MISSING>"

            hours = (
                "".join(store_sel.xpath('//meta[@name="description"]/@content'))
                .split("Hours:")[1]
                .strip()
            )
            hours_of_operation = (
                hours.replace("day;", "day:")
                .replace("b;", "b:")
                .replace("Dia:; ", "")
                .replace("Hora:; ", "")
                .replace("PM", "PM; ")
                .replace("PM;  ", "PM; ")
                .strip(" ;")
            )
            map_link = "".join(
                store_sel.xpath('//iframe[contains(@src,"maps")]/@src')
            ).strip()

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
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
