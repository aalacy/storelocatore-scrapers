from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("spiritofmath")


def _close(driver):
    close_btn = driver.find_element_by_xpath("//div[@id='mapmaskBtn']")
    if close_btn:
        driver.execute_script("arguments[0].click();", close_btn)
    time.sleep(1)


def _street(addr):
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    return street_address


def fetch_data():
    locator_domain = "https://spiritofmath.com/"
    base_url = "https://spiritofmath.com/#locations"
    with SgChrome() as driver:
        driver.set_window_size(930, 660)
        driver.get(base_url)
        _close(driver)
        time.sleep(1)
        filterShowAll = driver.find_element_by_xpath('//a[@id="filterShowAll"]')
        driver.execute_script("arguments[0].click();", filterShowAll)
        time.sleep(2)
        locations = bs(driver.page_source, "lxml").select(
            "div.ssf-column div.store-locator__infobox"
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            if not _.select_one("div.store-website a"):
                continue
            phone = _.select_one("div.store-tel").text.split("x")[0].split("or")[0]
            page_url = _.select_one("div.store-website a")["href"]
            location_name = _.select_one("div.store-location").text
            hours_of_operation = _.select_one("div.store-operating-hours").text
            addr = parse_address_intl(_.select_one("div.store-address").text)
            if not addr.postcode:
                continue
            coord = (
                _.select_one("a.infobox__cta.ssflinks")["href"]
                .split("daddr=")[1][1:-1]
                .split(",")
            )
            yield SgRecord(
                store_number=_["id"].replace("store", ""),
                page_url=page_url,
                location_name=location_name,
                street_address=_street(addr),
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                phone=phone,
                latitude=coord[0],
                longitude=coord[-1],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
