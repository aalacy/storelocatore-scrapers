# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ingo.dk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.ingo.dk/station-search"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = json.loads(
            "".join(
                search_sel.xpath('//script[@type="application/json"]/text()')
            ).strip()
        )["ck_sim_search"]["station_results"]
        for no, store in stores.items():

            locator_domain = website

            location_name = store["/sites/{siteId}"]["name"]

            location_type = store["/sites/{siteId}"]["brand"]

            page_url = search_url

            raw_address = "<MISSING>"

            address_info = store["/sites/{siteId}/addresses"]["PHYSICAL"]
            street_address = address_info["street"]

            city = address_info["city"]

            state = address_info["county"]

            zip = address_info["postalCode"]

            country_code = address_info["country"]

            phone = store["/sites/{siteId}/contact-details"]["phones"]
            if phone:
                phone = phone["WOR"]
            else:
                phone = "<MISSING>"

            hours = store["/sites/{siteId}/opening-info"]["openingTimes"]

            hours_of_operation = (
                "; ".join(hours)
                .replace("day;", "day:")
                .replace("Fri;", "Fri:")
                .replace("Sat;", "Sat:")
                .replace("Sun;", "Sun:")
                .replace("Thurs;", "Thurs:")
                .replace(":;", ":")
            )
            if store["/sites/{siteId}/opening-info"]["alwaysOpen"] is True:
                hours_of_operation = "24 Hours"

            store_number = no

            latitude, longitude = (
                store["/sites/{siteId}/location"]["lat"],
                store["/sites/{siteId}/location"]["lng"],
            )

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
