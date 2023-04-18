from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time
from webdriver_manager.chrome import ChromeDriverManager
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("")

locator_domain = "https://www.iconcinemas.com"
base_url = "https://www.iconcinemas.com/"
info_url = "https://www.iconcinemas.com/theatreinfo.php"


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


def _d(driver, loc):
    logger.info(loc.find_element_by_css_selector("span").text)
    coming_soon = bs(driver.page_source, "lxml").select_one("div#cs")
    if coming_soon and "coming soon" in coming_soon.text.lower():
        return None
    button = loc.find_element_by_css_selector('div[role="button"]')
    driver.execute_script("arguments[0].click();", button)
    time.sleep(1)
    info_btn = driver.find_element_by_xpath("//a[contains(text(),'THEATRE INFO')]")
    driver.execute_script("arguments[0].click();", info_btn)
    rr = driver.wait_for_request(info_url)
    sp1 = bs(rr.response.body, "lxml")
    info = list(sp1.select_one("div#general table > tr > td").stripped_strings)
    addr = info[1].split(",")
    try:
        coord = (
            sp1.select_one("div#drawMap")["onclick"]
            .split("query=")[1]
            .split("');")[0]
            .split(",")
        )
    except:
        return None
    if coord[0] == "" and coord[1] == "":
        return None
    return SgRecord(
        page_url=base_url,
        location_name=info[0],
        street_address=" ".join(addr[:-2]),
        city=addr[-2].split(",")[0].strip(),
        state=addr[-1].strip().split()[0].strip(),
        zip_postal=addr[-1].strip().split()[-1].strip(),
        country_code="US",
        latitude=coord[0],
        longitude=coord[1],
        locator_domain=locator_domain,
        raw_address=", ".join(addr),
    )


def fetch_data():
    driver = get_driver()
    driver.get(base_url)
    locations = driver.find_elements_by_xpath('//div[@class="locationItem"]')
    total = len(locations)
    for x in range(total):
        del driver.requests
        driver.get(base_url)
        header = driver.find_element_by_css_selector("div.headerLocationName")
        driver.execute_script("arguments[0].click();", header)
        time.sleep(1)
        locations = driver.find_elements_by_xpath('//div[@class="locationItem"]')
        loc = locations[x]
        yield _d(driver, loc)

    if driver:
        driver.close()


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
