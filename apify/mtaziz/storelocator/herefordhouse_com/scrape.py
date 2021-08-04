from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgFirefox
from lxml import html


DOMAIN = "herefordhouse.com"
logger = SgLogSetup().get_logger("herefordhouse_com")
MISSING = SgRecord.MISSING

LOCATION_URL = "https://herefordhouse.com/locations"


def fetch_data():
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=5, backoff_factor=0.3)
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(LOCATION_URL, headers=hdr)
    dom = html.fromstring(response.text, "lxml")

    all_locations = dom.xpath(
        '//div[@class="entry-content"]/div/div[@class="wpb_column vc_column_container vc_col-sm-3"]'
    )
    for idx, poi_html in enumerate(all_locations[0:]):
        with SgFirefox() as driver:
            page_url = poi_html.xpath(".//a/@href")[0]
            driver.get(page_url)
            driver.implicitly_wait(15)
            logger.info("Page being loaded!!")
            iframe = driver.find_element_by_xpath("//iframe[contains(@src, 'google')]")
            driver.switch_to.frame(iframe)
            logger.info("iframe Loaded!!")
            loc_dom = html.fromstring(driver.page_source, "lxml")
            driver.switch_to.default_content()
            logger.info("Switched back to default content!!")

            location_name = "".join(loc_dom.xpath('//h1[@id="page-title"]/text()'))
            location_name = location_name if location_name else MISSING
            logger.info(f"[{idx}] Location Name: {location_name}")

            raw_address = poi_html.xpath('.//p[@style="text-align: center;"]/text()')
            raw_address = [e.strip() for e in raw_address if e.strip()]

            # Raw address being parsed here
            street_address = raw_address[0].strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            logger.info(f"[{idx}] Street Address: {street_address}")

            city = raw_address[-1].split(", ")[0]
            city = city if city else MISSING
            logger.info(f"[{idx}] City: {city}")

            state = raw_address[-1].split(", ")[-1]
            state = state if state else MISSING
            logger.info(f"[{idx}] State: {state}")

            zip_postal = loc_dom.xpath('//div[@class="address"]/text()')[0].split()[-1]
            zip_postal = zip_postal if zip_postal else MISSING
            logger.info(f"[{idx}] Zip Postal: {zip_postal}")

            country_code = "US"
            store_number = MISSING
            phone = loc_dom.xpath('//strong[contains(text(), "CALL NOW")]/text()')
            if not phone:
                phone = poi_html.xpath(".//strong/text()")
            phone = phone[0].split("NOW")[-1].strip() if phone else MISSING
            logger.info(f"[{idx}] Phone: {phone}")

            location_type = MISSING
            latlng = "".join(
                loc_dom.xpath('//div[@jsaction="placeCard.directions"]/a/@href')
            )
            latlng = latlng.split("@")[1].split(",")

            latitude = latlng[0]
            latitude = latitude if latitude else MISSING
            logger.info(f"[{idx}] Latitude: {latitude}")

            longitude = latlng[1]
            longitude = longitude if longitude else MISSING
            logger.info(f"[{idx}] Longitude: {longitude}")
            hoo = loc_dom.xpath(
                '//h4[contains(text(), "Dine-in Hours:")]/following-sibling::p//text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else MISSING
            logger.info(f"[{idx}] HOO: {hours_of_operation}")

            raw_address = [i.lstrip(",").rstrip(",") for i in raw_address]
            raw_address = ", ".join(raw_address)
            raw_address = raw_address if raw_address else MISSING
            logger.info(f"[{idx}] Raw Address: {raw_address}")

            yield SgRecord(
                locator_domain=DOMAIN,
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
