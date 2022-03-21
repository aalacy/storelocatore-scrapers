# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json

website = "sunrisetreatmentcenter.net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.sunrisetreatmentcenter.net",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.sunrisetreatmentcenter.net/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="col sqs-col-3 span-3"]//a/@href')
    for store_url in stores:
        if "/staff/corporate" == store_url:
            continue
        page_url = "https://www.sunrisetreatmentcenter.net" + store_url.replace(
            "/staff/", "/locations/"
        )
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        street_address = store_sel.xpath(
            '//div[@class="sqs-block html-block sqs-block-html"]/div/p[1]/text()'
        )
        if len(street_address) > 0:
            street_address = street_address[0]

        locator_domain = website
        store_json_text = (
            "".join(
                store_sel.xpath(
                    '//div[@class="sqs-block map-block sqs-block-map sized vsize-12"]/@data-block-json'
                )
            )
            .strip()
            .replace("&#123;", "{")
            .replace("&quot;", '"')
            .replace("&#125;", "}")
        )

        store_json = json.loads(store_json_text)["location"]
        location_name = "".join(
            store_sel.xpath('//div[@class="sqs-block-content"]/h1/text()')
        ).strip()

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
        phone = (
            "".join(store_sel.xpath('//a[contains(text(),"CALL NOW")]/@href'))
            .strip()
            .replace("tel:", "")
            .strip()
        )
        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
