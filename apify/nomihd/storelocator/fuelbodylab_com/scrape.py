# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "fuelbodylab.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.fuelbodylab.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.fuelbodylab.com/contact"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath(
        "//div[@class='col sqs-col-4 span-4']/div[@class='sqs-block html-block sqs-block-html']/div[@class='sqs-block-content']"
    )
    json_list = search_sel.xpath(
        "//div[@class='col sqs-col-4 span-4']/div[@class='sqs-block map-block sqs-block-map']"
    )

    for index, store in enumerate(store_list):

        page_url = search_url
        locator_domain = website

        location_name = "".join(store.xpath("./p/strong/text()")).strip()

        add_and_phone = list(
            filter(
                str,
                [x.strip() for x in store.xpath("./p/text()")],
            )
        )

        street_address = add_and_phone[0]
        store_json = json.loads(
            "".join(json_list[index].xpath("@data-block-json"))
            .strip()
            .replace("&#123;", "{")
            .replace("{&quot;", '"')
            .replace("&#125;", "}")
            .strip()
        )["location"]
        city_state_zip = store_json["addressLine2"].replace("DC,", "DC").strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()
        country_code = "US"

        store_number = "<MISSING>"
        phone = add_and_phone[-1].strip()

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
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
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
