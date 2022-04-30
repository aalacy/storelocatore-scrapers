# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bimbobakeriesusa.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "Origin": "https://bimbobakeriesusa.com",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://bimbobakeriesusa.com/outlet-locator",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://bimbobakeriesusa.com/outlet-locator"
    home_req = session.get(search_url, headers=headers)
    home_sel = lxml.html.fromstring(home_req.text)
    states = home_sel.xpath('//select[@name="state"]/option[position()>1]/@value')

    ID = "".join(home_sel.xpath('//input[@name="form_build_id"]/@value')).strip()
    for state in states:
        log.info(f"fetching data for state: {state}")
        data = {
            "state": state,
            "form_build_id": ID,
            "form_id": "outlet_locator_form",
        }

        stores_req = session.post(
            "https://bimbobakeriesusa.com/outlet-locator", headers=headers, data=data
        )
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//table[@class="table"]//tbody/tr')

        for store in stores:
            page_url = "https://bimbobakeriesusa.com/outlet-locator"
            location_type = "<MISSING>"
            locator_domain = website
            location_name = "BIMBO BAKERIES USA"

            raw_address = "".join(store.xpath("td[1]/text()")).strip()
            if "Sorry, No outlet" in raw_address:
                continue

            raw_address = raw_address.split(",")
            street_address = ", ".join(raw_address[:-2]).strip()
            city = raw_address[-2].strip()
            state = raw_address[-1].strip().split(" ")[0].strip()
            zip = raw_address[-1].strip().split(" ")[-1].strip()

            country_code = "US"
            phone = (
                "".join(store.xpath("td[2]//text()"))
                .strip()
                .split("Ext")[0]
                .strip()
                .split("x")[0]
                .strip()
                .split("X")[0]
                .strip()
            )
            hours_of_operation = "<MISSING>"
            store_number = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.PHONE})
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
