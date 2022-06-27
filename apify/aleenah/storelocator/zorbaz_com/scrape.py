import ssl
import time
from sglogging import sglog
import undetected_chromedriver as uc
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.chrome import ChromeDriverManager


ssl._create_default_https_context = ssl._create_unverified_context

website = "zorbaz_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://www.zorbaz.com"
MISSING = SgRecord.MISSING


def get_driver(url, driver=None):
    driver = uc.Chrome(executable_path=ChromeDriverManager().install())
    driver.get(url)
    return driver


def fetch_data():
    url = "https://www.zorbaz.com/locationz"
    driver = get_driver(url)
    time.sleep(2)
    loclist = (
        driver.page_source.split("window.POPMENU_APOLLO_STATE = ")[1]
        .split("[]}};")[0]
        .split("RestaurantLocation:")[1:]
    )

    for loc in loclist:
        try:
            phone = loc.split('"displayPhone":"')[1].split('"')[0]
        except:
            continue
        location_name = loc.split('"name":"')[1].split('"')[0]
        page_url = loc.split('">Vizit Uz/Eventz')[0].split('href=\\"')[-1]
        store_number = loc.split('"id":')[1].split(",")[0]
        log.info(page_url)
        street_address = loc.split('"streetAddress":"')[1].split('"')[0]
        city = loc.split('"city":"')[1].split('"')[0]
        state = loc.split('"state":"')[1].split('"')[0]
        zip_postal = loc.split('"postalCode":"')[1].split('"')[0]
        country_code = loc.split('"country":"')[1].split('"')[0]
        latitude = loc.split('"lat":')[1].split('"')[0]
        longitude = loc.split('"lng":')[1].split('"')[0]
        hours_of_operation = (
            loc.split('"schemaHours":[')[1]
            .split("]")[0]
            .replace('","', " ")
            .replace('"', "")
        )
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
            phone=phone,
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
