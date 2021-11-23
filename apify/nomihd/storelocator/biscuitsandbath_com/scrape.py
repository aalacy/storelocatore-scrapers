# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "biscuitsandbath.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.biscuitsandbath.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.biscuitsandbath.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="wp-block-columns"]')
    for store in stores:
        store_url = "".join(
            store.xpath(".//p/span/a[contains(@href,'/locations/')]/@href")
        ).strip()
        page_url = ""
        if "biscuitsandbath" not in store_url:
            page_url = "https://www.biscuitsandbath.com" + store_url
        else:
            page_url = store_url

        log.info(page_url)

        location_type = "<MISSING>"
        locator_domain = website
        location_name = "".join(store.xpath("div[2]/span[1]//text()")).strip()
        if (
            len(location_name) <= 0
            or "COMING SOON"
            in "".join(store.xpath("div[2]/span/span/strong/text()")).strip()
        ):
            continue
        raw_address = store.xpath("div[2]/p[1]/a")
        address = []
        for add in raw_address:
            if "".join(add.xpath("@data-type")).strip() == "tel":
                break
            else:
                address.append("".join(add.xpath("text()")).strip())

        address = ", ".join(address).strip().replace(", NY, NY,", " NY, NY").strip()
        log.info(address)
        street_address = (
            address.split(",")[0]
            .strip()
            .replace("New York", "")
            .replace(" NY", "")
            .strip()
        )
        city = "New York"
        state = address.split(",")[1].strip().split(" ")[0].strip()
        zip = address.split(",")[1].strip().split(" ")[-1].strip()
        country_code = "US"

        phone = "".join(store.xpath('div[2]/p[1]/a[@data-type="tel"]/text()')).strip()
        if len(phone) <= 0:
            phone = "".join(
                store.xpath('div[2]/p[1]/a[contains(@href,"tel:")]/text()')
            ).strip()

        temp_days = store.xpath("div[2]/p[1]/strong/span/text()")
        days_list = []
        for day in temp_days:
            if len("".join(day).strip()) > 0:
                days_list.append("".join(day).strip())

        temp_time = store.xpath("div[2]/p[1]/text()")
        time_list = []
        for time in temp_time:
            if len("".join(time).strip()) > 0:
                time_list.append("".join(time).strip())

        hours_list = []
        for index in range(0, len(days_list)):
            hours_list.append(days_list[index] + time_list[index])

        hours_of_operation = (
            "".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", " ")
            .strip()
        )
        store_number = "<MISSING>"

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
        ).strip()

        if len(map_link) > 0:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
