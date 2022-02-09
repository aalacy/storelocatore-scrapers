from sgselenium import SgChrome
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import ssl
import lxml.html

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("saintlukeshealthsystem_org")


def parse_addy(addy):
    arr = addy.split(",")
    if len(arr) == 4:
        arr = [arr[0], arr[2], arr[3]]
    street_address = arr[0].strip()
    city = arr[1].strip()
    state_zip = arr[2].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]

    return street_address, city, state, zip_code


def fetch_data():
    locator_domain = "https://www.saintlukeskc.org/"

    with SgChrome() as driver:
        driver.get(locator_domain)
        driver.implicitly_wait(5)

        search_url = "https://www.saintlukeskc.org/location?serviceline_speciality=&field_location_type_target_id=All#"
        while True:
            logger.info(search_url)
            driver.get(search_url)
            driver.implicitly_wait(5)

            stores_sel = lxml.html.fromstring(driver.page_source)
            locs = stores_sel.xpath("//div[@class='geolocation-location js-hide']")
            for loc in locs:
                lat = "".join(loc.xpath("@data-lat")).strip()
                longit = "".join(loc.xpath("data-lng")).strip()
                location_type = ""
                try:
                    location_type = (
                        "".join(
                            loc.xpath(
                                './/div[@class="location-result__pin-wrapper"]/div[1]/@class'
                            )
                        )
                        .strip()
                        .replace("location-result__pin location-result__pin--", "")
                        .strip()
                    )

                except:
                    pass

                location_name = "".join(loc.xpath(".//h4//text()")).strip()
                if len(location_type) <= 0:
                    if "Walk-in Clinic" in location_name:
                        location_type = "Walk-in Clinic"
                    elif "Urgent Care" in location_name:
                        location_type = "Urgent Care"

                addy = "".join(loc.xpath(".//p[@class='address']/text()")).strip()

                street_address, city, state, zip_code = parse_addy(addy)

                street_address = street_address.split("Ste ")[0]

                phone_number = "".join(loc.xpath(".//a[@class='tel__number']/text()"))

                country_code = "US"
                page_url = "".join(
                    loc.xpath(
                        './/div[@class="location-result__button-wrapper"]/a/@href'
                    )
                ).strip()
                if len(page_url) > 0:
                    page_url = "https://www.saintlukeskc.org" + page_url
                hours = "<MISSING>"
                store_number = "<MISSING>"
                street_address = (
                    street_address.split("Suite")[0]
                    .strip()
                    .split("Unit")[0]
                    .strip()
                    .replace(",", "")
                    .strip()
                )

                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone_number,
                    location_type=location_type,
                    latitude=lat,
                    longitude=longit,
                    hours_of_operation=hours,
                )

            next_page = stores_sel.xpath('//li/a[@rel="next"]/@href')
            if len(next_page) <= 0:
                break
            else:
                search_url = "https://www.saintlukeskc.org/location" + next_page[0]


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_TYPE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
