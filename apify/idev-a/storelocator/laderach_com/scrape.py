from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgselenium import SgChrome
from sgscrape.sgpostal import parse_address_intl
import re
import time
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("laderach")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://laderach.com/"
base_url = "https://us.laderach.com/our-locations/"


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def _detail(_id, driver):
    driver.switch_to.default_content()
    time.sleep(1)
    driver.switch_to.frame(driver.find_element_by_xpath(f'//div[@id="{_id}"]//iframe'))
    sp1 = bs(driver.page_source, "lxml")
    _addr = sp1.select_one("a.sk-google-business-profile-address-link").text.strip()
    addr = parse_address_intl(_addr)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    if street_address.isdigit() and len(_addr.split(",")) > 1:
        street_address = _addr.split(",")[0]
    country_code = addr.country
    if not country_code and "Singapore" in _addr:
        country_code = "Singapore"
    hours = []
    _hr = sp1.find("label", string=re.compile(r"Business Hours"))
    if _hr:
        _temp = sp1.select("table.sk-ww-google-business-profile-content-container")
        if _temp:
            temp = _temp[-1].select("tr")
            if temp and "Business Hours" in temp[0]:
                del temp[0]
            if temp:
                hours = [":".join(hh.stripped_strings) for hh in temp]
    _phone = list(
        sp1.select("table.sk-ww-google-business-profile-main-info tr")[
            -1
        ].stripped_strings
    )
    phone = ""
    if _phone and _p(_phone[-1]):
        phone = _phone[-1]
    _url = sp1.select_one("td.sk-google-profile-website a")
    page_url = ""
    if _url:
        page_url = _url.text.strip()
    return SgRecord(
        page_url=page_url,
        location_name=sp1.select_one(".name").text.strip(),
        store_number=_id.split("-")[-1],
        street_address=street_address,
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        country_code=country_code,
        phone=phone,
        locator_domain=locator_domain,
        latitude=sp1.select_one(".place_lat").text.strip(),
        longitude=sp1.select_one(".place_lng").text.strip(),
        hours_of_operation="; ".join(hours),
    )


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        stores = soup.select("div.store-row-container div.store-row")
        logger.info(f"{len(stores)} found")
        missing = []
        for store in stores:
            _id = store["id"]
            logger.info(_id)
            try:
                yield _detail(_id, driver)
            except Exception as err:
                logger.warning(str(err))
                logger.info(f"missing {_id}")
                missing.append(_id)

        logger.info(f"{len(missing)} missing")
        if missing:
            time.sleep(2)
        for _id in missing:
            try:
                yield _detail(_id, driver)
            except Exception as err:
                logger.warning(str(err))
                logger.info(f"missing {_id}")


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
