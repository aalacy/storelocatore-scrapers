from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import time


def _close(driver):
    close_btn = driver.find_element_by_xpath("//div[@id='mapmaskBtn']")
    if close_btn:
        driver.execute_script("arguments[0].click();", close_btn)
    time.sleep(1)


def fetch_data():
    locator_domain = "https://spiritofmath.com/"
    base_url = "https://spiritofmath.com/#locations"
    with SgChrome() as driver:
        driver.set_window_size(930, 660)
        driver.get(base_url)
        _close(driver)
        toggle_btn = driver.find_element_by_xpath(
            "//td[@id='storeLocatorFilterToggler']"
        )
        driver.execute_script("arguments[0].click();", toggle_btn)
        ca_selector = driver.find_element_by_xpath(
            "//input[@id='storesCountry' and @value='CA']"
        )
        driver.execute_script("arguments[0].click();", ca_selector)
        approval_btn = driver.find_element_by_xpath('//a[@id="applyFilterOptions"]')
        driver.execute_script("arguments[0].click();", approval_btn)
        apply_btn = driver.find_element_by_xpath('//a[@id="applyFilterOptionss"]')
        if apply_btn:
            driver.execute_script("arguments[0].click();", apply_btn)
        el = driver.find_element_by_xpath(
            '//div[contains(@class, "ssf-column")]/div[@class="store-locator__infobox"]'
        )
        driver.execute_script("arguments[0].click();", el)
        time.sleep(1)
        locations = bs(driver.page_source, "lxml").select(
            "div.ssf-column div.store-locator__infobox"
        )
        for _ in locations[:-1]:
            phone = _.select_one("div.store-tel").text
            page_url = _.select_one("div.store-website a")["href"]
            location_name = _.select_one("div.store-location").text
            hours_of_operation = _.select_one("div.store-operating-hours").text
            addr = parse_address_intl(_.select_one("div.store-address").text)
            coord = (
                _.select_one("a.infobox__cta.ssflinks")["href"]
                .split("daddr=")[1][1:-1]
                .split(",")
            )
            yield SgRecord(
                store_number=_["id"].replace("store", ""),
                page_url=page_url,
                location_name=location_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
