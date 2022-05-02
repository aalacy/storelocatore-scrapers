# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "learningrx.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://code.metalocator.com/index.php?option=com_locator&view=location&tmpl=component&task=load&framed=1&format=json&templ[]=map_address_template&sample_data=undefined&lang=&_opt_out=&Itemid=15430&number={}&id={}&distance=&_urlparams"
    for index in range(1, 200):
        log.info(index)
        store_req = session.get(
            search_url.format(str(index), str(index)), headers=headers
        )
        json_data = json.loads(store_req.text)
        if len(json_data) > 0:
            store = json_data[0]
            if "name" in store:
                if store["name"] != "" or store["name"] is not None:
                    location_name = store["name"]
                    if (
                        "coming" in location_name.lower()
                        or "opening" in location_name.lower()
                    ):
                        continue

                    if "http" not in store["link"]:
                        page_url = "https:" + store["link"]
                    else:
                        page_url = store["link"]
                    locator_domain = website

                    street_address = store["address"]
                    if store["address2"] is not None:
                        if len(store["address2"]) > 0:
                            street_address = street_address + ", " + store["address2"]

                    city = store["city"].strip()
                    state = store["state"].strip()
                    zip = store["postalcode"].strip()

                    country_code = store["country"]
                    store_number = str(store["id"])
                    phone = store["phone"]

                    log.info(page_url)
                    hours_of_operation = "<MISSING>"
                    store_page_req = session.get(page_url, headers=headers)
                    if not isinstance(store_page_req, SgRequestError):
                        store_page_sel = lxml.html.fromstring(store_page_req.text)
                        if phone is None or len(phone) <= 0:
                            phone = store_page_sel.xpath(
                                '//a[@class="app-header__utility-bar-phone"]/text()'
                            )
                            if len(phone) > 0:
                                phone = phone[0].strip()

                        hours_of_operation = "; ".join(
                            list(
                                filter(
                                    str,
                                    (
                                        [
                                            x.strip()
                                            for x in store_page_sel.xpath(
                                                '//div[@class="detail-list_block"][.//div[contains(text(),"Hours")]]/div[2]/text()'
                                            )
                                        ]
                                    ),
                                )
                            )
                        )

                    location_type = "<MISSING>"

                    latitude = store["lat"]
                    longitude = store["lng"]

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
