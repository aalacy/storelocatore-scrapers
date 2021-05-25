# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "coffeecupfuelstops.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.coffeecupfuelstops.com/hartford-sd"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    stores = list(set(stores_sel.xpath('//div[@class="subnav"]/div/a/@href')))
    for store_url in stores:
        page_url = "https://www.coffeecupfuelstops.com" + store_url
        log.info(page_url)
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
        location_name = store_json["addressTitle"]
        city = store_json["addressLine2"].strip().split(",")[0].strip()
        try:
            street_address = (
                street_address.split(city)[0].strip().replace("l", ", ").strip()
            )
        except:
            pass

        if "," in street_address[-1]:
            street_address = "".join(street_address[:-1]).strip()
        state = store_json["addressLine2"].strip().split(",")[1].strip()
        zip = store_json["addressLine2"].strip().split(",")[-1].strip()

        sections = store_sel.xpath(
            '//div[@class="sqs-block html-block sqs-block-html"]'
        )

        if zip.isalpha():
            if len(sections) > 0:
                zip = (
                    "".join(sections[0].xpath("div/p[1]/text()"))
                    .strip()
                    .split(",")[-1]
                    .strip()
                    .split(" ")[1]
                    .strip()
                )

        country_code = "US"

        store_number = "<MISSING>"
        phone = "".join(store_sel.xpath('//p[contains(text(),"Ph: ")]/text()')).strip()
        try:
            phone = phone.split("Ph: ")[1].strip()
        except:
            pass
        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"
        if len(sections) > 0:
            hours_of_operation = "".join(sections[0].xpath("div/p[2]/text()")).strip()

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
