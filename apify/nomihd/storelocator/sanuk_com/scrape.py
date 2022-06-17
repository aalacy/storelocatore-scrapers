# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "sanuk.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.sanuk.com/official-sanuk-stores.html"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="col-xs-12"]')
        for store in stores:
            page_url = search_url

            locator_domain = website

            location_name = "".join(store.xpath("div/h2/text()")).strip()

            raw_list = list(
                filter(str, [x.strip() for x in store.xpath("div/address/a/text()")])
            )

            street_address = raw_list[0].strip().split("(")[0].strip()
            city_state_zip = raw_list[-1].strip()
            city = city_state_zip.split(",")[0].strip()
            state = (
                city_state_zip.split(",")[-1]
                .strip()
                .split(" ")[0]
                .strip()
                .replace(".", "")
                .strip()
            )
            zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()

            country_code = "US"

            store_number = "<MISSING>"

            phone = "".join(
                store.xpath('.//p/a[contains(@href,"tel:")]/text()')
            ).strip()

            location_type = "<MISSING>"
            hours = store.xpath(".//p")[-2].xpath("text()")
            hours_of_operation = "; ".join(hours).strip().replace("\n", "").strip()
            if len(hours_of_operation) > 0 and hours_of_operation[-1] == ";":
                hours_of_operation = "".join(hours_of_operation[:-1]).strip()

            map_link = "".join(store.xpath("div/address/a/@href")).strip()
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            if len(map_link) > 0 and "/@" in map_link:
                latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                longitude = map_link.split("/@")[1].strip().split(",")[1]

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
