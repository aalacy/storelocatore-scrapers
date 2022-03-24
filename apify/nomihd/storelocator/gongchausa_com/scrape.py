# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser
import lxml.html

website = "gongchausa.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "api.storepoint.co",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "accept": "*/*",
    "origin": "https://gongchausa.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://gongchausa.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (("rq", ""),)


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        stores_req = session.get(
            "https://api.storepoint.co/v1/161d1d5abc0b7c/locations",
            headers=headers,
            params=params,
        )
        stores = json.loads(stores_req.text)["results"]["locations"]
        for store in stores:
            locator_domain = website
            page_url = store["website"]

            location_name = store["name"]
            if "Coming soon" in location_name:
                continue

            locator_domain = website

            location_type = "<MISSING>"

            raw_address = store["streetaddress"]
            if "(" in raw_address:
                raw_address = (
                    raw_address.split("(")[0].strip()
                    + " "
                    + raw_address.split(")")[1].strip()
                )
            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address:
                if "Mall " in street_address:
                    street_address = street_address.split("Mall ")[1].strip()
                if "Center " in street_address:
                    street_address = street_address.split("Center ")[1].strip()
                if "Court " in street_address:
                    street_address = street_address.split("Court ")[1].strip()

            city = formatted_addr.city
            if city:
                city = (
                    city.replace("Space C, Dorchester", "Dorchester")
                    .replace("Logan Plaza Edison", "Edison")
                    .replace("Suite Montclair", "Montclair")
                    .strip()
                )

            state = formatted_addr.state
            zip = formatted_addr.postcode
            country_code = "US"

            phone = store["phone"]
            if page_url:
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                hours_of_operation = (
                    "; ".join(
                        store_sel.xpath('//div[./p[contains(text(),"Mon ")]]/p/text()')
                    )
                    .strip()
                    .replace("\n", "")
                    .strip()
                )
                if len(hours_of_operation) <= 0:
                    hours_of_operation = (
                        "; ".join(
                            store_sel.xpath(
                                '//div[./p[contains(text(),"Monday-")]]/p/text()'
                            )
                        )
                        .strip()
                        .replace("\n", "")
                        .strip()
                    )

            else:
                hours_of_operation = "<MISSING>"
            store_number = store["id"]
            latitude = store["loc_lat"]
            longitude = store["loc_long"]

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
