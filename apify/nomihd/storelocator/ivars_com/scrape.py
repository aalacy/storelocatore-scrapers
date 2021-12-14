# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ivars.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.ivars.com/sfb-locations"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@class="sqs-block-content"][./p/a[contains(text(),"Menu")]]/p/a[strong]/@href'
        )
        for store_url in stores:
            page_url = "https://www.ivars.com" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            store_json = json.loads(
                "".join(store_sel.xpath("//div[@data-block-json]/@data-block-json"))
                .strip()
                .replace("&#123;", "{")
                .replace("&#125;", "}")
                .replace("&quot;", '"')
                .strip()
            )["location"]

            locator_domain = website
            location_name = "".join(
                store_sel.xpath(
                    "//div[@class='sqs-block-content'][./p/a[contains(text(),'Menu')]]/p[1]/a//text()"
                )
            ).strip()

            street_address = store_json["addressLine1"]
            city_state_zip = store_json["addressLine2"]
            city = city_state_zip.split(",")[0].strip()
            if len(city_state_zip.split(",")) == 2:
                state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
                zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()
            elif len(city_state_zip.split(",")) == 3:
                state = city_state_zip.split(",")[1].strip()
                zip = city_state_zip.split(",")[-1].strip()

            country_code = "US"
            store_number = "<MISSING>"
            raw_data = store_sel.xpath(
                "//div[@class='sqs-block-content'][./p/a[contains(text(),'Menu')]]/p[1]/text()"
            )
            phone = "<MISSING>"
            if len(raw_data) > 0:
                phone = raw_data[-1]

            location_type = "<MISSING>"
            latitude = store_json["markerLat"]
            longitude = store_json["markerLng"]

            hours_of_operation = (
                "; ".join(
                    store_sel.xpath(
                        "//div[@class='sqs-block-content'][./p/a[contains(text(),'Menu')]]/h3/text()"
                    )
                )
                .strip()
                .replace("Daily;", "Daily:")
                .strip()
            )

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
