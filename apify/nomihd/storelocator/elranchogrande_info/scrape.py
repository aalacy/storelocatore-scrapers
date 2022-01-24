# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "elranchogrande.info"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.livewireorders.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "content-type": "application/json",
    "origin": "https://www.livewireorders.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
}


def fetch_data():
    # Your scraper here

    search_url = "https://elranchogrande.info/online-order/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="fusion-column-wrapper fusion-flex-justify-content-flex-start fusion-content-layout-column"][.//a[contains(@href,"livewireorders.com")]]'
    )
    for store in stores:
        page_url = "".join(
            store.xpath('.//a[contains(@href,"livewireorders.com")]/@href')
        ).strip()
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        if isinstance(store_req, SgRequestError):
            page_url = "https://elranchogrande.info/online-order/"
            location_name = "".join(store.xpath(".//h1/text()")).strip()
            raw_address = store.xpath(
                './/div[contains(@class,"fusion-text fusion-text-")]/p/span/text()'
            )
            phone = "".join(
                store.xpath(
                    './/div[contains(@class,"fusion-text fusion-text-")]/p/a/span/text()'
                )
            ).strip()

            street_address = ", ".join(raw_address[:-1]).strip()
            city = raw_address[-1].strip().split(",")[0].strip()
            state = raw_address[-1].strip().split(",")[-1].strip().split(" ")[0].strip()
            zip = raw_address[-1].strip().split(",")[-1].strip().split(" ")[-1].strip()
            country_code = "US"

            hours_of_operation = "<MISSING>"
            store_number = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"
        else:
            restaurantUID = (
                store_req.text.split("restaurantUID = '")[1]
                .strip()
                .split("'")[0]
                .strip()
            )
            companyUID = (
                store_req.text.split("companyUID = '")[1].strip().split("'")[0].strip()
            )

            data = {
                "#": None,
                "company_uid": companyUID,
                "restaurant_uid": restaurantUID,
                "facebook": "true",
                "payload": {
                    "language_code": "en",
                    "init": 1,
                    "source": "facebook",
                    "reference": None,
                },
            }
            store_req = session.post(
                "https://www.livewireorders.com/api/cart/init",
                json=data,
                headers=headers,
            )

            json_data = json.loads(store_req.text)["restaurant"]

            location_name = json_data["name"]

            street_address = json_data["terms"]["address"]
            city = json_data["terms"]["city"]
            state = json_data["terms"]["state_code"]
            zip = json_data["terms"]["zip"]
            country_code = json_data["terms"]["country_code"]

            phone = json_data["terms"]["phone"].replace("+1 ", "").strip()

            hours_of_operation = "<INACCESSIBLE>"
            store_number = "<MISSING>"

            latitude = json_data["latitude"]
            longitude = json_data["longitude"]

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
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
