from lxml import etree
from functools import reduce
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By
import time
import ssl
import json
from sglogging import SgLogSetup
import tenacity

import os

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-vn:{}@proxy.apify.com:8000/"

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("toyota.com.vn")
user_agent = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0"
)


@tenacity.retry(wait=tenacity.wait_fixed(5))
def get_with_retry(url):
    with SgChrome(user_agent=user_agent) as driver:
        driver.get(url)
        time.sleep(16)
        return json.loads(driver.find_element(By.CSS_SELECTOR, "body").text)


def remove_characters(value):

    pattern = ";"

    split_string = [
        r.split("Email")[0].split("Mail")[0].split("Hotline")[0].strip(" ").strip("-")
        for r in value.split("\\r\\n")
    ]
    join_string = pattern.join(split_string)
    res = reduce((lambda x, y: x + pattern + y if y else x), join_string.split(pattern))

    return (
        res.strip(pattern).replace(":;", ": ").replace(".;", "; ")
        if res
        else "<MISSING>"
    )


def fetch_data():

    start_url = "https://www.toyota.com.vn/api/common/provinces"
    domain = "toyota.com.vn"
    logger.info(f"Started Crawling: {start_url}")
    jsn = get_with_retry(start_url)

    for p in jsn["Data_Ext"]["result"]["items"]:
        url = f'https://www.toyota.com.vn/api/common/dealerbyprovinceidanddistrictid?provinceId={p["id"]}&districtId='
        logger.info(f"Crawling: {url}")
        data = get_with_retry(url)

        for poi in data["Data_Ext"]["result"]:
            hours_of_operation = (
                remove_characters(poi["operatingTime"])
                if poi["operatingTime"]
                else "<MISSING>"
            )
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
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            yield item


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
