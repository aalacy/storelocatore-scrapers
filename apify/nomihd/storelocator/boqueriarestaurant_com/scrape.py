# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "boqueriarestaurant.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "boqueriarestaurant.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    base = "https://boqueriarestaurant.com"

    search_res = session.get(base, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    api_url = "https://webstore-v2.goparrot.ai/api/v2/merchants/465e4a11-4b2e-4807-8f5d-e90de1f1d84e/place-picker-stores-with-stores"
    api_res = session.get(api_url, headers=headers)
    json_res = json.loads(api_res.text)

    stores_list = search_sel.xpath(
        '//div[@class="vc_tta-panels" and .//p[contains(./text(),"Hours")]]/div[.//text()="Hours"]'
    )
    for store in stores_list:
        name = "".join(store.xpath(".//h3/text()")).strip()

        for store_json in json_res:  # get target store json
            if name.upper() in store_json["name"].upper():
                break

        if name.upper() not in store_json["name"].upper():
            log.info("json_data not updated")
            continue

        store_number = "".join(store.xpath("@id")).strip()
        page_url = "https://boqueriarestaurant.com/#" + store_number
        locator_domain = website

        location_name = store_json["name"].strip()

        street_address = (
            store_json["location"]["houseNumber"]
            + " "
            + store_json["location"]["streetName"]
        ).strip()

        city = store_json["location"]["city"].strip()
        state = store_json["location"]["stateCode"].strip()

        zip = store_json["location"]["postalCode"].strip()

        country_code = store_json["location"]["countryCode"].strip()

        phone = store_json["details"]["contactInfo"]["phoneNumber"]

        location_type = "<MISSING>"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath(
                        ".//div[./p[contains(text(),'Hours')]]/p[2]//text()"
                    )
                ],
            )
        )
        hours_of_operation = "; ".join(hours).strip()

        latitude = store_json["location"]["latitude"]
        longitude = store_json["location"]["longitude"]

        raw_address = "<MISSING>"
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
