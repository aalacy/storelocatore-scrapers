# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "dyson.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.dyson.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.dyson.com/demo-stores"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//div[@class="faq-container parbase"]')

    for store in store_list:

        page_url = search_url

        locator_domain = website

        store_info = list(
            filter(
                str,
                [x.strip() for x in store.xpath(".//div[h2]//div[p]//text()")],
            )
        )

        for phn_idx, x in enumerate(store_info):
            if "Tel" in x:
                break

        if "Tel" in store_info[phn_idx]:
            phone = store_info[phn_idx + 1].strip()

        full_address = store_info[:phn_idx]

        street_address = ", ".join(full_address[:-1]).strip()
        city = full_address[-1].split(",")[0].strip()
        state = full_address[-1].split(" ")[-2].strip()
        zip = full_address[-1].split(" ")[-1].strip()
        country_code = "US"

        location_name = "".join(store.xpath(".//div[h2]//div/h3/text()")).strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        hours = store_info[phn_idx + 3 :]
        hours_of_operation = (
            "; ".join(hours).replace("Now Open!;", "").replace(":;", ":").strip()
        )
        latitude, longitude = "<MISSING>", "<MISSING>"

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
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
