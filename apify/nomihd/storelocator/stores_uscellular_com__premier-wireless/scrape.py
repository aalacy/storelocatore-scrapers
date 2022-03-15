# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "https://stores.uscellular.com/premier-wireless"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "stores.uscellular.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "*/*",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://stores.uscellular.com/premier-wireless/" + "find-a-store"
    find_store_req = session.get(search_url, headers=headers)
    find_store_req_sel = lxml.html.fromstring(find_store_req.text)
    currentPageId = "".join(
        find_store_req.text.split("setParams(")[1].strip().split(",")[0].strip()
    )
    ufprt = "".join(find_store_req_sel.xpath('//input[@name="ufprt"]/@value')).strip()
    params = (
        ("currentPageId", currentPageId),
        ("googleApiKey", "AIzaSyCR5gGZa9t3Uq-LH7RMeAaxpqfUcRdLEtQ"),
        ("ufprt", ufprt),
    )
    stores_req = session.get(search_url, headers=headers, params=params)
    stores = stores_req.json()["locations"]
    for store in stores:
        page_url = "https://stores.uscellular.com" + store["storeDetailsUrl"]

        location_name = store["heading"]
        location_type = "<MISSING>"
        locator_domain = website

        street_address = store["streetAddress"]
        city = store["city"]
        state = store["state"]
        zip = store["zipCode"]

        country_code = "US"
        store_number = store["locationId"]
        phone = store["phoneNumber"]
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        days = store_sel.xpath(
            '//div[contains(@class,"hours service-div no-padding")]//div[@class="day"]/text()'
        )
        time = store_sel.xpath(
            '//div[contains(@class,"hours service-div no-padding")]//div[@class="timings"]/text()'
        )
        hours_list = []
        for index in range(0, len(days)):
            hours_list.append(
                "".join(days[index]).strip() + ":" + "".join(time[index]).strip()
            )

        if len(hours_list) > 0:
            hours_of_operation = "; ".join(hours_list).strip()
        else:
            hours_of_operation = "<MISSING>"
            if "our store is currently closed" in store_req.text:
                hours_of_operation = "Temporarily Closed"

        latitude = store["latitude"]
        longitude = store["longitude"]

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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
