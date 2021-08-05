# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "applianceplusonline.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.applianceplusonline.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json",
    "cache-control": "no-cache, no-store, must-revalidate",
    "language": "null",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
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

    search_url = "https://www.applianceplusonline.com/api/rest/pages/contacts"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.json()["content"])
    stores = stores_sel.xpath(
        '//avb-link[contains(text(),"Contact this location")]/@data-href'
    )
    for store_url in stores:

        page_url = store_url
        log.info(page_url)
        page_url = (
            "https://www.applianceplusonline.com/api/rest/pages/"
            + page_url.split("/")[-1].strip()
        )
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.json()["content"])

        location_type = "<MISSING>"
        locator_domain = website

        raw_address = list(
            filter(
                str,
                store_sel.xpath('//span[@class="dsg-contact-1__address-line"]/text()'),
            )
        )
        street_address = raw_address[0].strip()
        city = raw_address[1].strip().split(",")[0].strip()
        state_zip = raw_address[1].strip().split(",")[-1].strip()
        state = state_zip.split(" ")[0].strip()
        zip = state_zip.split(" ")[-1].strip()

        location_name = city

        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(store_sel.xpath('//avb-link[contains(@data-href,"tel:")]/text()'))
            .strip()
            .strip()
        )

        hours = list(
            filter(
                str,
                store_sel.xpath(
                    '//div[@class="dsg-contact-1__content"][./h2[contains(text(),"Hours")]]/ul[1]/li/text()'
                ),
            )
        )

        hours_of_operation = "; ".join(hours)

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
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
