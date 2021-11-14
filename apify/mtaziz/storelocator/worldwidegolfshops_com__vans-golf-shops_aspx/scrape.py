import re
import json
from lxml import etree
from urllib.parse import urljoin
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sglogging import SgLogSetup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
}


USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
start_url = "https://www.worldwidegolfshops.com/vans-golf-shops"
logger = SgLogSetup().get_logger("worldwidegolfshops_com__vans-golf-shops_aspx")


def get_store_urls():
    with SgRequests() as session:
        response = session.get(start_url, headers=headers)
        dom = etree.HTML(response.text)
        data = dom.xpath(
            '//script[contains(text(), "store.custom.find-a-store")]/text()'
        )[2]
        data = json.loads(data)
        all_poi_raw = []
        for k, v in data.items():
            if (
                "find-a-store-vansContainer/flex-layout.col#find-a-store-vans-col/flex-layout.row"
                in k
            ):
                all_poi_raw.append(v)

        all_locations = []
        for poi in all_poi_raw:
            if poi["props"].get("text"):
                try:
                    all_locations.append(
                        poi["props"]["text"].split("](")[1].split(")\n")[0]
                    )
                except Exception:
                    continue
        return all_locations


def get_driver(url, xpath, driver=None):
    if driver is not None:
        driver.quit()
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=USER_AGENT,
                is_headless=True,
            ).driver()
            driver.get(url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(((By.XPATH, xpath)))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def fetch_data():
    all_locations = get_store_urls()
    for idx, url in enumerate(all_locations[0:]):
        domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
        page_url = urljoin(start_url, url)
        logger.info(f"Pulling the data from {page_url}")
        xpath_store_hours = '//div[contains(text(), "STORE HOURS")]'
        if "##" in page_url:
            continue
        driver = get_driver(page_url, xpath_store_hours)
        loc_dom = etree.HTML(driver.page_source)
        poi = loc_dom.xpath('//script[contains(text(), "address")]/text()')[0]
        poi = json.loads(poi)
        location_name = "".join(loc_dom.xpath("//title/text()"))
        logger.info(f"[{idx}] Location Name: {location_name}")
        hoo = []
        try:
            for e in poi["openingHoursSpecification"]:
                if not e.get("dayOfWeek"):
                    continue
                hoo.append(f'{e["dayOfWeek"]} {e["opens"]} {e["closes"]}')
        except Exception as e:
            logger.info(f" [ {e} ] Please fix it at >>> [{idx}] | {page_url}")
        hours_of_operation = " ".join(hoo)
        country_code = ""
        country_code = "US"
        if "store/the-golf-mart-nm-87111/ABQ" in page_url:
            country_code = "MX"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=poi["address"]["streetAddress"],
            city=poi["address"]["addressLocality"],
            state=poi["address"]["addressRegion"],
            zip_postal=poi["address"]["postalCode"],
            country_code=country_code,
            store_number=poi["@id"],
            phone=poi["telephone"],
            location_type=poi["@type"][0],
            latitude=poi["geo"]["latitude"],
            longitude=poi["geo"]["longitude"],
            hours_of_operation=hours_of_operation,
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
