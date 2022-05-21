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

website = "clubcarwash.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "clubcarwash.com",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
    "x-wpgmza-action-nonce": "119069b99c",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://clubcarwash.com/locations-map/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    with SgRequests(dont_retry_status_codes=([404])) as session:
        api_urls = [
            "https://clubcarwash.com/wp-json/wpgmza/v1/marker-listing/base64eJyrVirIKHDOSSwuVrJSCg9w941yjInxTSzKTi3yySwuycxLj4lxSizOTA5JTMpJVdJRKi5JLCpRsjLQUcpJzUsvyVCyMjQAcnITC+IzU4BmGCnVAgDK3RuU",
            "https://clubcarwash.com/wp-json/wpgmza/v1/marker-listing/base64eJyrVirIKHDOSSwuVrJSCg9w941yjInxTSzKTi3yySwuycxLj4lxSizOTA5JTMpJVdJRKi5JLCpRsjI0MNBRyknNSy-JgHJyEwviM1OAphgp1QIA-Usb9Q",
        ]
        for api_url in api_urls:
            stores_req = session.get(api_url, headers=headers)
            stores = json.loads(stores_req.text)["meta"]

            for store in stores:
                page_url = store["link"]
                locator_domain = website
                location_name = store["title"]

                phone = "<MISSING>"
                raw_address = store["address"]
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode
                country_code = "US"

                store_number = store["id"]

                location_type = "<MISSING>"
                hours = store["description"]
                hours_sel = lxml.html.fromstring(hours)
                hours_info = hours_sel.xpath(".//text()")[1:]
                if (
                    "coming" in hours.lower()
                    or "opening" in hours.lower()
                    or "opens in" in hours.lower()
                ):
                    location_type = " ".join(hours_sel.xpath("//text()")).strip()

                hours_of_operation = "; ".join(hours_info).replace(" //", ":")
                latitude = store["lat"]
                longitude = store["lng"]

                if (
                    page_url
                    == "https://clubcarwash.com/locations/overland-park-mo-w-121st-street/"
                ):
                    hours_of_operation = "Mon - Sat: 7 AM to 8 PM; Sunday: 8 AM to 8 PM"
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
