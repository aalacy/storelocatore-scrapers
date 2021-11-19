# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser
import json

website = "rockitcoin.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "rockitcoin.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://rockitcoin.com/locations"
    with SgRequests(proxy_country="us", dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(
            (
                stores_req.text.split("pointONE = ")[1].strip().split("];")[0].strip()
                + "]"
            )
        )
        for store in stores:
            store_sel = lxml.html.fromstring(store[2])

            page_url = "".join(
                store_sel.xpath('//a[./p[@class="loc-title"]]/@href')
            ).strip()

            location_name = "".join(
                store_sel.xpath('//a/p[@class="loc-title"]/text()')
            ).strip()
            if len(location_name) <= 0:
                location_name = "".join(
                    store_sel.xpath('//p[@class="loc-title"]/text()')
                ).strip()
            location_type = "<MISSING>"
            locator_domain = website

            raw_address = list(
                filter(
                    str,
                    store_sel.xpath('//p[@class="location-address"]/text()'),
                )
            )
            raw_address = (
                ", ".join(raw_address).strip().replace("United States", "").strip()
            )
            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            if state is None and city is not None:
                state = city.rsplit(" ", 1)[-1].strip()
                city = city.rsplit(" ", 1)[0].strip()

            zip = formatted_addr.postcode
            if zip:
                if zip.isalpha():
                    zip = "<MISSING>"

            if not city and not state:
                if "," in raw_address:
                    city = raw_address.split(",")[-1].strip().rsplit(" ", 1)[0].strip()
                    state = (
                        raw_address.split(",")[-1].strip().rsplit(" ", 1)[-1].strip()
                    )
                    street_address = raw_address.split(",")[0].strip()

            country_code = "US"
            store_number = "<MISSING>"
            phone = "1-888-702-4826"
            hours_of_operation = (
                " ".join(
                    filter(
                        str,
                        store_sel.xpath('//p[@class="hours-of-operation"]//text()'),
                    )
                )
                .strip()
                .replace("\n", "")
                .strip()
                .replace("Hours of Operation;", "")
                .strip()
                .replace("Hours of Operation", "")
                .strip()
            )

            latitude = store[0]
            longitude = store[1]

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
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
