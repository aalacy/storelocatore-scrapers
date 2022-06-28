# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "brassicas.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.brassicas.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://brassicas.com/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    stores_list = search_sel.xpath(
        '//div[@data-controller-folder="locationslist"]//a/@href'
    )
    for store_url in stores_list:
        if "/locations" in store_url:
            continue
        page_url = "https://www.brassicas.com" + store_url
        locator_domain = website
        log.info(page_url)
        page_res = session.get(page_url, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)

        location_name = "".join(page_sel.xpath("//h1/text()")).strip()

        details_info = list(
            filter(
                str,
                page_sel.xpath(
                    '//div[@class="col sqs-col-6 span-6"][.//a[contains(text(),"Order Online")]]//div[@class="sqs-block-content"]/h3/text()'
                ),
            )
        )

        store_json_text = (
            "".join(
                page_sel.xpath(
                    '//div[@class="sqs-block map-block sqs-block-map sized vsize-12"]/@data-block-json'
                )
            )
            .strip()
            .replace("&#123;", "{")
            .replace("&quot;", '"')
            .replace("&#125;", "}")
        )

        store_json = json.loads(store_json_text)["location"]

        street_address = store_json["addressLine1"]

        addressLine2 = store_json["addressLine2"]
        city = addressLine2.split(",")[0].strip()

        state = addressLine2.split(",")[1].strip()
        zip = addressLine2.split(",")[2].strip()

        country_code = "US"

        store_number = "<MISSING>"

        phone = details_info[-2].strip()

        location_type = "<MISSING>"

        hours_of_operation = details_info[-1].strip()

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
