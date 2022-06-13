# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "discoveringfinland.com/shopping/shopping-centres"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.discoveringfinland.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.discoveringfinland.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.discoveringfinland.com/jm-ajax/get_listings/"
    data = {
        "lang": "en",
        "search_categories[]": "shopping-centres",
        "search_keywords": "",
        "search_location": "",
        "per_page": "1000",
        "orderby": "featured",
        "order": "DESC",
        "page": "1",
        "featured": "true",
        "show_pagination": "false",
    }
    with SgRequests() as session:
        search_res = session.post(search_url, headers=headers, data=data)
        stores_sel = lxml.html.fromstring(json.loads(search_res.text)["html"])
        stores = stores_sel.xpath("//article")
        for store in stores:
            locator_domain = website
            page_url = "".join(store.xpath("@data-permalink")).strip()
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            if isinstance(store_req, SgRequestError):
                continue

            store_sel = lxml.html.fromstring(store_req.text)
            location_name = "".join(
                store_sel.xpath('//h1[@class="entry-title"]/text()')
            ).strip()
            location_type = "<MISSING>"

            street_address = " ".join(
                store_sel.xpath(
                    '//address[@itemprop="address"]/div[@itemprop="streetAddress"]//text()'
                )
            ).strip()
            city = "".join(
                store_sel.xpath(
                    '//address[@itemprop="address"]/span[@itemprop="addressLocality"]/text()'
                )
            ).strip()

            state = "".join(
                store_sel.xpath(
                    '//address[@itemprop="address"]/span[@itemprop="addressRegion"]/text()'
                )
            ).strip()
            zip = "".join(
                store_sel.xpath(
                    '//address[@itemprop="address"]/span[@itemprop="postalCode"]/text()'
                )
            ).strip()
            country_code = "".join(
                store_sel.xpath(
                    '//address[@itemprop="address"]/span[@itemprop="addressCountry"]/text()'
                )
            ).strip()

            phone = "".join(
                store_sel.xpath('//a[@itemprop="telephone"]/text()')
            ).strip()
            if phone == "-":
                phone = "<MISSING>"

            hours_of_operation = "<MISSING>"
            store_number = "<MISSING>"
            latitude, longitude = (
                "".join(store.xpath("@data-latitude")).strip(),
                "".join(store.xpath("@data-longitude")).strip(),
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
