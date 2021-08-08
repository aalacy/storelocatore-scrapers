from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
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

    with SgChrome(is_headless=True) as driver:
        for idx, poi_html in enumerate(all_locations[0:]):
            page_url = poi_html.xpath(".//a/@href")[0]
            page_url = poi_html.xpath(".//a/@href")[0]
            logger.info(f"Page URL: {page_url}")
            driver.get(page_url)
            driver.implicitly_wait(15)
            iframe = driver.find_element_by_xpath("//iframe[contains(@src, 'google')]")
            driver.switch_to.frame(iframe)
            pgsrc = driver.page_source
            loc_dom = html.fromstring(pgsrc, "lxml")

            google_map_data = loc_dom.xpath(
                '//script[contains(text(), "onEmbedLoad")]/text()'
            )
            logger.info(f"\n[{page_url}] Google Map URL Data: \n{google_map_data}\n\n")
            address_from_google_entity_details = (
                "".join(google_map_data)
                .split("GetEntityDetails")[-1]
                .split("reviews")[0]
                .split("[")[-1]
                .split("]")
            )
            logger.info(
                f"\n[{page_url}] Address from Goolge entity details: \n\n{address_from_google_entity_details}\n\n"
            )

            gmd1 = (
                "".join(google_map_data)
                .split("[[[")[2]
                .split("review")[0]
                .split("[[")[-1]
            )
            gmd2 = gmd1.split(",")
            gmd2 = [
                i.replace('"', "").strip().replace("[", "").replace("]", "")
                for i in gmd2
            ]
            logger.info(f"[{idx}] Raw Data from GMap: {gmd2}")

            location_name = gmd2[1]
            location_name = location_name if location_name else MISSING
            logger.info(f"[{idx}] Location Name: {location_name}")

            street_address = gmd2[2]
            street_address = street_address if street_address else MISSING
            logger.info(f"[{idx}] Street Address: {street_address}")

            city = gmd2[3]
            city = city if city else MISSING
            logger.info(f"[{idx}] City: {city}")

            state = gmd2[4].split(" ")[0].strip()
            state = state if state else MISSING
            logger.info(f"[{idx}] State: {state}")

            zip_postal = gmd2[4].split(" ")[1].strip()
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
            latitude = gmd2[5]
            latitude = latitude if latitude else MISSING
            logger.info(f"[{idx}] Latitude: {latitude}")

            longitude = gmd2[6]
            longitude = longitude if longitude else MISSING
            logger.info(f"[{idx}] Longitude: {longitude}")

            # Hours of Operations
            ya = "".join(google_map_data).split("[[[")[3].split("\n")
            ya1 = [i for i in ya[0].split('"') if i]
            ya2 = ya1[0::2]
            ya3 = ya2[0:14]
            hoo = []
            for i in range(0, 7):
                j = ya3[0::2][i] + " " + ya3[1::2][i]
                hoo.append(j)
            hours_of_operation = "; ".join(hoo)
            logger.info(f"[{idx}] HOO: {hours_of_operation}")

            raw_address = poi_html.xpath('.//p[@style="text-align: center;"]/text()')
            raw_address = [e.strip() for e in raw_address if e.strip()]
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
