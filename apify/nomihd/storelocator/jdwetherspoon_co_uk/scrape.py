# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "jdwetherspoon.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://www.jdwetherspoon.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.jdwetherspoon.com/pubs/all-pubs",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    data = '{"region":null,"paging":{"UsePagination":false},"facilities":[],"searchType":0}'
    search_url = "https://www.jdwetherspoon.com/api/advancedsearch"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.post(search_url, data=data, headers=headers)
        regions = json.loads(stores_req.text)["regions"]
        for region in regions:
            subRegions = region["subRegions"]
            for sub in subRegions:
                stores = sub["items"]
                for store in stores:
                    page_url = "https://www.jdwetherspoon.com" + store["url"]

                    locator_domain = website
                    location_name = store["name"]

                    street_address = (
                        store["address1"]
                        .strip()
                        .encode("ascii", "replace")
                        .decode("utf-8")
                        .replace("?", "-")
                        .strip()
                    )
                    city = store["city"].strip()
                    state = store["county"].strip()
                    zip = store["postcode"].strip()
                    country_code = region["region"]

                    store_number = store["pubNumber"]
                    phone = store["telephone"]

                    location_type = "<MISSING>"
                    if "/pubs/" in page_url:
                        location_type = "pub"
                    elif "/hotels/" in page_url:
                        location_type = "hotel"

                    hours_of_operation = ""
                    if store["pubIsTemporaryClosed"] is True:
                        hours_of_operation = "Temporary Closed"
                    else:
                        log.info(page_url)
                        retry_count = 0
                        store_req = session.get(page_url, headers=headers)
                        while isinstance(store_req, SgRequestError) and retry_count < 3:
                            log.info(page_url)
                            store_req = session.get(page_url, headers=headers)
                            retry_count = retry_count + 1

                        if not isinstance(store_req, SgRequestError):

                            store_sel = lxml.html.fromstring(store_req.text)
                            hours = store_sel.xpath(
                                '//div[@id="opening-times"]//td[@itemprop="openingHours"]'
                            )
                            hours_list = []
                            for hour in hours:
                                if (
                                    len(
                                        "".join(hour.xpath("@content"))
                                        .strip()
                                        .split("-")
                                    )
                                    > 1
                                ):
                                    if (
                                        len(
                                            "".join(hour.xpath("@content"))
                                            .strip()
                                            .split("-")[1]
                                            .strip()
                                        )
                                        > 0
                                    ):
                                        hours_list.append(
                                            "".join(hour.xpath("@content")).strip()
                                        )

                            hours_of_operation = "; ".join(hours_list).strip()
                        else:
                            log.error("\t\tSkipped\t\t")

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
