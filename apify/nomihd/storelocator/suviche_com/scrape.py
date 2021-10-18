# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "suviche.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
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
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    search_url = "https://www.suviche.com/sushi-ceviche-restaurant-locations-miami-beach-fort-lauderdale"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[@class="adrs-box"]')

        for store in stores:

            page_url = "".join(
                store.xpath('.//div[@class="adrs-rt-txt"]/a[@class="fancybox"]/@href')
            ).strip()
            log.info(page_url)
            page_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(page_res.text)

            locator_domain = website

            location_name = "".join(
                store.xpath('.//div[@class="adrs-rt-txt"]/a[@class="fancybox"]/@title')
            ).strip()
            raw_address = list(
                filter(
                    str, [x.strip() for x in store.xpath("./div[p]/p[not(a)]//text()")]
                )
            )

            raw_address = " ".join(raw_address).strip().split("Find us")[0].strip()
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

            phone = "".join(
                store.xpath(
                    './/div[@class="adrs-rt-txt"]/span[@class="adrs-ph-no"]//text()'
                )
            ).strip()

            location_type = "<MISSING>"

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './/div[@class="time-box"]/div[@class="desc"]/p//text()'
                        )
                    ],
                )
            )
            hours_of_operation = "; ".join(hours)

            map_link = "".join(store_sel.xpath('//iframe[contains(@src,"maps")]/@src'))
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
