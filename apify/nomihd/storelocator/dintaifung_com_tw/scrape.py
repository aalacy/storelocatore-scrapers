# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "dintaifung.com.tw"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.dintaifung.com.tw/eng/store.php?cid=1"
    stores_req = session.get(
        search_url.replace("store.php", "store_list.php"), headers=headers
    )
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="info"]')

    for store in stores:
        page_url = search_url
        locator_domain = website
        location_name = "".join(store.xpath('div[@class="name"]/text()')).strip()

        raw_address = (
            "".join(store.xpath('.//div[@class="addr"]//text()'))
            .strip()
            .split("(")[0]
            .strip()
        )
        street_address = raw_address.rsplit(",", 1)[0].strip()
        city = raw_address.rsplit(",", 1)[-1].strip()
        state = "<MISSING>"
        if "District" in street_address or "Dist." in street_address:
            state = street_address.rsplit(",", 1)[-1].strip()
            street_address = street_address.rsplit(",", 1)[0].strip()

        zip = "<MISSING>"
        country_code = "TW"

        phone = (
            "".join(store.xpath('.//div[@class="line"][2]/div/text()'))
            .strip()
            .split("FAX")[0]
            .strip()
        )

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        hours_of_operation = "".join(
            store.xpath(
                './/div[@class="line"][./label[contains(text(),"Business Hours")]]/div/text()'
            )
        ).strip()
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
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
