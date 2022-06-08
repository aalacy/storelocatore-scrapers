# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
import json

website = "bata.cz"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.bata.cz",
    "accept": "text/html, */*; q=0.01",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "referer": "https://www.bata.cz/stores",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

params = {
    "viewType": "storelocator",
    "skipTextUpdate": "true",
    "distancesMap": "true",
    "isUserLocation": "true",
    "callFitToBounds": "true",
    "storeType": "original",
    "format": "ajax",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        stores_req = session.get(
            "https://www.bata.cz/storesfind", params=params, headers=headers
        )
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@data-id="store"]')
        for store in stores:

            page_url = (
                "https://www.bata.cz"
                + "".join(
                    store.xpath(
                        './/div[@class="b-find-store__address-title js-title-wrapper"]/a/@href'
                    )
                ).strip()
            )
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')
            for js in json_list:
                if "streetAddress" in js:
                    store_json = json.loads(js)

                    locator_domain = website

                    location_name = store_json["name"]

                    street_address = store_json["address"]["streetAddress"]
                    city = store_json["address"]["addressLocality"]
                    state = store_json["address"]["addressRegion"]
                    zip = store_json["address"]["postalCode"]
                    country_code = "CZ"
                    phone = store_json["telephone"]

                    location_type = "".join(store.xpath("@data-store-type")).strip()
                    store_number = page_url.split("?storeID=")[1].strip()

                    hours = store_sel.xpath(
                        '//ul[@class="b-storedetails__store-hours-list"]/li'
                    )
                    hours_list = []
                    for hour in hours:
                        day = "".join(
                            hour.xpath(
                                'span[@class="b-storedetails__store-hours-days"]/text()'
                            )
                        ).strip()
                        time = "".join(
                            hour.xpath(
                                'span[@class="b-storedetails__store-hours-time"]/text()'
                            )
                        ).strip()
                        hours_list.append(day + ":" + time)

                    hours_of_operation = "; ".join(hours_list).strip()

                    latitude, longitude = (
                        store_json["geo"]["latitude"],
                        store_json["geo"]["longitude"],
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
                    break


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
