from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgselenium import SgChrome
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "worldwidegolfshops.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    LOCATION_URL = "https://www.worldwidegolfshops.com/golfers-warehouse.aspx/"

    with SgRequests() as session:
        with SgChrome() as driver:
            stores_req = session.get(LOCATION_URL)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath(
                '//div[@class="vtex-rich-text-0-x-wrapper vtex-rich-text-0-x-wrapper--StoreLocationText"]/h3/a/@href'
            )
            for store_url in stores:
                locator_domain = website
                page_url = "https://www.worldwidegolfshops.com" + store_url.strip()
                log.info(page_url)
                driver.get(page_url)
                store_sel = lxml.html.fromstring(driver.page_source)
                location_name = "".join(
                    store_sel.xpath(
                        '//h1[contains(@class,"vtex-yext-store-locator-0-x-storeTitle")]/text()'
                    )
                ).strip()

                main = driver.find_element_by_css_selector(
                    "script[type='application/ld+json']"
                ).get_attribute("innerHTML")
                data = json.loads(main)
                street_address = data["address"]["streetAddress"]
                city = data["address"]["addressLocality"]
                state = data["address"]["addressRegion"]
                zip = data["address"]["postalCode"]
                country_code = "US"
                phone = data["telephone"]
                hours_of_operation = (
                    (
                        "; ".join(
                            store_sel.xpath(
                                '//div[@class="vtex-yext-store-locator-0-x-normalHours"]//text()'
                            )
                        ).strip()
                    )
                    .replace("\n", "; ")
                    .replace("STORE HOURS;", "")
                    .replace("day;", "day:")
                    .strip()
                )
                store_number = data["@id"]
                location_type = "<MISSING>"
                latitude = data["geo"]["latitude"]
                longitude = data["geo"]["longitude"]
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
