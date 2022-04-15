# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "direkten.se"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "direkten.se",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://direkten.se/hittabutiker/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@id="stores_data"]/div[@data-storename]')
        for store in stores:
            page_url = "".join(store.xpath("@data-permalink")).strip()
            locator_domain = website
            location_name = "".join(store.xpath("@data-storename")).strip()

            street_address = "".join(store.xpath("@data-address")).strip()
            city = "".join(store.xpath("@data-city")).strip()
            state = "<MISSING>"
            zip = "".join(store.xpath("@data-postcode")).strip()

            country_code = "SE"
            store_number = "".join(store.xpath("@data-databaseid")).strip()
            phone = "".join(store.xpath("@data-phone")).strip()

            location_type = "<MISSING>"

            latitude = "".join(store.xpath("@data-latitude")).strip()
            longitude = "".join(store.xpath("@data-longitude")).strip()

            hours_list = []
            if len("".join(store.xpath("@data-mondayopen")).strip()) > 0:
                hours_list.append(
                    "Mon:" + "".join(store.xpath("@data-mondayopen")).strip()
                )

            if len("".join(store.xpath("@data-tuesdayopen")).strip()) > 0:
                hours_list.append(
                    "Tue:" + "".join(store.xpath("@data-tuesdayopen")).strip()
                )

            if len("".join(store.xpath("@data-wednesdayopen")).strip()) > 0:
                hours_list.append(
                    "Wed:" + "".join(store.xpath("@data-wednesdayopen")).strip()
                )

            if len("".join(store.xpath("@data-thursdayopen")).strip()) > 0:
                hours_list.append(
                    "Thu:" + "".join(store.xpath("@data-thursdayopen")).strip()
                )

            if len("".join(store.xpath("@data-fridayopen")).strip()) > 0:
                hours_list.append(
                    "Fri:" + "".join(store.xpath("@data-fridayopen")).strip()
                )

            if len("".join(store.xpath("@data-saturdayopen")).strip()) > 0:
                hours_list.append(
                    "Sat:" + "".join(store.xpath("@data-saturdayopen")).strip()
                )

            if len("".join(store.xpath("@data-sundayopen")).strip()) > 0:
                hours_list.append(
                    "Sun:" + "".join(store.xpath("@data-sundayopen")).strip()
                )

            hours_of_operation = "; ".join(hours_list).strip()

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
