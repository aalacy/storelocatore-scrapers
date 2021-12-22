from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By
import time
import ssl
import json
from sglogging import SgLogSetup
import tenacity


ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("toyota.com.vn")
user_agent = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0"
)


@tenacity.retry(wait=tenacity.wait_fixed(5))
def get_with_retry(url):
    with SgChrome(user_agent=user_agent) as driver:
        driver.get(url)
        time.sleep(70)
        return json.loads(driver.find_element(By.CSS_SELECTOR, "body").text)


def fetch_data():

    start_url = "https://www.toyota.com.vn/api/common/provinces"
    domain = "toyota.com.vn"
    logger.info(f"Started Crawling: {start_url}")
    jsn = get_with_retry(start_url)

    for p in jsn["Data_Ext"]["result"]["items"]:
        url = f'https://www.toyota.com.vn/api/common/dealerbyprovinceidanddistrictid?provinceId={p["code"]}&districtId='
        logger.info(f"Crawling: {url}")
        data = get_with_retry(url)

        for poi in data["Data_Ext"]["result"]:
            raw_address = poi["address"]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            geo = ["", ""]
            if poi["mapUrl"]:
                geo = (
                    etree.HTML(poi["mapUrl"].replace('""', '"'))
                    .xpath("//@src")[0]
                    .split("!2d")[-1]
                    .split("!2m")[0]
                    .split("!3d")
                )

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.toyota.com.vn/danh-sach-dai-ly",
                location_name=poi["name"],
                street_address=street_address,
                city=addr.city,
                state=poi["province"],
                zip_postal=addr.postcode,
                country_code="VN",
                store_number=poi["code"],
                phone=poi["phone"],
                location_type="",
                latitude=geo[0],
                longitude=geo[1],
                hours_of_operation=poi["operatingTime"],
            )

            yield item


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
