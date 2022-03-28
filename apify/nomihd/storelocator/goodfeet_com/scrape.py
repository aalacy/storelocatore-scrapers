# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import re
import us
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "goodfeet.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "Connection": "keep-alive",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_urls = [
        "https://www.goodfeet.com/locations",
        "https://www.goodfeet.com/au/locations",
    ]
    for search_url in search_urls:
        search_res = session.get(search_url, headers=headers)

        stores = (
            search_res.text.split("var addresses = ")[1]
            .split("]];")[0]
            .strip(' []"')
            .replace("\\u003C", "<")
            .replace("\\u003E", ">")
            .replace("\\u0022", '"')
            .replace("\\u0026", ",")
            .replace(" ,", ",")
            .replace("\\u0027", "")
            .replace("\\u0071", "")
            .replace("\\/", "/")
            .replace("\\n", "")
            .replace("\\r", "")
            .split('"],["')
        )

        for store in stores:
            if "Opening Soon!" in store:
                continue

            locator_domain = website

            store_info = store.split(',"')[1]

            store_number = "<MISSING>"

            html_str = store_info.split('",')[0].strip()
            page_sel = lxml.html.fromstring(html_str)

            location_name = "".join(page_sel.xpath("//h4//text()"))

            page_url = "".join(page_sel.xpath("//h4/a/@href")).strip()
            if page_url.split("/")[-1] == "test":
                continue

            phone = "".join(page_sel.xpath("//a[contains(@href,'tel:')]/text()"))

            address_info = page_sel.xpath(
                '//p[./i[contains(@class,"map-marked")]]//text()'
            )
            if len(address_info) == 1:
                address_info = "".join(address_info).split(",")

            street_address = ", ".join(address_info[0:-2]).strip()
            city = address_info[-2].split(", ")[-1].strip(' ",')
            state = address_info[-1].strip().split(" ")[0].strip()
            zip = address_info[-1].strip().split(" ")[-1].strip()

            country_code = "US"
            if not us.states.lookup(state):
                if re.search("[A-Za-z]", zip):
                    country_code = "CA"

            if "au/" in search_url:
                country_code = "AU"

            if "kor/" in page_url:
                country_code = "KR"

            if "sa-i/" in page_url:
                country_code = "SA"

            if "pr/" in page_url:
                country_code = "PR"

            location_type = "<MISSING>"

            hours_of_operation = (
                "; ".join(page_sel.xpath("//p[not(./i)]/text()"))
                .replace(";  ;  ;  ;", "")
                .replace(";  ;  ; ", "")
                .strip()
                .split("; Located")[0]
                .strip()
                .replace("; ,nbsp;", "")
                .strip()
                .split("; Appointments")[0]
                .strip()
                .split("; Christmas Eve")[0]
                .strip()
            )

            if "call the store for more information" in hours_of_operation.lower():
                hours_of_operation = "<MISSING>"

            try:
                latitude = store.split(',"')[2].strip(' "')
                longitude = store.split(',"')[3].strip(' "')
            except IndexError:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

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
