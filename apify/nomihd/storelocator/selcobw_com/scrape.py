# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "selcobw.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.selcobw.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "origin": "https://www.selcobw.com",
    "content-type": "application/x-www-form-urlencoded",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.selcobw.com/branches"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = json.loads(
            "".join(
                search_sel.xpath('//script[@id="apollo-client-state"]/text()')
            ).strip()
        )
        for key in stores.keys():
            if "ROOT_QUERY.branches." in key:
                locator_domain = website

                location_name = stores[key]["name"]

                location_type = stores[key]["__typename"]

                page_url = stores[key]["url"]
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                json_list = store_sel.xpath(
                    '//script[@type="application/ld+json"]/text()'
                )
                street_address = "<MISSING>"
                city = "<MISSING>"
                hours_of_operation = "<MISSING>"
                for js in json_list:
                    if "@type" in js and json.loads(js)["@type"] == "LocalBusiness":
                        store_json = json.loads(js)
                        location_name = store_json["name"]
                        street_address = store_json["address"]["streetAddress"]
                        city = store_json["address"]["addressLocality"]
                        hours_of_operation = "; ".join(
                            store_json["openingHours"]
                        ).strip()

                state = stores[key]["county"]

                zip = stores[key]["postcode"]

                country_code = "GB"

                phone = stores[key]["telephone"]

                store_number = stores[key]["branch_id"]

                latitude, longitude = (
                    stores[key]["latitude"],
                    stores[key]["longitude"],
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
