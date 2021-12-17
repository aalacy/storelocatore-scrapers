# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import us

website = "studiomoviegrill.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://www.studiomoviegrill.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="location-box"]')
    for store in stores:
        page_url = (
            "https://www.studiomoviegrill.com"
            + "".join(store.xpath("h3/a/@href")).strip()
            + "/"
        )

        locator_domain = website
        location_name = "".join(store.xpath("h3/a/text()")).strip()

        add_list = []
        address = store.xpath('p[@class="info"]/a[@target="_blank"]/text()')
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = add_list[0].strip()
        city = add_list[1].strip().split(",")[0].strip()
        state = add_list[1].strip().split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[1].strip().split(",")[1].strip().split(" ")[-1].strip()

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        store_number = "<MISSING>"
        phone = "".join(
            store.xpath('p[@class="info"]/a[contains(@href,"tel:")]/text()')
        ).strip()
        raw_text = store.xpath('p[@class="info"]/span[@class="caps"]/b/text()')
        location_type = "<MISSING>"
        if "RE-OPENING" not in ", ".join(raw_text).strip():
            if "OPENING" in ", ".join(raw_text).strip():
                location_type = "Coming Soon"
            if "TEMPORARILY CLOSED" in ", ".join(raw_text).strip():
                location_type = "TEMPORARILY CLOSED"

        hours_list = []
        for index in range(0, len(raw_text)):
            if "SPRING BRK" in raw_text[index]:
                continue
            else:
                hours_list.append(raw_text[index])

        hours_of_operation = "; ".join(hours_list).strip()

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        map_link = "".join(
            store_sel.xpath('//p[@class="google-map"]/iframe/@src')
        ).strip()
        latitude, longitude = get_latlng(map_link)

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
