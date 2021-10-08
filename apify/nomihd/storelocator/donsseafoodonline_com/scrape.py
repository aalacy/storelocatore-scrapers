# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "donsseafoodonline.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.donsseafoodonline.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.donsseafoodonline.com/locations"
    with SgRequests(dont_retry_status_codes=([404]), proxy_country="us") as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//span[@class="Header-nav-item Header-nav-item--folder"][./a[contains(text(),"Locations")]]/span/a/@href'
        )
        for store_url in stores:
            page_url = "https://www.donsseafoodonline.com" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            locator_domain = website
            store_json_text = (
                "".join(
                    store_sel.xpath(
                        '//div[contains(@class,"sqs-block map-block sqs-block-map")]/@data-block-json'
                    )
                )
                .strip()
                .replace("&#123;", "{")
                .replace("&quot;", '"')
                .replace("&#125;", "}")
            )
            store_json = json.loads(store_json_text)["location"]
            location_name = (
                "".join(store_sel.xpath('//div[@class="sqs-block-content"]/h1/text()'))
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "'")
                .strip()
            )

            street_address = store_json["addressLine1"]
            city = store_json["addressLine2"].strip().split(",")[0].strip()
            state_zip = store_json["addressLine2"].strip().split(",", 1)[-1].strip()
            if "," in state_zip:
                state = state_zip.split(",")[0].strip()
                zip = state_zip.split(",")[-1].strip()
            else:
                state = state_zip.split(" ")[0].strip()
                zip = state_zip.split(" ")[-1].strip()

            country_code = "US"

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath('//p[./strong[contains(text(),"Phone:")]]/a/text()')
            ).strip()
            location_type = "<MISSING>"

            hours = store_sel.xpath(
                '//div[@class="sqs-block-content"]/p[./strong[contains(text(),"Hours")]]/following-sibling::p/text()'
            )
            hours_of_operation = "; ".join(hours).strip()

            latitude = store_json["markerLat"]
            longitude = store_json["markerLng"]

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
