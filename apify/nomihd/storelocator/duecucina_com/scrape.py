# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "duecucina.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "duecucina.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://duecucina.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://duecucina.com/locations/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    asr_ajax_nonce = (
        session.get("https://duecucina.com/locations/", headers=headers)
        .text.split('"asr_ajax_nonce":"')[1]
        .strip()
        .split('"')[0]
        .strip()
    )
    data = {
        "action": "asr_filter_posts",
        "asr_ajax_nonce": asr_ajax_nonce,
        "term_ID": "-1",
        "layout": "1",
        "jsonData": '{"show_filter":"yes","btn_all":"yes","initial":"-1","layout":"1","post_type":"restuarent-cpt","posts_per_page":18,"paginate":"no"}',
    }
    search_url = "https://duecucina.com/wp-admin/admin-ajax.php"
    stores_req = session.post(search_url, headers=headers, data=data)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[contains(@id,"returanItem-")]')
    for store in stores:

        page_url = "".join(
            store.xpath(".//a[contains(text(),'View Details')]/@href")
        ).strip()

        locator_domain = website

        location_name = "".join(store.xpath("@data-title")).strip()
        if "COMING SOON" in location_name.upper():
            continue
        raw_address = "".join(
            store.xpath('.//p[@class="resturent_address"]/text()')
        ).strip()

        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "US"

        store_number = "<MISSING>"

        phone = "".join(
            store.xpath('.//p[@class="resturent_address phoneNo"]/text()')
        ).strip()

        location_type = "<MISSING>"
        hours_of_operation = "; ".join(
            store.xpath('.//p[@class="resturent_time_open"]/text()')
        ).strip()

        latitude = "".join(store.xpath("@data-lat")).strip()
        longitude = "".join(store.xpath("@data-lng")).strip()

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
            raw_address=raw_address,
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
