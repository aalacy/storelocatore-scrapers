# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "sds.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.sds.com.au",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.sds.com.au/stores"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@id="store-location-results"]/div')
        for store in stores:
            page_url = "".join(
                store.xpath(".//a[@class='store-details-link']/@href")
            ).strip()
            if len(page_url) > 0:
                page_url = "https://www.sds.com.au" + page_url

            locator_domain = website
            location_name = "".join(store.xpath("@data-storename")).strip()
            raw_address = "".join(store.xpath("@data-addressa")).strip()
            add_2 = "".join(store.xpath("@data-addressb")).strip()
            if add_2 != "null":
                raw_address = raw_address + ", " + add_2

            if "," == raw_address[-1]:
                raw_address = "".join(raw_address[:-1]).strip()

            city = "".join(store.xpath("@data-city")).strip()
            if len(city) > 0:
                raw_address = raw_address + ", " + city

            state = "".join(store.xpath("@data-statecode")).strip()
            if len(state) > 0:
                raw_address = raw_address + ", " + state

            zip = (
                "".join(store.xpath("@data-postalcode"))
                .strip()
                .replace("null", "")
                .strip()
            )
            if len(zip) > 0:
                raw_address = raw_address + ", " + zip

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address:
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
            else:
                if formatted_addr.street_address_2:
                    street_address = formatted_addr.street_address_2

            phone = (
                "".join(store.xpath("@data-storephone"))
                .strip()
                .replace("null", "")
                .strip()
            )

            country_code = "AU"
            store_number = "".join(store.xpath("@data-storeid")).strip()

            location_type = "<MISSING>"

            latitude = (
                "".join(store.xpath("@data-storelat"))
                .strip()
                .replace("null", "")
                .strip()
            )
            longitude = (
                "".join(store.xpath("@data-storelon"))
                .strip()
                .replace("null", "")
                .strip()
            )

            days = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './/div[@class="store-hours"]/div/span/text()'
                        )
                    ],
                )
            )
            timee = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath('.//div[@class="store-hours"]/div/text()')
                    ],
                )
            )
            hours_list = []
            for index in range(0, len(days)):
                hours_list.append(days[index] + ":" + timee[index])

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
                raw_address=raw_address,
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
