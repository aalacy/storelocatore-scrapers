import json
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from lxml import html

DOMAIN = "partycity.com"
logger = SgLogSetup().get_logger(logger_name="partycity_com")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

MISSING = SgRecord.MISSING


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url = "https://stores.partycity.com/us/"
    store_url_list = []
    http = SgRequests()
    r1 = http.get(url, headers=headers)
    sel1 = html.fromstring(r1.text, "lxml")
    state_list = sel1.xpath(
        '//div[@class="tlsmap_list"]/div/div/a[@class="gaq-link"]/@href'
    )
    for idx1, state_url in enumerate(state_list[0:]):
        r2 = http.get(state_url, headers=headers, timeout=180)
        sel2 = html.fromstring(r2.text, "lxml")
        city_list = sel2.xpath(
            '//div[contains(@class, "map-list-item")]/a[contains(@class, "gaq-link")]/@href'
        )
        logger.info(f"city_list: {city_list}")
        for city_url in city_list:
            r3 = http.get(city_url, headers=headers, timeout=180)
            sel3 = html.fromstring(r3.text, "lxml")
            loclist = sel3.xpath(
                '//div[contains(@class, "map-list-item-section")]/a[contains(@class, "gaq-link store-info")]/@href'
            )
            for loc in loclist:
                store_url_list.append(loc)
                logger.info(loc)
                state.push_request(SerializableRequest(url=loc))
    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        r = http.get(next_r.url, headers=headers, timeout=180)
        logger.info(f"Pulling the data from: {next_r.url}")
        sel = html.fromstring(r.text, "lxml")
        js = sel.xpath("//script[@type='application/ld+json']/text()")
        js = "".join(js)
        loc = json.loads(js)[0]
        page_url = next_r.url
        country_code = "US"
        address = loc["address"] or MISSING
        street_address = address["streetAddress"] or MISSING
        city = address["addressLocality"] or MISSING
        state = address["addressRegion"] or MISSING
        zip_postal = address["postalCode"] or MISSING
        phone = address["telephone"] or MISSING
        coords = loc["geo"]
        latitude = coords["latitude"] or MISSING
        longitude = coords["longitude"] or MISSING
        hours_of_operation = loc["openingHours"] or MISSING
        location_name = loc["mainEntityOfPage"]["headline"] or MISSING
        try:
            store_number = page_url.split("pc")[-1].split(".")[0]
        except:
            store_number = MISSING
        location_type = MISSING
        raw_address = MISSING
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
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
