# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "jhootspharmacy.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "http://www.jhootspharmacy.co.uk/"
    search_url = "http://www.jhootspharmacy.co.uk/jhoots-pharmacy-branches.htm"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath("//option[@value]")
        for no, store in enumerate(stores, 1):

            locator_domain = website
            store_number = "<MISSING>"

            page_url = (
                base
                + "".join(store.xpath("./text()")).strip().replace(" ", "-").lower()
                + "_branch.htm"
            )
            log.info(page_url)

            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            location_name = "".join(
                store_sel.xpath('//div[@id="branch_details"]//h1/text()')
            ).strip()

            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@id="branch_details"]//span//text()'
                        )
                    ],
                )
            )

            phone = (
                " ".join(store_info)
                .split("Tel:")[1]
                .split("Fax:")[0]
                .strip()
                .split("/")[0]
                .strip()
            )

            raw_address = " ".join(store_info).split("Tel:")[0].strip()
            street_address = ", ".join(raw_address.split(",")[:-1]).strip()
            city = raw_address.split(",")[-1].strip().rsplit(" ", 2)[0].strip()
            state = "<MISSING>"
            zip = " ".join(raw_address.split(",")[-1].strip().split(" ", 2)[1:]).strip()

            country_code = "GB"

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@id="branch_details"]//div[@class="day font" or @class="time font"]//text()'
                        )
                    ],
                )
            )

            hours_of_operation = (
                "; ".join(hours)
                .replace("day; ", "day: ")
                .replace("day:;", "day:")
                .replace("OPEN FOR BUSINESS!", "")
                .replace("NOW OPEN!", "")
                .strip(";! ")
            )

            latitude, longitude = "<MISSING>", "<MISSING>"

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
