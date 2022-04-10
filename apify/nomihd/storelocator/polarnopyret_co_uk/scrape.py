# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "polarnopyret.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.polarnopyret.co.uk/pages/store-locator"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@class="shg-row" and @data-col-grid-mode-on="true"]'
        )
        for store in stores:
            page_url = search_url

            locator_domain = website
            location_name = "".join(store.xpath("div[1]//p[1]//text()")).strip()

            raw_address = store.xpath("div[1]//p[position()>1]//text()")
            formatted_addr = parser.parse_address_intl(
                ", ".join(raw_address[:-1]).strip()
            )
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            if not city:
                city = ", ".join(raw_address[:-1]).strip().split(",")[-2].strip()

            state = formatted_addr.state
            zip = formatted_addr.postcode
            country_code = "GB"

            store_number = "<MISSING>"
            phone = raw_address[-1].strip().split("Ext:")[0].strip()

            location_type = "<MISSING>"

            hours_of_operation = (
                "; ".join(store.xpath("div[2]//p//text()"))
                .strip()
                .replace("Normal Hours;", "")
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "")
                .strip()
                .replace(";;", "")
                .strip()
                .split("; Bank")[0]
                .strip()
            )
            if hours_of_operation:
                if ";" == hours_of_operation[-1]:
                    hours_of_operation = "".join(hours_of_operation[:-1]).strip()

            latitude = "".join(
                store.xpath("div[3]//div[@class='shg-map-container']/@data-latitude")
            ).strip()
            longitude = "".join(
                store.xpath("div[3]//div[@class='shg-map-container']/@data-longitude")
            ).strip()

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
                raw_address=", ".join(raw_address[:-1]).strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
