# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "tubby.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.tubbys.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.tubbys.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@role="gridcell"]')
    for store in stores:
        page_url = "".join(
            store.xpath('.//a[@style="cursor:pointer"]/@href')[-1]
        ).strip()
        locator_domain = website

        location_name = "".join(store.xpath(".//h2//text()")).strip()

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        address = store_sel.xpath("//div[@data-packed='false'][1]//text()")
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = "".join(add_list[0]).strip()
        city = add_list[1]
        state_zip = add_list[2].replace(",", "").strip()
        state = state_zip.split(" ")[0].strip()
        if state == "City":
            state = "MI"
            city = "Imlay City"

        zip = state_zip.split(" ")[-1].strip()
        country_code = "US"

        store_number = page_url.split("-")[-1].strip()
        phone = "".join(
            store.xpath('.//p//a[contains(@href,"tel:")][1]//text()')
        ).strip()

        location_type = "<MISSING>"
        hours = store_sel.xpath('//p[@style="font-size:16px; line-height:1.5em;"]/span')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("span[1]/text()")).strip()
            time = "".join(hour.xpath("span[2]/text()")).strip()
            hours_list.append(day + time)

        if len(hours_list) <= 0:
            hours = store_sel.xpath(
                '//div[@data-packed="true"]/p[@class="font_8" and not(@style)]'
            )
            for hour in hours:
                hours_list.append("".join(hour.xpath(".//text()")).strip())

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .replace("; ; ", "")
            .replace(":;", ":")
            .strip()
            .replace("; AM", "AM;")
            .replace("-;", "-")
            .strip()
            .replace("; -", "-")
            .replace(";;", ";")
            .strip()
            .replace("; PM", "PM")
        )
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
