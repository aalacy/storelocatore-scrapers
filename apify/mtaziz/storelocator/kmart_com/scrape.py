from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from lxml import html


logger = SgLogSetup().get_logger("kmart_com")
DOMAIN = "https://www.kmart.com/"
LOCATION_URL = url = "https://www.kmart.com/stores.html"
MISSING = SgRecord.MISSING
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}


def get_store_urls():
    with SgRequests() as session:
        store_urls = []
        state_codes = []
        r_base = session.get(LOCATION_URL, headers=headers)
        r_base_data = html.fromstring(r_base.text, "lxml")
        logger.info("crawling from base url:%s" % url)
        state_urls = r_base_data.xpath('//li[contains(@class, "state")]/a/@href')
        logger.info(f"Number of States to be Crawled: {len(state_urls)}")
        state_urls = ["https://www.kmart.com" + state_slug for state_slug in state_urls]
        for statenum, state_url in enumerate(state_urls[0:]):
            logger.info(f"[{statenum}] State URL: {state_url}")
            r_state = session.get(state_url, headers=headers)
            sel_state = html.fromstring(r_state.text, "lxml")
            store_slugs = sel_state.xpath(
                '//li[contains(@class, "details__list")]/a/@href'
            )
            logger.info(f"{state_url}: {store_slugs}")
            state_code_list = sel_state.xpath(
                '//li[contains(@class, "details__list")]/a/span[1]/text()'
            )
            state_code_list = [i.split(",")[-1] for i in state_code_list]
            if store_slugs:
                store_urls.extend(store_slugs)
                state_codes.extend(state_code_list)

        store_urls = ["https://www.kmart.com" + store_slug for store_slug in store_urls]
        logger.info(f"Total number of stores found: {len(store_urls)}")
        return (state_codes, store_urls)


def fetch_records():
    state_codes, store_urls_from_all_states = get_store_urls()
    with SgRequests() as session:
        for idx, purl in enumerate(store_urls_from_all_states[0:]):
            r = session.get(purl)
            sel = html.fromstring(r.text, "lxml")
            locator_domain = DOMAIN
            page_url = purl
            st = sel.xpath(
                '//p[contains(@class, "location__details--address")]/span/text()'
            )
            st = st[0:2]
            street_address = st[0] if st[0] else MISSING
            logger.info(f"[{idx}] Street Address: {street_address}")

            city = sel.xpath('//h1[contains(@class, "store__title")]/@data-city')
            city = "".join(city)
            city = city if city else MISSING
            logger.info(f"[{idx}] City: {city}")

            state = state_codes[idx]
            state = state if state else MISSING
            logger.info(f"[{idx}] State: {state}")

            zc = st[1].split(",")[-1].strip()
            zip_postal = zc if zc else MISSING
            logger.info(f"[{idx}] Zip Code: {zip_postal}")

            country_code = "US"
            store_number = sel.xpath(
                '//h1[contains(@class, "store__title")]/@data-unit-number'
            )
            store_number = "".join(store_number)

            phone = sel.xpath(
                '//div[h3[contains(text(), "Store Location")]]/strong/text()'
            )
            phone = [i for i in phone]
            phone = phone[0]
            phone = phone if phone else MISSING
            logger.info(f"[{idx}]  Phone: {phone}")

            location_type = MISSING

            location_name = f"Kmart {city} #{store_number}"
            logger.info(f"[{idx}] location_name: {location_name}")

            lat = sel.xpath(
                '//div[contains(@class, "store-map")]/div[contains(@class, "store-location")]/@data-latitude'
            )
            lat = lat[0]
            latitude = lat if lat else MISSING
            logger.info(f"[{idx}] latitude: {latitude}")

            lng = sel.xpath(
                '//div[contains(@class, "store-map")]/div[contains(@class, "store-location")]/@data-longitude'
            )
            lng = lng[0]
            longitude = lng if lng else MISSING
            logger.info(f"[{idx}] longitude: {longitude}")

            hoos1 = sel.xpath('//div[h3[contains(text(), "Store Hours")]]/div/ul')
            for hoo in hoos1[0:1]:
                days = hoo.xpath('./li/span[contains(@class, "day")]/text()')
                timings = hoo.xpath('./li/span[contains(@class, "timing")]/text()')
            hours_of_operation = []
            for daynum, timing in enumerate(timings):
                dt = days[daynum] + " " + timing
                hours_of_operation.append(dt)
            hours_of_operation = "; ".join(hours_of_operation)
            logger.info(f"Hours of operation: {hours_of_operation}")

            raw_address = ""
            raw_address = raw_address if raw_address else MISSING
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
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        results = fetch_records()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
