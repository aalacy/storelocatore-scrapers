from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from lxml import html
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("midas_com")
MISSING = SgRecord.MISSING
DOMAIN = "https://www.midas.com"
SITEMAP_URL = "https://www.midas.com/tabid/697/default.aspx"
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    r1 = http.get(SITEMAP_URL, headers=headers)
    d1 = html.fromstring(r1.text, "lxml")
    us_state_urls = d1.xpath(
        '//div[h2[contains(text(), "Midas Stores - United States")]]/ul/li/a/@href'
    )
    logger.info(f"total count for the USA: {us_state_urls}")
    us_state_urls = [f"{DOMAIN}{url}" for url in us_state_urls]
    ca_state_urls = d1.xpath(
        '//div[h2[contains(text(), "Midas Stores - Canada")]]/ul/li/a[contains(@href, "sitemap.aspx?country=CA")]/@href'
    )
    ca_state_urls = [f"{DOMAIN}{url}" for url in ca_state_urls]
    us_ca_state_urls = us_state_urls + ca_state_urls
    for u in us_ca_state_urls:
        logger.info(f"Pulling the store URLs from: {u}")
        r2 = http.get(u, headers=headers)
        d2 = html.fromstring(r2.text, "lxml")
        store_url_list = d2.xpath(
            '//ul[@class="list"]/li/a[contains(@class, "link")]/@href'
        )
        store_url_list = [f"{DOMAIN}{sul}" for sul in store_url_list]
        logger.info(f"Found: {len(store_url_list)}")
        for store_url in store_url_list:
            state.push_request(SerializableRequest(url=store_url))

    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    # Your scraper here

    idx = 0
    for next_r in state.request_stack_iter():
        store_url = next_r.url
        logger.info(f"[{idx}] Pulling the data from: {store_url} ")
        store_number = store_url.split("shopnum=")[-1].split("&dmanum")[0]
        get_store_details_by_shopnum = (
            f"https://www.midas.com/shop/getstorebyshopnumber?shopnum={store_number}"
        )
        poi = http.get(
            get_store_details_by_shopnum.format(store_number), headers=headers
        ).json()
        location_name = poi["Name"]
        location_name = location_name if location_name else "<MISSING>"
        page_url = store_url
        locator_domain = DOMAIN
        street_address = poi["Address"]
        street_address = street_address if street_address else "<MISSING>"

        city = poi["City"]
        city = city if city else "<MISSING>"

        state = poi["State"]
        state = state if state else "<MISSING>"

        zip_postal = poi["ZipCode"]
        zip_postal = zip_postal if zip_postal else "<MISSING>"

        country_code = poi["Country"]
        country_code = country_code if country_code else "<MISSING>"

        store_number = poi["ShopNumber"]
        store_number = store_number if store_number else "<MISSING>"

        phone = poi["PhoneNumber"]
        phone = phone if phone else "<MISSING>"

        location_type = MISSING
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"

        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        for i in poi["GroupDaysList"]:
            dayhours = i["DayLabel"] + " " + i["HoursLabel"]
            hoo.append(dayhours)
        hours_of_operation = "; ".join(hoo)
        hours_of_operation = hours_of_operation if hours_of_operation else MISSING
        raw_address = MISSING
        idx += 1
        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
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
    logger.info("Started")
    state = CrawlStateSingleton.get_instance()
    count = 0
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            for rec in fetch_records(http, state):
                writer.write_row(rec)
                count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
