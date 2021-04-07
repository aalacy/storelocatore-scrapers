# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "halfshelloysterhouse.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.halfshelloysterhouse.com/location"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="col sqs-col-6 span-6"]/div[@class="sqs-block html-block sqs-block-html"]'
    )
    for store in stores:
        page_url = search_url

        locator_domain = website
        location_name = "".join(
            store.xpath("div[@class='sqs-block-content']/h3/text()")
        ).strip()
        address = "".join(
            store.xpath("div[@class='sqs-block-content']/p[1]/text()")
        ).strip()

        street_address = address.split(",")[0].strip()
        city = address.split(",")[1]
        state = address.split(",")[-1].strip().split(" ")[0].strip()
        zip = address.split(",")[-1].strip().split(" ")[-1].strip()
        country_code = "US"

        phone = "".join(
            store.xpath("div[@class='sqs-block-content']/p[1]/strong/text()")
        )

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        hours_of_operation = ""
        hours = None
        hours_list = []
        sections = store.xpath("div[@class='sqs-block-content']/p")
        for index in range(0, len(sections)):
            if (
                "Hours of Operation"
                in "".join(sections[index].xpath("strong/text()")).strip()
            ):
                hours = sections[index + 1 :]

        if hours is not None:
            for hour in hours:
                hours_list.append("".join(hour.xpath("text()")).strip())

        hours_of_operation = "; ".join(hours_list).strip().replace(".;", ";").strip()

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
