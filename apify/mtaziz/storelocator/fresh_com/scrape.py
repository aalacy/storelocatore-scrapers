from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.firefox import GeckoDriverManager
from sgselenium import SgFirefox
from lxml import html


STORE_LOCATOR = "https://www.fresh.com/us/stores"
logger = SgLogSetup().get_logger("fresh_com")
MISSING = SgRecord.MISSING


def fetch_data():
    with SgFirefox(
        executable_path=GeckoDriverManager().install(), block_third_parties=True
    ) as driver:
        driver.get(STORE_LOCATOR)
        logger.info(f"Pulling the content from {STORE_LOCATOR}")
        driver.implicitly_wait(30)
        pgsrcf = driver.page_source
        sel = html.fromstring(pgsrcf, "lxml")
        divs_bout = sel.xpath('//div[@id="boutique"]/div')
        for idx, div in enumerate(divs_bout[0:]):
            store_number = "".join(div.xpath("./@data-store-id"))
            location_name = "".join(
                div.xpath('.//a[@class="store_heading"]/@aria-label')
            )
            coord = div.xpath('.//a[@class="store_heading"]/@data-store-coord')
            lat = ""
            lng = ""
            lat = coord[0].split(",")[0]
            lng = coord[0].split(",")[1]
            store_state = div.xpath('.//span[@class="store-state"]/text()')
            store_state = "".join(store_state).replace(", ", "")
            state = ""
            if store_state:
                state = store_state
            store_hours = div.xpath('.//*[@class="store_hours"]/text()')
            store_hours = "".join(store_hours)
            location_type = "".join(
                div.xpath('.//address/div[@class="show-in-map"]/@data-store-type')
            )
            raw_address = div.xpath('.//address/div[@class="show-in-map"]/text()')
            raw_address = "".join(raw_address)
            ra = " ".join(raw_address.split())
            phone = "".join(div.xpath('.//div[@class="store_phone"]/span/text()'))
            logger.info(f"[{idx}] [Phone] [{phone}]")
            pa = parse_address_intl(ra)
            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING
            city = pa.city
            city = city.strip() if city else MISSING
            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            if "US" in store_number:
                country_code = "US"
            else:
                country_code = MISSING
            item = SgRecord(
                locator_domain="fresh.com",
                page_url="https://www.fresh.com/us/stores",
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state,
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=location_type,
                latitude=lat,
                longitude=lng,
                hours_of_operation=store_hours.strip(),
                raw_address=ra,
            )
            yield item


def scrape():
    logger.info("Scrape Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
