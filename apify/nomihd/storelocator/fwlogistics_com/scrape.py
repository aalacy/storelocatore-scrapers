# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "fwlogistics.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://fwlogistics.com/warehousing/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath("//div[@class='state-item']")
    for store in stores:

        page_url = "".join(
            store.xpath('.//a[@class="state-item__link-title"]/@href')
        ).strip()
        location_name = "".join(
            store.xpath(".//h3[@class='state-item__title']/text()")
        ).strip()
        location_type = "<MISSING>"
        locator_domain = website

        raw_info = (
            "".join(store.xpath('.//div[@class="state-item__address"]/p[1]/a//text()'))
            .strip()
            .replace("Tracy CA", ",Tracy, CA")
            .split(",")
        )
        street_address = ", ".join(raw_info[:-2]).strip()

        city = raw_info[-2].strip()
        state = raw_info[-1].strip().split(" ", 1)[0].strip()
        zipp = raw_info[-1].strip().split(" ", 1)[-1].strip()
        phone = "".join(
            store.xpath(
                './/div[@class="state-item__address"]/p[contains(text(),"Scheduling")]/a/text()'
            )
        ).strip()
        if phone == "":
            phone = "".join(
                store.xpath(
                    './/div[@class="state-item__address"]/p/a[contains(@href,"tel:")]/text()'
                )
            ).strip()
            if phone == "" or phone == "1-877-FWDRIVE":
                phone = "1-877-393-7483"

        hours_of_operation = "<MISSING>"

        country_code = "US"
        store_number = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store.xpath('.//div[@class="state-item__address"]/p[1]/a/@href')
        ).strip()

        if "/@" in map_link:
            latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
            longitude = map_link.split("/@")[1].strip().split(",")[1]

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
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
