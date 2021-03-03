# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "carlosokellys.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://carlosokellys.com/all-locations.html"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    stores = stores_sel.xpath('//div[@class="productBoxes"]')
    for store in stores:
        page_url = "https://carlosokellys.com" + "".join(store.xpath("a/@href")).strip()
        location_type = "<MISSING>"
        locator_domain = website
        location_name = (
            "".join(store.xpath("a/span/text()"))
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

        raw_info = store.xpath('div[@class="moduleItemIntrotext"]/p')
        if len(raw_info) > 0:
            raw_info = raw_info[-1].xpath("text()")

        add_list = []
        for add in raw_info:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = add_list[0].strip()
        city_state_zip = add_list[-1].strip()
        city = ""
        state = ""
        zip = ""
        if "," in city_state_zip:
            city = city_state_zip.split(",")[0].strip()
            state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
            zip = city_state_zip.split(",")[1].strip().split(" ")[1].strip()
        else:
            city = city_state_zip.split(" ")[0].strip()
            state = city_state_zip.split(" ")[1].strip()
            zip = city_state_zip.split(" ")[-1].strip()

        country_code = "US"

        phone = "".join(
            store.xpath(
                'div[@class="moduleItemIntrotext"]/p[@class="mainPhone"]/strong/text()'
            )
        ).strip()

        hours_of_operation = (
            "".join(
                store.xpath(
                    'div[@class="moduleItemIntrotext"]/p[contains(text(),"New Hours:")]/text()'
                )
            )
            .strip()
            .replace("New Hours:", "")
            .strip()
        )
        if len(hours_of_operation) <= 0:
            hours = store.xpath('div[@class="moduleItemIntrotext"]/p')
            for hour in hours:
                if "New Hours:" in "".join(hour.xpath(".//text()")).strip():
                    hours_of_operation = (
                        hour.xpath("text()")[-1]
                        .strip()
                        .replace("New Hours:", "")
                        .strip()
                    )

        store_number = "<MISSING>"

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
