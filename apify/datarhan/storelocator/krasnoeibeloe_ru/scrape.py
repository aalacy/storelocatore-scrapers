import ssl
import random
import time
from lxml import etree

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from sgselenium.sgselenium import SgChrome
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton

website = "krasnoeibeloe.ru"
page_url = "https://krasnoeibeloe.ru/address"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=website)


ssl._create_default_https_context = ssl._create_unverified_context


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=3, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


def get_items(driver, city):
    items = []
    dom = etree.HTML(driver.page_source)
    all_locations = dom.xpath('//div[contains(@class, "shop_list_row")]')

    for location in all_locations:
        raw_data = location.xpath(".//text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        store_number = location.xpath(".//input/@value")[0]
        state = dom.xpath('//select[@name="region"]/option/text()')[0]
        hoo = location.xpath('.//div[@class="shop_l_time"]/div/text()')
        hoo = " ".join([e.strip() for e in hoo])
        street_address = raw_data[0].replace("&quot;", '"')

        raw_address = f"{street_address}, {city}, {state}".replace(MISSING, "")
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

        items.append(
            SgRecord(
                locator_domain=website,
                page_url=page_url,
                country_code="RU",
                location_name=MISSING,
                phone=MISSING,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                zip_postal=MISSING,
                street_address=street_address,
                city=city,
                state=state,
                store_number=store_number,
                hours_of_operation=hoo,
                raw_address=raw_address,
            )
        )
    return items


def fetch_data(driver):
    driver.get(page_url)
    random_sleep(driver)
    try:
        driver.find_element_by_xpath(
            '//a[@class="btn btn_red age_popup_btn age_popup_btn--agree"]'
        ).click()
    except Exception:
        pass
    all_regions = driver.find_elements_by_xpath(
        '//select[@name="region"]/following-sibling::div[1]//div[@class="option"]'
    )
    log.info(f"Total regions = {len(all_regions)}")

    count = 0
    for region in all_regions[0:1]:
        count = count + 1
        log.info(f"{count}. Scrapping region ...")
        all_regions = driver.find_elements_by_xpath(
            '//select[@name="region"]/following-sibling::div[1]//div[@class="option"]'
        )

        driver.find_element_by_xpath('//div[@class="item_select_city"]').click()
        try:
            driver.find_element_by_xpath(
                '//a[@class="btn btn_red age_popup_btn age_popup_btn--agree"]'
            ).click()
        except Exception:
            pass
        driver.find_element_by_xpath('//div[@class="item_select_city"]').click()
        random_sleep(driver)
        all_regions[count - 1].click()
        random_sleep(driver)
        driver.find_element_by_xpath('//div[@class="bl_selects_city"]/div[2]').click()
        random_sleep(driver)

        state_items = get_items(driver, MISSING)
        log.info(f"  total items from state = {len(state_items)}")

        all_cities = driver.find_elements_by_xpath(
            '//select[@name="city"]/following-sibling::div[1]//div[contains(@class,"option")]'
        )
        log.info(
            f"  total items from state = {len(state_items)}; cities = {len(all_cities)}"
        )

        city_count = 0
        city_store_count = 0
        for city in all_cities:
            city_count = city_count + 1
            all_cities = driver.find_elements_by_xpath(
                '//select[@name="city"]/following-sibling::div[1]//div[contains(@class,"option")]'
            )

            city_name = all_cities[city_count - 1].text.strip()
            if len(city_name) == 0:
                continue

            all_cities[city_count - 1].click()
            log.info(f"    {city_count}. Scrapping city {city_name}...")
            random_sleep(driver)
            city_items = get_items(driver, city_name)
            log.info(f"        city items = {len(city_items)}")
            city_store_count = city_store_count + len(city_items)
            for item in city_items:
                yield item

            driver.find_element_by_xpath(
                '//div[@class="bl_selects_city"]/div[2]'
            ).click()
            random_sleep(driver)

        log.info(
            f"{count}. total city stores = {city_store_count}; from state={len(state_items)}"
        )
        for item in state_items:
            yield item
        log.info("---------------")


def scrape():
    log.info(f"Start scrapping {website} ...")
    CrawlStateSingleton.get_instance().save(override=True)
    start = time.time()
    with SgChrome(executable_path=ChromeDriverManager().install()) as driver:
        with SgWriter(
            deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
        ) as writer:
            for rec in fetch_data(driver):
                writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
